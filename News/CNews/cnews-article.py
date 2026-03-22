import datetime
import time
import os
import sys
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
        if page != 1:
            page_link = f"https://cnews.com.tw/category/{category}/page/{page}/"
        elif page == 1:
            page_link = f"https://cnews.com.tw/category/{category}/"
        print(page_link)
        try:
            soup = get_soup(session, page_link, sleep_seconds=0.2)
            figures = soup.find_all('figure','special-format')
            if not figures:
                break

            last_date = ''
            for f in figures:
                links = f.find('a')['href']
                print(links)
                if '/category/' in links:
                    continue
                dates = f.find('li','date').text.strip()
                last_date = dates
                if dates < end_date:
                    break
                else:
                    urls.append(links)
            if last_date and last_date < end_date:
                break
            else:
                page += 1
        except Exception as e:
            print(e)
    
    if len(urls)!=0:
        write_urls_to_txt(category,urls)
        scrape_content(session, category, label, urls)
        
def write_urls_to_txt(category,urls):
    #bulid folder yyyy-mm
    folder_path =  '/home/ftp_246/data_1/news_data/CNews/urls/' + time.strftime('%Y-%m') 
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(folder_path + '/'+f'cnews-{category}-urls_'+time.strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url+'\n')
    txtf.close()
    
def scrape_content(session, category, label, urls):
    data_collect = []
    for url in urls:
        print(url)
        time.sleep(1)
        try:
            soup = get_soup(session, url, sleep_seconds=0.2)
            title = soup.find(id='articleTitle')\
                                   .find(class_='_line')\
                                   .strong.text.strip()
            date = soup.find(class_='date').text.strip()
            author = soup.find(class_='user').text.strip()
            label = category
            content = soup.find(
                class_='theme-article-content').article.text.strip()

            keywords = []
            try:
                keywords = [a.text for a in soup.select('.tags > a')]
            except Exception:
                pass
            article = {'url':url,'title':title,
                       'date':date,'author':author,
                       'label':label,'content':content,
                       'keywords':keywords}
            print(article)
            data_collect.append(article)
        except Exception as e:
            print(e)
            pass
    if len(data_collect)!=0:
        write_to_json(label, data_collect)
                   
def write_to_json(label, data_collect):
    file_path = write_json_records(
        records=data_collect,
        source_name='CNews',
        category=label,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='cnews',
    )
    print(f"saved: {file_path}")
    
if __name__ == '__main__':
    end_date = build_end_date(days_back=1)
    print(end_date)
    session = create_session()

    categories = [
                 ('新聞匯流', 'news'),
                 ('政治匯流', 'politics'),
                 ('國際匯流', 'global'),
                 ('生活匯流', 'life'),
                 ('健康匯流', 'health'),
                 ('金融匯流', 'finance'),
                 ('數位匯流', 'tech')
                 ]

    for label, category in categories:
        scrape_link(session, category, label, end_date)
