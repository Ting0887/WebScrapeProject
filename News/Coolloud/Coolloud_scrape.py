import os
import datetime
import time
import sys
from bs4 import BeautifulSoup
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")


HEADERS = {"referer": "https://www.coolloud.org.tw/story",
           "Connection": "keep-alive",
           "upgrade-insecure-requests": "1",
           "cache-control": "max-age=0",
           "if-modified-since": "",
            "if-none-match": "W/61501943-8991",
           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"}

    def scrape_link(session, end_date):
    newsdata = []
    page = 0
    while True:
        if page == 0:
            url = 'https://www.coolloud.org.tw/story'
        elif page!=1:
            url = 'https://www.coolloud.org.tw/story?page=' + str(page)
        print(url)
        time.sleep(1)
        res = session.get(url, headers=HEADERS, allow_redirects=False, timeout=20)
        res.encoding = 'utf8'
        soup = BeautifulSoup(res.text,'lxml')
        views = soup.find_all('div','view-content')
        if len(views) < 2:
            break
        bar = views[1].find_all('div','views-row')
        if not bar:
            break

        last_date_time = ''
        for item in bar:
            title = extract_title(item)
            link = extract_link(item)
            author = extract_author(item)
            date_time = extract_date(item)
            last_date_time = date_time
            if date_time < end_date:
                break
            else:
                newsdata.append((title,link,author,date_time))
            print(link)
        if last_date_time and last_date_time < end_date:
            break
        else:
            page += 1
    if len(newsdata)!=0:
        scrape_content(session, newsdata)

def extract_title(item):
    try:
        title = item.find('span','field-content pc-style').text.replace('\n','')
    except Exception:
        title = ''
    return title

def extract_link(item):
    try:
        link = 'https://www.coolloud.org.tw' + item.find('a')['href']
    except Exception:
        link = ''
    return link

def extract_author(item):
    try:
        author = item.find('div','views-field-field-author').text
    except Exception:
        author = ''
    return author

def extract_date(item):
    try:
        date_time = item.find('span','date-display-single').text
    except Exception:
        date_time = 'no date'
    return date_time  

def scrape_content(session, newsdata):
    article = []
    for item in newsdata:
        title = item[0]
        link = item[1]
        author = item[2]
        date_time = item[3]
        try:
            res = session.get(link, headers=HEADERS, timeout=5, allow_redirects=False)
            res.encoding = 'utf8'
            soup = BeautifulSoup(res.text,'lxml')
            content = ''
            try:
                contents = soup.find_all('div','nodeinner')
                for c in contents:
                    content += c.text.replace('\n','') .replace('\r','') .replace('\t','')
            except Exception:
                print('no content')
            keyword = ''
            try:
                keywords = soup.find_all('div','field-name-field-tag')[0].find_all('a')
                for k in keywords:
                    keyword += k.text + ' '
            except Exception:
                print('no keyword')
            article.append({'title':title,
                            'author':author,
                            'date_time':date_time,
                            'label':'苦勞報導',
                            'link':link,
                            'content':content,
                            'keyword':keyword})
            print(article)
        except Exception:
            continue
    if article:
        write_to_json(article)

def write_to_json(article):
    file_path = write_json_records(
        records=article,
        source_name='Coolloud',
        category='report',
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='coolloud',
    )
    print(f"saved: {file_path}")

if __name__ == '__main__':
    end_date = build_end_date(days_back=1).replace('-', '/')
    print(end_date)
    session = create_session()
    scrape_link(session, end_date)
