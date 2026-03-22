from bs4 import BeautifulSoup
import datetime
import time
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import create_session, ensure_dir, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def build_ftv_end_date(days_back=1):
    target_date = datetime.datetime.today() - datetime.timedelta(days=days_back)
    return target_date.strftime('%Y/%m/%d')


def scrape_link(session, category, label, end_date):
    urls = []
    page = 1
    while True:
        page_link = f"https://www.ftvnews.com.tw/tag/{category}/{page}"
        print(page_link)
        resq = session.get(page_link, timeout=20)
        if resq.status_code != 200:
            break
        try:
            soup = BeautifulSoup(resq.text,'lxml')
            items = soup.find_all('ul','row')[1].find_all('li','col-lg-4 col-sm-6')
            dates = ''
            for item in items:
                links = 'https://www.ftvnews.com.tw'+item.find('a')['href']  
                print(links)
                dates = item.find('div','time').text.strip()
                if dates < end_date:
                    break
                else:
                    urls.append(links)
            if dates < end_date:
                break
            else:
                page += 1
        except Exception as e:
            break
    
    if len(urls)!=0:
        write_urls_to_txt(label,urls)
        scrape_article(session, category, label, urls)
        
def write_urls_to_txt(label,urls):
    folder_path = os.path.join(OUTPUT_BASE_DIR, 'FTVNnews', 'urls', time.strftime('%Y-%m'))
    ensure_dir(folder_path)

    with open(folder_path + '/'+f'ftv-{label}-urls_'+time.strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url+'\n')
    txtf.close()
    
def scrape_article(session, category, label, urls):
    data_collect = []
    for url in urls:
        time.sleep(1)
        try:
            res = session.get(url, timeout=20)
            soup = BeautifulSoup(res.text,'lxml')
            title = extract_title(soup)
            date = extract_date(soup)
            contents = extract_content(soup)
            summary = extract_summary(soup)
            article = {'contents':contents,'summary':summary,'label':category,
                       'date':date,'title':title,'url':url}
            print(article)
            data_collect.append(article)
        except Exception as e:
            print(e)
    if len(data_collect)!=0:
        write_to_json(label, data_collect)

def extract_title(soup):
    try:
        title = soup.find('h1','text-center').text.replace('\n','').replace('\r','').strip()
    except Exception:
        title = ''
    return title

def extract_date(soup):
    try:
        date = soup.find('li','date').text.strip()
    except Exception:
        date = ''
    return date

def extract_content(soup):
    contents = ''
    try:
        content = soup.find_all('article')[0].find_all('p')
        for c in content:
            contents += c.text.replace('\n','')
    except Exception:
        pass
    return contents

def extract_summary(soup):
    try:
        summary = soup.find('div',id='preface').text
    except Exception:
        summary = ''
    return summary

def write_to_json(label, data_collect):
    file_path = write_json_records(
        records=data_collect,
        source_name='FTVNnews',
        category=label,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='ftv',
    )
    print(f"saved: {file_path}")
    
if __name__ == '__main__':
    session = create_session()
    end_date = build_ftv_end_date(days_back=1)
    print(end_date)

    categories = [('政治','politics'),('國際','world'),('社會','society'),
                  ('生活','life'),('健康','health'),('財經', 'finance'),]
    for category, label in categories:
        scrape_link(session, category, label, end_date)
