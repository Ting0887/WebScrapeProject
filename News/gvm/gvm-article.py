from bs4 import BeautifulSoup
import datetime
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, ensure_dir, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def scrape_link(session, label, category, end_date):
    urls = []
    page = 1
    while True:
        page_link = f"https://www.gvm.com.tw/category/{label}?page={page}"
        res = session.get(page_link, timeout=20)
        print(page_link)
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.find_all('div','article-list-item__intro')
        if not items:
            break
    
        date = ''
        for item in items:
            link = item.find('a')['href']
            date = item.find('div','time').text
            print(link)
        
            if date < end_date:
                break
            else:
                urls.append(link)
        if date < end_date:
            break
        page += 1
    if len(urls)!=0:
        write_to_txt(label,urls)
        scrape_content(session, category, label, urls)

def write_to_txt(label,urls):
    folder_path = os.path.join(OUTPUT_BASE_DIR, 'gvm', 'urls', datetime.datetime.today().strftime('%Y-%m'))
    ensure_dir(folder_path)

    with open(folder_path + '/'+f'gvm-{label}-urls_'+datetime.datetime.today().strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url+'\n')
    txtf.close()

def scrape_content(session, category, label, urls):
    data_collect = []
    for url in urls:
        try:
            res = session.get(url, timeout=20)
            soup = BeautifulSoup(res.text,'lxml')
            title = soup.find('h1').text
            author = soup.find('div', class_="pc-bigArticle").a.text
            date = soup.find(class_='article-time').text
            content = soup.find(class_='article-content').text.strip()
        except Exception:
            continue
        try:
            keywords = [k.text for k in soup.find(class_='article-keyword').find_all('a')]
        except Exception:
            keywords = ''
        
        article = {'url':url,'title':title,'author':author,
                   'date':date,'label':category,'content':content,'keywords':keywords}      
        data_collect.append(article)
        
    if len(data_collect)!=0:
        write_to_json(label,data_collect)

def write_to_json(label,data_collect):
    file_path = write_json_records(
        records=data_collect,
        source_name='gvm',
        category=label,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='gvm',
    )
    print(f"saved: {file_path}")
    
if __name__ == '__main__':
    session = create_session()
    end_date = build_end_date(days_back=1)
    
    categories = [('news','時事熱點'),('world','國際'),('money','金融'),
                  ('tech','科技'),('business','產經'),('life','生活')]

    for label,category in categories:
        scrape_link(session, label, category, end_date)
