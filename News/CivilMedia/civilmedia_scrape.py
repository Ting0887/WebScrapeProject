import time
import datetime
import os
import sys
from bs4 import BeautifulSoup
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, get_soup, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def scrape_link(session, url, cate, folder, end_date):
    page = 1
    newslink = []
    while True:
        link = url + '/page/' + str(page)
        try:
            soup = get_soup(session, link, sleep_seconds=0.2)
        except Exception as error:
            print(f"skip list page by request error: {error}")
            break

        sections = soup.select('section')
        if not sections:
            break
        article_bar = sections[0].find_all('div','post-box one-half')
        if not article_bar:
            break

        last_date_time = ''
        for item in article_bar:
            try:
                link = item.find('a')['href']
            except Exception:
                link = ''
            try:
                date_time = item.find('div','entry-meta').text
            except Exception:
                date_time = ''
            last_date_time = date_time
            print(date_time)
            if date_time < end_date:
                break
            elif link != '':
                newslink.append(link)

        if last_date_time and last_date_time < end_date:
            break
        else:
            page += 1
    if len(newslink)!=0:
        scrape_content(session, cate, folder, newslink)

def scrape_content(session, cate, folder, newslink):
    article = []
    for link in newslink:
        try:
            soup = get_soup(session, link, sleep_seconds=0.2)
        except Exception as error:
            print(f"skip article by request error: {error}")
            continue

        try:
            title = soup.find('h1').text
        except Exception:
            title = ''
        try:
            date_time = soup.find_all('div','entry-meta clearfix')[0].text[:11].replace('\n','').strip()
        except Exception:
            date_time = ''

        content = ''
        try:
            contents = soup.find_all('section','entry-content clearfix')[0].find_all('p')
            for c in contents:
                content += c.text + ' '
        except Exception:
            pass

        keyword = ''
        try:
            keywords = soup.find_all('a',{'rel':'tag'})
            for k in keywords:
                keyword += k.text + ' '
        except Exception:
            pass

        article.append({'date_time':date_time,
                        'author':'',
                        'title':title,
                        'label':cate,
                        'link':link,
                        'content':content,
                        'keyword':keyword})
    if len(article)!=0:
        write_to_json(folder, article)

def write_to_json(folder, article):
    file_path = write_json_records(
        records=article,
        source_name='civilmedia',
        category=folder,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='civilmedia',
    )
    print(f"saved: {file_path}")

if __name__ == '__main__':
    end_date = build_end_date(days_back=1)
    print(end_date)
    session = create_session()
    
    #categories
    cate_url = [('https://www.civilmedia.tw/archives/category/environment','環境','environment'),
                ('https://www.civilmedia.tw/archives/category/%e4%ba%ba%e6%ac%8a','人權','humanrights'),
                ('https://www.civilmedia.tw/archives/category/%e5%8b%9e%e5%b7%a5','勞工','labor'),
                ('https://www.civilmedia.tw/archives/category/aborigines','原民','aborigine'),
                ('https://www.civilmedia.tw/archives/category/migrant','移民','migrant')]

    for url,cate,folder in cate_url:
        scrape_link(session, url, cate, folder, end_date)
