import os
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def determine_datetime(session, url, cate, cate1, end_date):
    link_collect = []
    num = 1
    while True:
        base_url = url + cate + '/page/' + str(num)
        print(base_url)
        res = session.get(base_url, timeout=20)
        soup = BeautifulSoup(res.text,'lxml')
        listings = soup.find_all('div','listing listing-grid listing-grid-1 clearfix columns-2')
        if not listings:
            break
        items = listings[0].find_all('div','item-inner')
        date_time = ''
        for item in items:
            date_time = item.find('time').text
            link = item.find('h2').a.get('href')
            
            if date_time < end_date:
                break
            else:
                link_collect.append(link)

        if date_time < end_date:
            break
        else:
            num += 1
    if len(link_collect)!=0:
        extract_info(session, link_collect, cate1)

    def extract_info(session, link_collect, cate1):
    article = []
    for link in link_collect:
        print(link)
        res = session.get(link, timeout=20)
        soup = BeautifulSoup(res.text,'lxml')

        title = extract_title(soup)
        date_time = extract_date(soup)
        label = extract_label(soup)
        content = extract_content(soup)
        keyword = extract_keyword(soup)

        article.append({'title':title,'author':'芋傳媒',
                        'date_time':date_time,'link':link,
                        'content':content,'keyword':keyword[:-1],
                        'label':label[:-1],'website':'芋傳媒'})

    if len(article)!=0:
        write_to_json(article,cate1)

def extract_title(soup):
    try:
        title = soup.find('span','post-title').text
    except Exception:
        title = ''
    return title

def extract_date(soup):
    try:
        date_time = soup.find('time').b.text
    except Exception:
        date_time = ''
    return date_time

def extract_label(soup):
    label = ''
    try:
        labels = soup.find_all('div','term-badges floated')[0].find_all('a')
        for l in labels:
            label += l.text + '、'
    except Exception:
        print('no label')
    return label 

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('p')
        for c in contents:
            content += c.text.replace('\n','')
    except Exception:
        pass
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','post-tags')[0].find_all('a')
        for k in keywords:
            keyword += k.text + '、'
    except Exception:
        print('no keyword')
    return keyword
        
def write_to_json(article,cate1):
    file_path = write_json_records(
        records=article,
        source_name='taronews',
        category=cate1,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='taro',
    )
    print(f"saved: {file_path}")

if __name__ == '__main__':
    session = create_session()
    end_date = build_end_date(days_back=1)
    print(end_date)
    url = 'https://taronews.tw/category/'
    
    category = [('politics','politics'),('world','global'),
                ('lifestyle','life'),('finance','finance'),('lifestyle/health','health')]

    for cate,cate1 in category:
        determine_datetime(session, url, cate, cate1, end_date)

