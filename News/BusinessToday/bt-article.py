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


def scrape_link(session, category, number, end_date):
    urls = []
    page = 1
    while True:
        page_link = f"http://www.businesstoday.com.tw/catalog/{number}/list/page/{page}"
        try:
            soup = get_soup(session, page_link, sleep_seconds=0.2)
        except Exception as error:
            print(f"skip list page by request error: {error}")
            break

        articles = soup.find_all(class_='article__item')
        if not articles:
            break

        last_date = ''
        for article in articles:
            date_node = article.find('p', 'article__item-date')
            dates = date_node.text.strip() if date_node else ''
            links = article.get('href', '')
            last_date = dates
            if not dates or not links:
                continue
            if dates < end_date:
                break
            print(links)
            urls.append(links)
        if last_date and last_date < end_date:
            break
        else:
            page += 1
    
    if len(urls)!=0:
        write_urls_to_txt(category,urls)
        scrape_content(session, category, urls)
        
def write_urls_to_txt(category,urls):
    #bulid folder yyyy-mm
    folder_path = '/home/ftp_246/data_1/news_data/businesstoday' + '/urls/' +time.strftime('%Y-%m') 
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(folder_path + '/'+f'bt-{category}-urls_'+time.strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url)
            txtf.write('\n')
    txtf.close()
        
def scrape_content(session, category, urls):
    data_collect = []
    for link in urls:
        try:
            soup = get_soup(session, link, sleep_seconds=0.2)
            article = {}

            article['url'] = link
            article['author'] = soup.find(class_='context__info-item--author').text
            article['title'] = soup.find(class_='article__maintitle').text
            article['date'] = soup.find(class_='context__info-item--date').text
            article['label'] = soup.find(class_='context__info-item--type').text
            article['content'] = ''.join(p.text.strip() for p in soup.find(itemprop='articleBody').select('div > div > p'))
            data_collect.append(article)
            
        except Exception as err:
            print('Error: could not parse.')
            print(err)
    if len(data_collect)!=0:
        write_to_json(category, data_collect)
                   
def write_to_json(category, data_collect):
    file_path = write_json_records(
        records=data_collect,
        source_name='businesstoday',
        category=category,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='bt',
    )
    print(f"saved: {file_path}")
    
if __name__ == '__main__':
    end_date = build_end_date(days_back=1)
    session = create_session()

    categories = [('finance', '80391'),('health' , '183029'),
                  ('life&consume','183030'),('tech','183015'),
                  ('politics&society','183027'),('InternationalGeneralEconomics','183025')]

    for category, number in categories:
        scrape_link(session, category, number, end_date)

