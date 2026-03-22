import datetime
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, get_soup, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def Scrape(session, url, end_date):
    page = 1
    article = []
    while True:
        base_url = url + str(page)
        print(base_url)
        try:
            soup = get_soup(session, base_url, sleep_seconds=0.2)
        except Exception as error:
            print(f"skip list page by request error: {error}")
            break

        try:
            items = soup.find_all('ul','list-unstyled news-list')[0].find_all('li','d-flex')
            if not items:
                break

            last_date_time = ''
            for item in items:
                title = extract_title(item)
                date_time = extract_date(item)
                link = extract_link(item)
                keyword = extract_keyword(item)
                last_date_time = date_time
                if not date_time or not link:
                    continue

                try:
                    detail_soup = get_soup(session, link, sleep_seconds=0.2)
                except Exception as error:
                    print(f"skip article by request error: {error}")
                    continue

                label = extract_label(detail_soup)
                author = extract_author(detail_soup)
                content = extract_content(detail_soup)

                if date_time < end_date:
                    break
                else:
                    article.append({'date_time':date_time,'author':author,
                                    'title':title,'link':link,'label':label,
                                    'content':content,'keyword':keyword})
            if last_date_time and last_date_time < end_date:
                break
            else:
                page += 1
        except Exception as error:
            print(f"skip page by parse error: {error}")
            break

    if len(article)!=0:
        file_path = write_json_records(
            records=article,
            source_name='PTS',
            category='2020~2021',
            base_output_dir=OUTPUT_BASE_DIR,
            file_prefix='pts',
        )
        print(f"saved: {file_path}")

def extract_title(item):
    try:
        title = item.find('h2').text
    except Exception:
        title = ''
    return title

def extract_date(item):
    try:
        date_time = item.find('time')['datetime']
    except Exception:
        date_time = ''
    return date_time 

def extract_link(item):
    try:
        link = item.find('h2').a.get('href')
    except Exception:
        link = ''
    return link

def extract_keyword(item):                        
    keyword = ''
    try:
        keywords = item.find_all('ul','list-unstyled tag-list d-flex flex-wrap')[0].find_all('a')
        for k in keywords:
            keyword += k.text.replace('...','') + ' '
    except Exception:
        print('no keyword')
    return keyword 

def extract_label(soup):
    try:
        label = soup.find_all('ol','breadcrumb')[0].find_all('li','breadcrumb-item')[1].text.replace('\n','')
    except Exception:
        label = ''
    return label 

def extract_author(soup):
    try:
        author = soup.find('span','article-reporter mr-2').text
    except Exception:
        author = ''
    return author  

def extract_content(soup):
    try:
        content = soup.find('article','post-article').text.replace('\n','').strip()
    except Exception:
        content = ''
    return content

if __name__ == '__main__':
    end_date = build_end_date(days_back=1)
    url = 'https://news.pts.org.tw/dailynews?page='
    session = create_session()
    Scrape(session, url, end_date)
