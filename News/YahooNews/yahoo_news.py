from bs4 import BeautifulSoup
import datetime
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, get_soup, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def Yahoo_news(session, label, cate, tag, url, end_date):
    article = []
    for num in range(0,2000,10):
        base_url = url + f'count=10;loadMore=true;mrs=%7B%22size%22%3A%7B%22w%22%3A220%2C%22h%22%3A128%7D%7D;newsTab={cate};start={num};tag={tag};usePrefetch=false?bkt=ybar_twnews'
        try:
            res = session.get(base_url, timeout=20)
            res.raise_for_status()
        except Exception as error:
            print(f"skip yahoo list page by request error: {error}")
            continue

        print(base_url)
        try:
            parse_json = res.json()
        except Exception:
            continue
        if parse_json is None:
            continue
        stop_by_date = False
        for item in parse_json:
            title = extract_title(item)
            source = extract_source(item)
            date_time = extract_date(item)
            link = extract_link(item)
            if not date_time or not link:
                continue

            try:
                soup = get_soup(session, link, sleep_seconds=0.2)
            except Exception:
                print('link is 404')
                continue

            content = extract_content(soup)
            if date_time < end_date:
                stop_by_date = True
                break
            else:
                article.append({'date_time':date_time,
                                'title':title,
                                'source':source,
                                'link':link,
                                'label':label,
                                'content':content,
                                'keyword':''})
        if stop_by_date:
            break
    if article:
        outputjson(cate, article)

def extract_title(item):
    try:
        title = item['title']
    except Exception:
        title = ''
    return title

def extract_source(item):
    try:
        source = item['provider_name']
    except Exception:
        source = ''
    return source

def extract_date(item):
    try:
        utime = item['published_at']
        date_time = datetime.datetime.utcfromtimestamp(float(utime))
        date_time = date_time.strftime('%Y-%m-%d')
    except Exception:
        date_time = ''
    return date_time


def extract_link(item):
    try:
        link = 'https://tw.news.yahoo.com' + item['url']
    except Exception:
        link = ''
    return link

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div','caas-content-wrapper')[0].find_all('p')
        for c in contents:
            if c.text.startswith('更多'):
                break
            else:
                content += c.text.replace('原始連結','')
    except Exception:
        pass
    return content
            
def outputjson(cate,article):
    file_path = write_json_records(
        records=article,
        source_name='yahoo_news',
        category=cate,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='yahoo',
    )
    print(f"saved: {file_path}")
    
if __name__ == '__main__':
    end_date = build_end_date(days_back=1)
    print(end_date)
    session = create_session()
    categories = [
            ('政治','politics','%5B%22yct%3A001000661%22%5D'),
             ('社會','society','%5B%22ymedia%3Acategory%3D000000179%22%2C%22yct%3A001000798%22%2C%22yct%3A001000667%22%5D'),
             ('國際','global','%5B%22ymedia%3Acategory%3D000000030%22%2C%22ymedia%3Acategory%3D000000032%22%5D'),
             ('生活','life','%5B%22ymedia%3Acategory%3D000000126%22%2C%22yct%3A001000560%22%2C%22yct%3A001000374%22%2C%22yct%3A001001117%22%2C%22yct%3A001000659%22%2C%22yct%3A001000616%22%5D'),
             ('財經','finance','%5B%22yct%3A001000298%22%2C%22yct%3A001000123%22%5D'),
             ('健康','health','%5B%22yct%3A001000395%22%5D'),
             ('科技','tech','%5B%22yct%3A001000931%22%2C%22yct%3A001000742%22%2C%22ymedia%3Acategory%3D000000175%22%5D')]
    url = 'https://tw.news.yahoo.com/_td-news/api/resource/IndexDataService.getExternalMediaNewsList;'
    for label,cate,tag in categories:
        Yahoo_news(session, label, cate, tag, url, end_date)
    
