import datetime
import os
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, get_soup, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def scrape_link(session, category, label, end_date):
    urls = []
    page = 1
    while True:
        page_link = f"https://www.cmmedia.com.tw/api/articles?num=12&page={page}&category={category}"
        try:
            res = session.get(page_link, timeout=20)
            res.raise_for_status()
        except Exception as error:
            print(f"skip list page by request error: {error}")
            break

        try:
            items = res.json()
            if not items:
                break

            last_date = ''
            for item in res.json():
                link = 'https://www.cmmedia.com.tw/home/articles/'+str(item['id'])
                soup = get_soup(session, link, sleep_seconds=0.2)
                dates = soup.find(class_="article_author-bar").span.next_sibling.text
                last_date = dates
                if dates < end_date:
                    break
                else:
                    print(link)
                    urls.append(link)

            if last_date and last_date < end_date:
                break
            else:
                page += 1
        except Exception as e:
            print(e)
    
    if len(urls)!=0:
        write_urls_to_txt(category,urls)
        scrape_content(session, label, category, urls)
        
def write_urls_to_txt(category,urls):
    #bulid folder yyyy-mm
    folder_path =  '/home/ftp_246/data_1/news_data/CMMedia/urls/' + time.strftime('%Y-%m') 
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(folder_path + '/'+f'cmmedia-{category}-urls_'+time.strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url)
            txtf.write('\n')
    txtf.close()

def scrape_content(session, label, category, urls):
    data_collect = []
    for link in urls:
        soup = get_soup(session, link, sleep_seconds=0.2)
        try:
            url = link.replace('\n','')
            title = soup.find(class_='article_title').text
            author = soup.find(class_="article_author-bar").span.text
            date = soup.find(class_="article_author-bar").span.next_sibling.text
            content = ''.join(p.text for p in soup.select(".article_content > p"))
            article = {'url':url,'title':title,
                        'author':author,'date':date,
                        'label':label,'content':content}
            print(article)
            data_collect.append(article)
        except Exception as e:
                print(e)
    if len(data_collect)!=0:
        write_to_json(category, data_collect)
                   
def write_to_json(category, data_collect):
    file_path = write_json_records(
        records=data_collect,
        source_name='CMMedia',
        category=category,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='cmmedia',
    )
    print(f"saved: {file_path}")
    
if __name__ == '__main__':
    session = create_session()
    end_date = build_end_date(days_back=1)
    print(end_date)
    
    categories = [
                ('politics', '政治'),
                ('life'    , '生活'),
                ('finance' , '財經'),
                 ]
    
    for category, label in categories:
        scrape_link(session, category, label, end_date)
