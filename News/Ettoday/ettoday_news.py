from bs4 import BeautifulSoup
import time
import datetime
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import create_session, get_soup, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def parse_cateurl(session, url, start_date, end_date, cate, cate1, cate2):
    newslink = set()
    while str(start_date) > end_date:
        baseurl = url + str(start_date) + '-' + cate1 +'.htm'
        soup = get_soup(session, baseurl, sleep_seconds=0.2)
        parts = soup.find_all('div','part_list_2')
        if not parts:
            break

        items = parts[0].find_all('h3')
        date_f = ''
        for item in items:
            link = 'https://www.ettoday.net' + item.find('a')['href']
            print(link)
            date_f = link.split('/news/')[-1].split('/')[0]
            date_f = datetime.datetime.strptime(date_f,'%Y%m%d').strftime('%Y-%m-%d')
            if date_f < end_date:
                break
            else:
                newslink.add(link)
        if date_f < end_date:
            break
            
        start_date -= delta
    parse_info(session, sorted(newslink,reverse=False), cate, cate2)

def parse_info(session, urls, cate, cate2):
    data_collect = []
    for link in urls:
        try:
            soup = get_soup(session, link, sleep_seconds=0.2)
        except Exception:
            continue

        title = extract_title(soup)
        date_time = extract_date(soup)
        content = extract_content(soup)
        keyword = extract_keyword(soup)

        article  = {'date_time':date_time,'title':title,
                    'link':link,'label':cate,
                    'content':content,'keyword':keyword}
        print(article)
        data_collect.append(article)

    if len(data_collect)!=0:
        outputjson(data_collect,cate2)

def extract_title(soup):
    try:
        title = soup.find('h1','title').text
    except Exception:
        title = ''
    return title
            
def extract_date(soup):
    try:
        date_time = soup.find('time').text.strip()
    except Exception:
        date_time = ''
    return date_time
        
def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div','story')[0].find_all('p')
        for c in contents:
            content += c.text.replace('\n','').replace('\r','')
    except Exception:
        pass
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','part_tag_1 clearfix')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except Exception:
        keyword = ''
    
    if keyword == '':
        try:
            keywords = soup.find_all('div','tag')[0].find_all('a')
            for k in keywords:
                keyword += k.text + ' '
        except Exception:
            keyword = ''

    if keyword == '':
        try:
            keywords = soup.find_all('p','tag')[0].find_all('a')
            for k in keywords:
                keyword += k.text + ' '
        except Exception:
            keyword = ''

    return keyword

def outputjson(data_collect,cate2):
    file_path = write_json_records(
        records=data_collect,
        source_name='Ettoday',
        category=cate2,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='ettoday',
    )
    print(f"saved: {file_path}")
        
if __name__ == '__main__':
    start_date = datetime.datetime.strptime(time.strftime('%Y-%m-%d'),'%Y-%m-%d')
    one_day = datetime.timedelta(days=1)
    global delta
    delta = datetime.timedelta(days=1)
    end_date = (start_date - one_day).strftime('%Y-%m-%d')
    print(end_date) 
    session = create_session()

    cates = [('政治','1','politics'),('社會','6','society'),('國際','2','global'),
             ('生活','5','life'),('財經','17','finance'),('健康','21','health'),('3C家電','20','3C')]

    url = 'https://www.ettoday.net/news/news-list-'
    for cate,cate1,cate2 in cates:
        parse_cateurl(session, url, start_date, end_date, cate, cate1, cate2)
