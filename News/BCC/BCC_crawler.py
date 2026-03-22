import os
import datetime
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, get_soup, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def category_url(session, cate, cate1, cate2, end_date):
    page = 1
    collect_url = []
    while True:
        url = f'https://bccnews.com.tw/archives/category/{cate2}/page/{page}'
        print(url)
        try:
            soup = get_soup(session, url, sleep_seconds=0.2)
        except Exception as error:
            print(f"skip page by request error: {error}")
            break

        wrapper = soup.find('div', id='tdi_65')
        article = wrapper.find_all('div', 'td-module-thumb') if wrapper else []
        if not article:
            break

        date_time = ''
        for item in article:
            link_tag = item.find('a', 'td-image-wrap')
            link = link_tag.get('href') if link_tag else ''
            if not link:
                continue

            try:
                detail_soup = get_soup(session, link, sleep_seconds=0.2)
            except Exception as error:
                print(f"skip article url by request error: {error}")
                continue

            time_node = detail_soup.find('time')
            date_time = time_node.get('datetime', '')[0:10] if time_node else ''
            print(date_time)
            if not date_time:
                continue

            if date_time < end_date:
                break
            else:
                collect_url.append(link)
        if date_time and date_time < end_date:
            break
        else:
            page += 1
    if len(collect_url)!=0:
        scrape_info(session, collect_url, cate, cate1)

def scrape_info(session, collect_url, cate, cate1):
    article = []
    for link in collect_url:
        try:
            soup = get_soup(session, link, sleep_seconds=0.2)
        except Exception as error:
            print(f"skip article by request error: {error}")
            continue
        
        date_time = extract_date(soup)
        title = extract_title(soup)
        content = extract_content(soup)
        keyword = extract_keyword(soup)
        post = {'title':title,'author':'','date_time':date_time,
                'content':content,'keyword':keyword,'link':link,
                'label':cate,'website':'中國廣播公司'}
        print(post)
        article.append(post)
    if len(article)!=0:
        file_path = write_json_records(
            records=article,
            source_name='BCC',
            category=cate1,
            base_output_dir=OUTPUT_BASE_DIR,
            file_prefix='BCC',
        )
        print(f"saved: {file_path}")

def extract_date(soup):
    try:
        date_time = soup.find('time')['datetime'][0:10]
    except Exception:
        date_time = ''
    return date_time

def extract_title(soup):
    try:
        title = soup.find('h1').text
    except Exception:
        title = ''
    return title

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('p')
        for c in contents:
            if '本網站內容屬於中國' in c.text:
                break
            else:
                content += c.text
    except Exception:
        pass
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('ul','tdb-tags')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except Exception:
        keyword = ''
    return keyword

if __name__ == '__main__':
    end_date = build_end_date(days_back=1)
    print(end_date)
    session = create_session()
    categories = [('政治','politics','c-03'),
                  ('國際','internation','c-04'),
                  ('社會','society','c-08'),
                  ('生活','life','c-07'),
                  ('財經','finance','c-06')]

    for cate,cate1,cate2 in categories:
        category_url(session, cate, cate1, cate2, end_date)

