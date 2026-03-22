from bs4 import BeautifulSoup
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import create_session, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def build_upmedia_end_date(days_back=1):
    import datetime

    target_date = datetime.datetime.today() - datetime.timedelta(days=days_back)
    return target_date.strftime('%Y年%m月%d日 %H:%M')


def parse_cateurl(session, end_date, url, cate, cate1):
    num = 1
    collect_url = []
    while True:
        base_url = url + 'currentPage=' + str(num) + '&Type=' + cate1
        res = session.get(base_url, timeout=20)
        print(base_url)
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.find_all('div','top-dl')
        date_time = ''
        
        for item in items:
            date_time = extract_date(item)
            print(date_time)
            link = extract_newslink(item)
            if date_time < end_date:
                break
            else:
                collect_url.append((date_time,link))
        if date_time < end_date:
            break
        else:
            num += 1

    if len(collect_url)!=0:
        extract_newsinfo(session, collect_url, cate)

def extract_date(item):
    try:
        date_time = item.find('div','time').text.strip()
    except Exception:
        date_time = ''
    return date_time

def extract_newslink(item):
    try:
        link = 'https://www.upmedia.mg/' + item.find('a')['href']
    except Exception:
        link = ''
    return link

def extract_newsinfo(session, collect_url, cate):
    article = []
    for item in collect_url:
        date_time = item[0]
        link = item[1]
        try:
            res = session.get(link, timeout=20)
            soup = BeautifulSoup(res.text,'lxml')

            title = extract_title(soup)
            author = extract_author(soup)
            label = extract_label(soup)
            content = extract_content(soup)
            keyword = extract_keyword(soup)

            article.append({'date_time':date_time,'title':title,'author':author,
                            'label':label,'link':link,'content':content,'keyword':keyword})
        except Exception as e:
            print(e)

    if len(article)!=0:
        write_to_json(article,cate)

def extract_title(soup):
    try:
        title = soup.find('h2',{'id':'ArticleTitle'}).text
    except Exception:
        title = ''
    return title

def extract_author(soup):
    try:
        author = soup.find('div','author').a.text
    except Exception:
        author = ''
    return author

def extract_label(soup):
    label = ''
    try:
        labels = soup.find_all('div','tag')[0].find_all('a')
        for l in labels:
            label += l.text + ' '
    except Exception:
        pass
    return label

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div','editor')[0].find_all('p')
        for c in contents:
            content += c.text
    except Exception:
        pass
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','label')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except Exception:
        pass
    return keyword
                            
def write_to_json(article,cate):
    file_path = write_json_records(
        records=article,
        source_name='upmedia',
        category=cate,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='upmedia',
    )
    print(f"saved: {file_path}")
        
if __name__ == '__main__':
    session = create_session(headers={'referer': 'https://www.upmedia.mg/news_list.php?'})
    end_date = build_upmedia_end_date(days_back=1)
    print(end_date)

    cates = [('global','3'),('focus','24'),('life','5')]
    
    for cate,cate1 in cates:
        url = 'https://www.upmedia.mg/news_list.php?'
        parse_cateurl(session, end_date, url, cate, cate1)
