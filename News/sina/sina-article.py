import time
import os
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import create_session, ensure_dir, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def scrape_link(session, category, label, start_date, end_date, delta):   
    urls = []
    while start_date.strftime('%Y%m%d') > end_date:
        page = 1
        while True:
            page_link = f'https://news.sina.com.tw/realtime/{category}/tw/'+\
                start_date.strftime('%Y%m%d')+'/list-'+str(page)+'.html'           
            time.sleep(1)
            res = session.get(page_link, timeout=20)
            soup = BeautifulSoup(res.text,'lxml')
            try:
                items = soup.find_all('ul','realtime')[0].find_all('a')
                if len(items) == 0:
                    break
                else:
                    page += 1
                    print(page_link)
                for item in items:
                    link = 'https://news.sina.com.tw' + item['href']
                    urls.append(link)
                    
            except Exception:
               break
        start_date -= delta
    if len(urls)!=0:
        write_to_txt(category,urls)
        scrape_content(session, category, label, urls)
        
def write_to_txt(category,urls):
    folder_path = f'/home/ftp_246/data_1/news_data/sina/{category}/urls'
    ensure_dir(folder_path)
    
    filename = f'sina-{category}-urls-'+time.strftime('%Y-%m-%d')+'.txt'
    with open(folder_path+'/'+filename,'w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url+'\n')
    txtf.close()

def scrape_content(session, category, label, urls):
    data_collect = []
    for url in urls:
        soup = BeautifulSoup(session.get(url, timeout=20).text,'lxml')
        time.sleep(1)
        try:
            title = soup.find('h1').text.strip()
            source = soup.find('cite').a.text
            date = soup.find('cite').text.strip()\
                              [len(source):]\
                              .strip()\
                              .lstrip('(')\
                              .rstrip(')')
        except Exception:
            continue
        
        try:
            content = soup.find(class_='pcont').text.replace('\n','').replace('\t','').strip()
        except Exception:
            content = ''
        article = {'url':url,'title':title,
                   'source':source,'date':date,
                   'label':label,'content':content}
        print(article)
        data_collect.append(article)
    if len(data_collect)!=0:
        write_to_json(category, data_collect)

def write_to_json(category, data_collect):
    file_path = write_json_records(
        records=data_collect,
        source_name='sina',
        category=category,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='sina',
    )
    print(f"saved: {file_path}")
                        
if __name__ == '__main__':
    #startdate enddate
    import datetime

    session = create_session()
    start_date = datetime.datetime.strptime(time.strftime('%Y%m%d'),'%Y%m%d')
    
    ten_days = datetime.timedelta(days=2)
    delta = datetime.timedelta(days=1)
    end_date = (start_date - ten_days).strftime('%Y%m%d')
    print(end_date)
    categories = [('politics', '政治'),
                  ('society' , '社會'),
                  ('china'   , '兩岸'),
                  ('global'  , '國際'),
                  ('life'    , '生活'),
                  ('finance' , '財經'),
                  ('tech'    , '科技')]
    for category,label in categories:
        scrape_link(session, category, label, start_date, end_date, delta)

