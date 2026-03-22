import requests
from bs4 import BeautifulSoup
import datetime
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import create_session, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def build_ctee_end_date(days_back=1):
    target_date = datetime.datetime.today() - datetime.timedelta(days=days_back)
    return target_date.strftime('%Y.%m.%d')


def Scrape_link(session, url, cate, cate1, end_date):
    news_link = []
    num = 1
    while True:
        base_url = url + cate1 + '/page/' + str(num)
        res = session.get(base_url, timeout=20)
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.find_all('div','item-inner clearfix')
        if not items:
            break

        last_date_time = ''
        for item in items:
            link = item.find('a')['href']
            date_time = item.find('time','post-published updated').text
            last_date_time = date_time
            if date_time < end_date:
                break
            else:
                news_link.append(link)
            
        if last_date_time and last_date_time < end_date:
            break
        else:
            num += 1

    if len(news_link)!=0:
        Scrape_article(session, cate, cate1, news_link)

def Scrape_article(session, cate, cate1, news_link):
    article = []
    for link in news_link:
        print(link)
        res = session.get(link, timeout=20)
        soup = BeautifulSoup(res.text,'lxml')
        date_time = extract_date(soup)
        author = extract_author(soup)
        title = extract_title(soup)
        content = extract_content(soup)
        keyword = extract_keyword(soup)
        if content == '':
            continue
        article.append({'date_time':date_time,'author':author,'title':title,
                        'label':cate,'link':link,'content':content,'keyword':keyword})
    if len(article)!=0:
        outputjson(cate1, article)

def extract_date(soup):
    try:
        date_time = soup.find('time','post-published updated').text
    except Exception:
        date_time = ''
    return date_time  

def extract_author(soup):
    try:
        author = soup.find('a','author url fn').text
    except Exception:
        author = ''
    return author

def extract_title(soup):
    try:
        title = soup.find('span','post-title').text
    except Exception:
        title = ''
    return title

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div','entry-content clearfix single-post-content')[0].find_all('p')
        for c in contents:
            content += c.text
    except Exception:
        pass
    return content
        
def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','entry-terms post-tags clearfix style-24')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except Exception:
        pass
    return keyword
        
def outputjson(cate1, article):
    file_path = write_json_records(
        records=article,
        source_name='Ctee',
        category=cate1,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='ctee',
    )
    print(f"saved: {file_path}")
    
if __name__ == '__main__':
    end_date = build_ctee_end_date(days_back=1)
    session = create_session()
    
    cates = [('國際','global'),('要聞','policy'),('財經','finance'),('3c消費','3C')]

    for cate,cate1 in cates:
        if cate == '3c消費':
            url = 'https://ctee.com.tw/tag/'
        else:
            url =  'https://ctee.com.tw/category/news/'
        Scrape_link(session, url, cate, cate1, end_date)
