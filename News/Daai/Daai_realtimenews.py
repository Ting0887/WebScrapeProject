from bs4 import BeautifulSoup
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import create_session, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")


def build_daai_end_date(days_back=1):
    import datetime

    target_date = datetime.datetime.today() - datetime.timedelta(days=days_back)
    return target_date.strftime('%Y/%m/%d')

def scrape_link(session, end_date):
    page = 1
    urls = []
    while True:
        url = f'https://daaimobile.com/api/news?size=500&page={page}&order=createdAt&desc=true&detail=undefined&onShelf=true'
        try:
            r = session.get(url, timeout=20).json()['rows']
            if not r:
                break

            last_date_time = ''
            for item in r:
                title = item['title']
                date_time = item['createdAt'][0:10].replace('-', '/')
                last_date_time = date_time
                link = 'https://daaimobile.com/news/'+item['_id']
                if date_time < end_date:
                    break
                else:
                    print(link)
                    urls.append((title,link,date_time))
            if last_date_time and last_date_time < end_date:
                break
            else:
                page += 1
        except Exception as e:
            print(e)
    if len(urls)!=0:
        scrape_content(urls)

def scrape_content(session, urls):
    data_collect = []
    for item in urls:
        title = item[0]
        link = item[1]
        date_time = item[2]
        try:
            res = session.get(link, timeout=20)
        except Exception:
            continue
        soup = BeautifulSoup(res.text,'lxml')
        try:
            content = soup.find('div','description').text.replace('\n','').strip()
        except Exception:
            content = ''

        data_collect.append({'date_time':date_time,'title':title,
                             'label':'即時新聞','link':link,
                             'content':content,'keyword':''})
    if len(data_collect)!=0:
        write_to_json(data_collect)

def write_to_json(data_collect):
    file_path = write_json_records(
        records=data_collect,
        source_name='Daai',
        category='realtime',
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='Daai',
    )
    print(f"saved: {file_path}")

if __name__ == '__main__':
    session = create_session()
    end_date = build_daai_end_date(days_back=1)
    scrape_link(session, end_date)
