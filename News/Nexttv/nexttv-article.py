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

def scrape_link(session, category, label, number, end_date):
    page = 1
    urls = []
    while True:
        page_link = 'http://www.nexttv.com.tw/m2o/loadmore.php'
        payload = {'offset' : 3+(page-1)*6, 'count' : 6, 'column_id' : number}
        res = session.post(page_link, data=payload, timeout=20)
        date = ''
        for item in res.json():
            url = item['content_url']
            print(url)
            date = item['file_name'].split('/')[0]
            if date < end_date:
                break
            urls.append(url)
        if date < end_date:
                break
        else:
            page += 1
    if len(urls)!=0:
        write_to_txt(category,urls)
        scrape_content(session, category, label, urls)

def write_to_txt(category,urls):
    folder_path = os.path.join(OUTPUT_BASE_DIR, 'nexttv', 'urls', datetime.datetime.today().strftime('%Y-%m'))
    ensure_dir(folder_path)
    filename = f'nexttv-{category}-'+datetime.datetime.today().strftime('%Y-%m-%d') + '.txt'
    with open(folder_path+'/'+filename,'w',encoding='utf8') as txtf:
        for url in urls:
            txtf.write(url+'\n')
    txtf.close()
        
def scrape_content(session, category, label, urls):
    data_collect = []
    for url in urls:
        r = session.get(url, timeout=20)
        r.encoding = 'utf8' # 避免亂碼出現
        soup = BeautifulSoup(r.text, 'lxml')        
        try:
            title = soup.find(class_='articletitle').text
            date = soup.find(class_='time').text
            content = soup.find(class_='article-main').text.strip()
            article = {'url':url,'title':title,'date':date,'label':label,'content':content}
            print(article)
            data_collect.append(article)
        except Exception as e:
            print(e)
    if len(data_collect)!=0:
        write_to_json(category, data_collect)

def write_to_json(category, data_collect):
    file_path = write_json_records(
        records=data_collect,
        source_name='nexttv',
        category=category,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='nexttv',
    )
    print(f"saved: {file_path}")

if __name__=='__main__':
    session = create_session()
    end_date = build_end_date(days_back=1)

    categories = [('politics', '政治',144),
                  ('society' , '社會',145),
                  ('finance' , '財經',147),
                  ('world'   , '國際',148),
                  ('life'    , '生活',149)]

    for category, label,number in categories:
        scrape_link(session, category, label, number, end_date)
