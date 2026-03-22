from bs4 import BeautifulSoup
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, ensure_dir, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def scrape_link(session, url_cate, label, category, end_date):
    urls = []
    page = 1
    while True:
        page_link = f'https://www.ntdtv.com/b5/{url_cate}/{page}'
        print(page_link)
        res = session.get(page_link, timeout=20)
        if res.status_code != 200:
            break
        soup = BeautifulSoup(res.text,'lxml')
        date = ''
        for h in soup.select('.post_list .text'):
            url = h.find(class_='title').a['href']
            
            #get date
            y = url.split('/b5/')[-1].split('/')[0]
            m = url.split('/b5/')[-1].split('/')[1]
            d = url.split('/b5/')[-1].split('/')[2]
            date = y+'-'+m+'-'+d
            print(url)
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
    import datetime

    folder_path = os.path.join(OUTPUT_BASE_DIR, 'ntdtv', 'urls', datetime.datetime.today().strftime('%Y-%m'))
    ensure_dir(folder_path)
    filename = f'ntdtv-{category}-urls-' + datetime.datetime.today().strftime('%Y-%m-%d') + '.json'
    with open(folder_path+'/'+filename,'w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url+'\n')
    txtf.close()

def scrape_content(session, category, label, urls):
    data_collect = []
    for url in urls:
        soup = BeautifulSoup(session.get(url, timeout=20).text,'lxml')
        try:
            title = soup.find(class_='article_title').h1.text
            date = soup.find(class_='time').span.text
            contents = soup.find(class_='post_content').find_all('p')
            content_strings = [x.text.strip() for x in contents]
            content = ''.join(content_strings)
            article = {'url':url,'title':title,'date':date,'label':label,'content':content}
            print(article)
            data_collect.append(article)
        except Exception as e:
            print(e)
            pass
    if len(data_collect)!=0:
        write_to_json(category, data_collect)

def write_to_json(category, data_collect):
    file_path = write_json_records(
        records=data_collect,
        source_name='ntdtv',
        category=category,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='ntdtv',
    )
    print(f"saved: {file_path}")

if __name__ == '__main__':
    session = create_session()
    end_date = build_end_date(days_back=1)
    
    categories = [('prog202', '國際', 'world'),
                  ('prog204', '大陸', 'china'),
                  ('prog203', '美國', 'usa'),
                  ('prog206', '台灣', 'taiwan'),
                  ('prog205', '港澳', 'hk'),
                  ('prog208', '財經', 'finance'),
                  ('prog1255', '健康', 'health')]

    for url_cate, label,category in categories:
        scrape_link(session, url_cate, label, category, end_date)
