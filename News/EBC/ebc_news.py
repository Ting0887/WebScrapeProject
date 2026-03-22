import datetime
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import create_session, get_soup, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def build_ebc_end_date(days_back=1):
    target_date = datetime.datetime.today() - datetime.timedelta(days=days_back)
    return target_date.strftime('%Y/%m/%d')


def parse_cateurl(session, cate, cate1, url, end_date):
    num = 1
    article = []
    while True:
        payloads = {'cate_code': cate1,
                    'exclude':'295762,295760,295759,295752,295748',
                    'page': num}

        try:
            res = session.post(url, data=payloads, timeout=20)
            res.raise_for_status()
        except Exception as error:
            print(f"skip list page by request error: {error}")
            break

        soup = get_soup_from_text(res.text)
        list_wrap = soup.find_all('div', 'white-box news-list-area')
        if not list_wrap:
            break
        items = list_wrap[0].find_all('div', 'style1 white-box')
        if not items:
            break

        date_time = ''
        for item in items:
            link = extract_newslink(item)
            print(link)
            if not link:
                continue

            try:
                soup = get_soup(session, link, sleep_seconds=0.2)
            except Exception as error:
                print(f"skip article by request error: {error}")
                continue

            title = extract_title(soup)
            date_time = extract_date(soup)
            content = extract_content(soup)
            keyword = extract_keyword(soup)
            if not date_time:
                continue
            if date_time < end_date:
                break
            post = {'date_time':date_time,'title':title,'label':cate,
                        'link':link,'content':content,'keyword':keyword}
            print(post)
            article.append(post)
        if date_time and date_time < end_date:
            break
        else:
            num += 1
    if len(article)!=0:
        file_path = write_json_records(
            records=article,
            source_name='EBC',
            category=cate1,
            base_output_dir=OUTPUT_BASE_DIR,
            file_prefix='ebc',
        )
        print(f"saved: {file_path}")


def get_soup_from_text(html):
    from bs4 import BeautifulSoup

    return BeautifulSoup(html, 'lxml')

def extract_newslink(item):
    try:
        link = 'https://news.ebc.net.tw' + item.find('a')['href']
    except Exception:
        link = ''
    return link

def extract_title(soup):
    try:
        title = soup.find('h1').text
    except Exception:
        title = ''
    return title

def extract_date(soup):
    try:
        date_time = soup.find('span','small-gray-text').text[0:17]
    except Exception:
        date_time = ''
    return date_time
        
def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div','raw-style')[0].find_all('p')
        for c in contents:
            content += c.text.replace('\n','').replace('\r','')
    except Exception:
        pass    
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','keyword')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except Exception:
        pass
    return keyword
    
if __name__ == '__main__':
    end_date = build_ebc_end_date(days_back=1)
    
    url = 'https://news.ebc.net.tw/News/List_Category_Realtime'
    session = create_session(headers={'x-requested-with': 'XMLHttpRequest'})

    cates = [('政治','politics'),('社會','society'),
             ('國際','world'),('生活','living'),
             ('財經','business'),('健康','health')]
    for cate,cate1 in cates:
        parse_cateurl(session, cate, cate1, url, end_date)
