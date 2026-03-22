from bs4 import BeautifulSoup
import os
import datetime
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import create_session, get_soup, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def build_nownews_end_date(days_back=7):
    target_date = datetime.datetime.today() - datetime.timedelta(days=days_back)
    return target_date.strftime('%Y-%m-%d')


def Nownews(session, url, cate, cate1, cate2, end_date):
    base_url = url + cate2 + '/'
    try:
        res = session.get(base_url, timeout=20)
        res.raise_for_status()
        parse_js = res.json()
    except Exception as error:
        print(f"skip initial category request by error: {error}")
        return

    news_list = parse_js.get('data', {}).get('newsList', [])
    if not news_list:
        return

    last_pid = news_list[-1].get('id', '')
    if not last_pid:
        return

    data_article = []
    while True:
        try:
            base_url = url + cate2 + '/' + '?pid=' + last_pid
            print(base_url)
            res = session.get(base_url, timeout=20)
            res.raise_for_status()
            parse_js = res.json()
            data = parse_js.get('data', {})
            news_list = data.get('newsList', [])
            if not news_list:
                break

            stop_by_date = False
            for item in news_list:
                title = extract_title(item)
                link = extract_link(item)
                date_time = extract_date(item)
                if not date_time or not link:
                    continue

                try:
                    soup = get_soup(session, link, sleep_seconds=0.2)
                except Exception as error:
                    print(f"skip article by request error: {error}")
                    continue

                [x.extract() for x in soup.findAll(['script', 'br'])]
                label = cate
                author = extract_author(soup)
                content = extract_content(soup)
                keyword = extract_keyword(soup)

                if date_time < end_date:
                    stop_by_date = True
                    break

                data_article.append({'date_time':date_time,'title':title,
                                     'author':author,'label':label,
                                     'link':link,'content':content,
                                     'keyword':keyword})

            last_pid = news_list[-1].get('id', '')
            if stop_by_date or not last_pid:
                break
        except Exception:
            break

    if len(data_article)!=0:
        write_into_json(cate1, data_article)

def extract_title(item):
    try:
        title = item['postTitle']
    except Exception:
        title = ''
    return title

def extract_link(item):
    try:
        link = 'https://www.nownews.com' + item['postUrl']
    except Exception:
        link = ''
    return link 

def extract_date(item):
    try:
        date_time = item['newsDate']
    except Exception:
        date_time = ''
    return date_time    

def extract_author(soup):
    try:
        author = soup.find('div','info').p.text
    except Exception:
        author = ''
    return author

def extract_content(soup):
    try:
        content = soup.find('article').text.replace('\n','').replace('\t','').strip()
    except Exception:
        content = ''
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('ul','tag')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except Exception:
        pass
    return keyword

def write_into_json(cate1, data_article):
    file_path = write_json_records(
        records=data_article,
        source_name='Nownews',
        category=cate1,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='Nownews',
    )
    print(f"saved: {file_path}")
    
if __name__ == '__main__':
    end_date = build_nownews_end_date(days_back=7)
    session = create_session()
    
    cates = [
            ('政治','politics','news-summary'),
            ('社會','society','society'),
            ('國際','global','news-global'),
            ('生活','life','life'),
            ('健康','health','health-life'),
            ('財經','finance','finance')
            ]
    
    url ='https://www.nownews.com/nn-client/api/v1/cat/'
    for cate,cate1,cate2 in cates:
        Nownews(session, url, cate, cate1, cate2, end_date)
