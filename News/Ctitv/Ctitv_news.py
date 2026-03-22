import os
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def Ctitv(session, url, cate, cate1, cate2, end_date):
    num = 1
    article = []
    while True: 
         try:
            base_url = url + cate1 + '/page/' + str(num)
            print(base_url)
         except:
             continue
         soup = BeautifulSoup(session.get(base_url, timeout=20).text,'lxml')
         items = soup.find_all('div','column half b-col')
         if not items:
             break

         last_date_time = ''
         for item in items:
             title = extract_title(item)
             link = extract_link(item)
             label = cate
             print(link)
             try:
                 soup = BeautifulSoup(session.get(link, timeout=20).text,'lxml')
                 
                 author = extract_author(soup)
                 date_time = extract_date(soup)
                 last_date_time = date_time
                 content = extract_content(soup)
                 keyword = extract_keyword(soup)

                 if date_time < end_date:
                     break
                 else:
                     article.append({'date_time':date_time,'title':title,'author':author,
                                     'label':label,'link':link,'content':content,'keyword':keyword})
             except Exception:
                 continue
         if last_date_time and last_date_time < end_date:
             break
         else:
             num += 1
    if len(article)!=0:
        write_to_json(cate2, article)

def extract_title(item):
    try:
        title = item.find('h2','post-title').a.text
    except:
        title = ''
    return title

def extract_link(item):
    try:
        link = item.find('h2','post-title').a['href']
    except:
        link = ''
    return link

def extract_author(soup):
    try:
        author = soup.find('span','reviewer').text
    except:
        author = ''
    return author

def extract_date(soup):
    try:
        date_time = soup.find('time','value-title').text
    except:
        date_time = ''
    return date_time  

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div','post-content description')[0].find_all('p')
        for c in contents:
            content += c.text
    except:
        pass
    return content
           
def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','tagcloud')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except:
        pass
    return keyword
            
def write_to_json(cate2, article):
    file_path = write_json_records(
        records=article,
        source_name='Ctitv',
        category=cate2,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='ctitv',
    )
    print(f"saved: {file_path}")

if __name__ == '__main__':
    end_date = build_end_date(days_back=1)
    print(end_date)
    cates = [('政治要聞','politics-news','politics'),
            ('社會萬象','local-news','society'),
            ('國際兩岸','international','global'),
            ('生活休閒','share-shopping','life'),
            ('健康新知','健康新知-2','health')]

    url = 'https://gotv.ctitv.com.tw/category/'
    session = create_session()
    for cate,cate1,cate2 in cates:
        Ctitv(session, url, cate, cate1, cate2, end_date)
