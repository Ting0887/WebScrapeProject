from bs4 import BeautifulSoup
import os
import sys
from pathlib import Path

import requests

requests.packages.urllib3.disable_warnings()

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def eranews(session, url, cate1, cate2, end_date):
    newslink = []
    page = 19
    for num in range(0,page+1):
        cate_url = url + f'/?pp={num}0'
        res = session.get(cate_url, verify=False, timeout=20)
        res.encoding = 'utf8'
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.find_all('p','tib-title')
        if not items:
            break

        date_f = ''
        for item in items:
            link = item.find('a')['href']
            date_f = link.split('/')[-2]
            if date_f < end_date:
                break
            else:
                print(link)
                newslink.append(link)
        if date_f < end_date:
                break

    if len(newslink)!=0:
        parse_article(session, newslink, cate1, cate2)

def parse_article(session, newslink, cate1, cate2):
    eradata = []
    for link in newslink:
        res = session.get(link, verify=False, timeout=20)
        res.encoding = 'utf8'
        if res.status_code == requests.codes.ok:
            soup = BeautifulSoup(res.text,'lxml')
            items = soup.select('.cell_416_')
            for item in items:
                try:
                    title = item.find('h1').text
                    print(title)
                except Exception:
                    title = ''
                try:
                    date_time = item.find('span','time').text
                except Exception:
                    date_time = ''
                label = cate1
                try:
                    content = item.find('div','article-main').text
                except Exception:
                    content = ''
                
                keyword = ''

                eradata.append({'date_time':date_time,
                                'title':title,
                                'link':link,
                                'label':label,
                                'content':content,      
                                'keyword':keyword})
    if len(eradata)!=0:
        outputjson(eradata, cate2)

def outputjson(eradata, cate2):
    file_path = write_json_records(
        records=eradata,
        source_name='era_news',
        category=cate2,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='era',
    )
    print(f"saved: {file_path}")
    
if __name__ == '__main__':
    end_date = build_end_date(days_back=1)
    session = create_session()

    #categories
    cates = {('political','政治','politic'),
              ('Society','社會','society'),
              ('WorldNews','國際','global'),
              ('Life','生活','life'),
              ('Finance','財經','finance')}
    
    for cate,cate1,cate2 in cates:
        url = f'http://www.eracom.com.tw/EraNews/Home/{cate}/'   
        eranews(session, url, cate1, cate2, end_date)


