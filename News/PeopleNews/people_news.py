from bs4 import BeautifulSoup
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def data_payloads(url,page):
    payloads = {'page': page,
                'status': '1'}
    return payloads

def people_news(session, url, cate, cate1, end_date):
    article = []
    page = 1
    while True:
        base_url = url + cate1
        res = session.post(base_url, data=data_payloads(url,page), timeout=20)
        try:
            parse_json = res.json()
            date_time = ''
            for item in parse_json['data_list']:
                title = extract_title(item)
                date_time = extract_date(item)
                author = extract_author(item)
                link = extract_link(item)
                content = extract_content(item)

                if date_time < end_date:
                    break
                else:
                    #collect every news data in article list
                    article.append({'date_time':date_time,'author':author,
                                    'title':title,'link':link,'label':cate1,
                                    'content':content,'keyword':''})
            #while datetime < enddate break
            if date_time < end_date:
                break
            else:
                page += 1
        except Exception:
            print('can not parse json')
            break

    if len(article)!=0:
        write_to_json(article,cate)

def extract_title(item):
    #title
    try:
        title = item['TITLE']
    except Exception:
        title = ''
    return title

def extract_date(item):
    #datetime
    try:
        date_time = item['PUBTIME']
    except Exception:
        date_time = ''
    return date_time

def extract_author(item):
    #author
    try:
        author = item['AUTHOR']
    except Exception:
        author = ''
    return author

def extract_link(item):
    #link
    try:
        link = 'https://www.peoplenews.tw/news/' + item['EID']
    except Exception:
        link = ''
    return link

def extract_content(item):
    #content
    try:
        content = BeautifulSoup(item['CONTENT'],'lxml').text.replace('\n','')
    except Exception:
        content = ''
    return content

def write_to_json(article,cate):
    file_path = write_json_records(
        records=article,
        source_name='PeopleNews',
        category=cate,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='people',
    )
    print(f"saved: {file_path}")
    
if __name__ == '__main__':
    session = create_session(headers={'x-requested-with': 'XMLHttpRequest'})
    end_date = build_end_date(days_back=1)
                                         
    cates = [('politics','政治'),
             ('society','社會'),
             ('global','全球'),
             ('life','生活'),
             ('finance','財經')]

    url = 'https://www.peoplenews.tw/resource/lists/NEWS/'
    for cate,cate1 in cates:
        people_news(session, url, cate, cate1, end_date)
