import os
import time
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def scrape_link(session, label, url, foldername, end_date):
    newsdata = []
    page = 1
    while True:
        page_url = url + '/page/' + str(page)
        res = session.get(page_url, timeout=20)
        soup = BeautifulSoup(res.text,'lxml')
        rows = soup.find_all('div','tipi-row content-bg clearfix')
        if not rows:
            break

        bar = rows[0].find_all('div','preview-mini-wrap clearfix')
        date_time = ''
        for item in bar:
            try:
                title = item.find('h3','title').text
            except Exception:
                title = ''
            try:
                link = item.find('h3','title').a.get('href')
            except Exception:
                link = ''
            try:
                date_time = item.find('time')['datetime'][:10]
            except Exception:
                date_time = ''

            if link != '' and date_time >= end_date:
                newsdata.append((title,link,date_time))
            print(link)
        if date_time < end_date:
            break
        else:
            page += 1
        
        # if end page ,break
        mes = soup.find('h1').text
        if '不好意思呢，找不到這個頁面' in mes:
            break
    if len(newsdata)!=0:
        scrape_content(session, label, newsdata, foldername)

def scrape_content(session, label, newsdata, foldername):
    article = []
    for item in newsdata:
        title = item[0]
        link = item[1]
        date_time = item[2]

        res = session.get(link, timeout=20)
        soup = BeautifulSoup(res.text,'lxml')
        try:
            author = soup.find('span','byline-part author').text
        except Exception:
            author = ''

        content = ''
        try:
            content = soup.find('div','entry-content').text.replace('\n','')
            content = content.split('延伸閱讀')[0]
        except Exception:
            print('no content!')
        
        keyword = ''
        try:
            keywords = soup.find_all('div','post-tags')[0].find_all('a')
            for k in keywords:
                keyword += k.text.replace('\n','').strip() + ' '
        except Exception:
            print('no keyword')

        article.append({'title':title,
                        'author':author,
                        'date_time':date_time,
                        'label':label,
                        'link':link,
                        'content':content,
                        'keyword':keyword})
        print(article)

    if len(article)!=0:
        write_to_json(article,foldername)

def write_to_json(article,foldername):
    file_path = write_json_records(
        records=article,
        source_name='Newsmarket',
        category=foldername,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='newsmarket',
    )
    print(f"saved: {file_path}")

if __name__ == '__main__':
    session = create_session()
    end_date = build_end_date(days_back=1)
    print(end_date)

    categories = [
                ('時事-政策','https://www.newsmarket.com.tw/blog/category/news-policy','news-policy'),
                ('食安','https://www.newsmarket.com.tw/blog/category/food-safety','food-safety'),
                ('新知','https://www.newsmarket.com.tw/blog/category/knowledge','knowledge'),
                ('綠生活-旅遊-國際通信','https://www.newsmarket.com.tw/blog/category/living-green-travel','living-green-travel')
                ]
    for label,url,foldername in categories:
            scrape_link(session, label, url, foldername, end_date)
