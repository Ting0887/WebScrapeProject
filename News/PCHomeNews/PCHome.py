import requests.packages.urllib3
from bs4 import BeautifulSoup
import time
import datetime
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import create_session, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

requests.packages.urllib3.disable_warnings()

def build_end_date(hours_back=12):
    target_date = datetime.datetime.today() - datetime.timedelta(hours=hours_back)
    return target_date.strftime('%Y-%m-%d %H:%M:%S')


def Scrape(session, cate, cate1, folder, end_date):
    datalist = []
    for num in range(1,17):
        url = f'https://news.pchome.com.tw/cat/{cate}/hot/{num}'
        print(url)
        res = session.get(url, verify=False, timeout=20)
        res.encoding = 'utf8'
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.find_all('div','channel_newssection')
        date_time = ''
        for item in items:
            try:
                title = item.find('a')['title']  #title
                print(title)
                link = 'https://news.pchome.com.tw' + item.find('a')['href'] #link
                    
                res = session.get(link, verify=False, timeout=20)
                soup = BeautifulSoup(res.text,'lxml')
                date_time = soup.find('time')['datetime']  #date_time
                author = soup.find('time').text.replace(date_time,'').strip() #author
                    
                content = soup.find('div',{'class':'article_text'}).text.replace('\n','').strip() #content
                   
                keyword = ''
                keywords = soup.select('.ent_kw')[0].find_all('a')
                for k in keywords:
                    keyword += k.text + ' '
                print(keyword)              
            except Exception:
                continue
                
            if date_time < end_date:
                break
                
            article = {'date_time':date_time,'title':title,
                       'author':author,'link':link,
                       'label':cate1,'content':content,
                       'keyword':keyword}

            datalist.append(article)
        if date_time < end_date:
            break
    if len(datalist)!=0:
        write_to_json(datalist,cate,folder)

def write_to_json(datalist,cate,folder):
    file_path = write_json_records(
        records=datalist,
        source_name='PCHome',
        category=folder,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='PCHome',
    )
    print(f"saved: {file_path}")

def main():
    session = create_session()
    end_date = build_end_date(hours_back=12)
    cates = [('politics','政治','politics'),
             ('society', '社會','society'),
             ('internation' , '國際','global'),
             ('healthcare', '健康','health'),
             ('finance','財經','finance'),
             ('living' , '生活','life'),
             ('science','科技','tech')]

    for cate,cate1,folder in cates:
        Scrape(session, cate, cate1, folder, end_date)

if __name__ == '__main__':
    main()
