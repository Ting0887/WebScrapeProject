from bs4 import BeautifulSoup
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def EpochTime(session, url, cate, cate1, cate2, end_date):
    article = []
    num = 1
    while True:
        base_url = url + cate1 + '_' + str(num) + '.htm'
        res = session.get(base_url, timeout=20)
        print(base_url)
        soup = BeautifulSoup(res.text,'lxml')
        posts_list = soup.find_all('div','posts-list')
        if not posts_list:
            break

        items = posts_list[0].find_all('li')
        last_date_time = ''
        for item in items:
            link = extract_link(item)
            print(link)
            label = extract_label(item)

            resp = session.get(link, timeout=20)
            soup = BeautifulSoup(resp.text,'lxml')
            title = extract_title(soup)
            date_time = extract_date(soup)
            last_date_time = date_time
            content = extract_content(soup)
            keyword = extract_keyword(soup)
            if date_time < end_date:
                break
            else:
                article.append({'date_time':date_time,'title':title,
                                'label':label,'link':link,
                                'content':content,'keyword':keyword})
        if last_date_time and last_date_time < end_date:
            break
        else:
            num += 1
    # if no data,pass
    if len(article)!=0:
        outputjson(article,cate2)

def extract_link(item):
    try:
        link = item.find('a')['href']
    except:
        link = ''
    return link

def extract_label(item):
    try:
        label = item.find('span','sub-cat').text.strip()
    except:
        label = ''
    
    return label

def extract_title(soup):
    try:
        title = soup.find('h1').text
    except:
        title = ''
    return title

def extract_date(soup):
    try:
        date_time = soup.find('time')['datetime'][0:10]
    except:
        date_time = ''
    return date_time 

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div',{'itemprop':'articleBody'})[0].find_all('p')
        for c in contents:
            content += c.text
    except Exception:
        pass
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','mbottom10 large-12 medium-12 small-12 columns')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except:
        pass
    return keyword

def outputjson(article,cate2):
    file_path = write_json_records(
        records=article,
        source_name='EpochTimes',
        category=cate2,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='epoch',
    )
    print(f"saved: {file_path}")
        
if __name__ == '__main__':
    end_date = build_end_date(days_back=1)
    print(end_date)
    url = 'https://www.epochtimes.com/b5/'
    session = create_session()

    cates=  [('台灣社會','ncid1077890','society'),
             ('台灣政治','ncid1077884','politics'),
             ('台灣生活','ncid1077891','life'),
             ('台灣經濟','ncid1077887','finance'),
             ('科技動向','ncid1185664','tech')
            ]
    for cate,cate1,cate2 in cates:
        EpochTime(session, url, cate, cate1, cate2, end_date)
