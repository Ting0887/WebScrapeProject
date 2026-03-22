from bs4 import BeautifulSoup
import datetime
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import create_session, ensure_dir, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")


def build_ctv_end_date(days_back=1):
    target_date = datetime.datetime.today() - datetime.timedelta(days=days_back)
    return target_date.strftime('%Y/%m/%d')

def scrape_link(session, label, category, end_date):
    urls = []
    page = 1
    while True:
        if page == 1:
            page_link = f"http://new.ctv.com.tw/Category/{category}"
        else:
            page_link = f"http://new.ctv.com.tw/Category/{category}?PageIndex={page}"
        res = session.get(page_link, timeout=20)
        soup = BeautifulSoup(res.text,'lxml')
        date = ''
        for a in soup.select("div.list")[1].find_all('a'):
            link = 'http://new.ctv.com.tw' + a['href']
            print(link)
            date = a.find('div','time').text
            print(date)
            if date < end_date:
                break
            else:
                print(link)
                urls.append(link)
        if date < end_date:
            break
        else:
            page += 1
    if len(urls)!=0:
        write_to_txt(label,urls)
        scrape_content(session, category, label, urls)

def write_to_txt(label,urls):
    folder_path = os.path.join(OUTPUT_BASE_DIR, 'CTV', 'urls', datetime.datetime.today().strftime('%Y-%m'))
    ensure_dir(folder_path)

    with open(folder_path + '/'+f'ctv-{label}-urls_'+datetime.datetime.today().strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url+'\n')
    txtf.close()

def scrape_content(session, category, label, urls):
    data_collect = []
    for link in urls:
        try:
            res = session.get(link, timeout=20)
            soup = BeautifulSoup(res.text,'lxml')
            title = soup.find(class_='title').text.split('│')[0].strip()
            date = soup.find(class_='author').text.split('|')[1].strip()
            content = soup.find(class_='editor').text.strip()
            article = {'url':link,'title':title,'date':date,'label':category,'content':content}
            print(article)
            data_collect.append(article)
        except Exception as e:
            print(e)
    
    if len(data_collect)!=0:
        write_to_json(label,data_collect)

def write_to_json(label,data_collect):
    file_path = write_json_records(
        records=data_collect,
        source_name='CTV',
        category=label,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='ctv',
    )
    print(f"saved: {file_path}")
    
if __name__ == '__main__':
    session = create_session(headers={'Host': 'new.ctv.com.tw', 'Connection': 'keep-alive'})
    end_date = build_ctv_end_date(days_back=1)
    
    categories = [
        ('popular', '十大發燒新聞'),
        ('life', '生活'),
        ('society', '社會'),
        ('world', '國際'),
        ('politics','政治')
    ]
    for label,category in categories:
        scrape_link(session, label, category, end_date)
