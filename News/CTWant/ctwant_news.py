import os
import datetime
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, get_soup, join_text, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def CTWant(session, url, cate, cate1, end_date):
    page = 1 
    article = []
    while True:
        base_url = url + cate1 + '?page=' + str(page)
        print(base_url)
        try:
            soup = get_soup(session, base_url, sleep_seconds=0.2)
        except Exception as error:
            print(f"skip list page by request error: {error}")
            break

        items = soup.find_all('a','m-card col-sm-4 col-6')
        if not items:
            break

        date_time = ''
        for item in items:
            title = extract_title(item)
            link = extract_link(item)
            if not link:
                continue
            
            try:
                soup = get_soup(session, link, sleep_seconds=0.2)
            except Exception as error:
                print(f"skip article by request error: {error}")
                continue
            
            date_time = extract_date(soup)
            author = extract_author(soup)
            content = extract_content(soup)
            keyword = extract_keyword(soup)
            if not date_time:
                continue

            if date_time < end_date:
                break
            else:
                article.append({'date_time':date_time,'title':title,'author':author,
                                'link':link,'label':cate1,'content':content,'keyword':keyword})
        if date_time and date_time < end_date:
            break
        else:
            page += 1

    if len(article)!=0:
        file_path = write_json_records(
            records=article,
            source_name='CTWant',
            category=cate,
            base_output_dir=OUTPUT_BASE_DIR,
            file_prefix='ctwant',
        )
        print(f"saved: {file_path}")

def extract_title(item):
    try:
        title = item.find('h3').text.replace('\n','').strip()
    except Exception:
        title = ''
    return title

def extract_link(item):
    try:
        link = 'https://www.ctwant.com' + item['href']
    except Exception:
        link = ''
    return link

def extract_date(soup):    
    try:
        date_time = soup.find('time')['datetime']
    except Exception:
        date_time = ''
    return date_time

def extract_author(soup):
    try:
        author_text = soup.find('span','p-article-info__author').text
        author = author_text.split(':', 1)[-1].strip()
    except Exception:
        author = ''
    return author
            
def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('article')[0].find_all('p')
        content = join_text(contents)
    except Exception:
        pass
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','l-tags__wrapper')[0].find_all('a')
        keyword = ' '.join(k.text.replace('\n','').replace(' ','') for k in keywords)
    except Exception:
        pass
    return keyword
    
if __name__ == '__main__':
    end_date = build_end_date(days_back=1)
    print(end_date)                                     
    session = create_session()
    cates = [('society','社會'),('finance','財經'),('politics','政治'),
            ('life','生活'),('global','國際')]

    url = 'https://www.ctwant.com/category/'
    for cate,cate1 in cates:
        CTWant(session, url, cate, cate1, end_date)
