import datetime
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import create_session, get_soup, join_text, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def build_cna_end_date(days_back=1):
    target_date = datetime.datetime.today() - datetime.timedelta(days=days_back)
    return target_date.strftime('%Y/%m/%d')


def parse_cateurl(session, url, cate, cate1, folder, end_date):
    collect_url = []
    page = 5
    for num in range(1,page+1):
        payloads = {"action": "0", "category": cate1, "pagesize": "20", "pageidx": num}
        print(url)
        try:
            res = session.post(url, data=payloads, timeout=20)
            res.raise_for_status()
            r = res.json()
        except Exception as error:
            print(f"skip list page by request error: {error}")
            break

        items = r.get('ResultData', {}).get('Items', [])
        if not items:
            break

        last_date_time = ''
        for item in items:
            date_time = extract_date(item)
            title = extract_title(item)
            link = extract_link(item)
            last_date_time = date_time
            if not date_time or not link:
                continue
            if date_time < end_date:
                break
            else:
                collect_url.append((date_time,title,link))

        if last_date_time and last_date_time < end_date:
            break
    
    if len(collect_url)!=0:
        extract_info(session, collect_url, cate, folder)

def extract_date(item):
    try:
        date_time = item['CreateTime'] #datetime
    except Exception:
        date_time = ''
    return date_time

def extract_title(item):
    try:
        title = item['HeadLine'] #title
    except Exception:
        title = ''
    return title
            
def extract_link(item):
    try:
        link = item['PageUrl'] #link
    except Exception:
        link = ''
    return link

def extract_info(session, collect_url, cate, folder):
    datalist = []
    for item in collect_url:
        date_time = item[0]
        title = item[1]
        link = item[2]
        try:
            soup = get_soup(session, link, sleep_seconds=0.2)
        except Exception as error:
            print(f"skip article by request error: {error}")
            continue

        content = extract_content(soup)
        article= {'date_time':date_time,'title':title,
                  'label':cate,'link':link,
                  'content':content,'keyword':''}
        datalist.append(article)

    if len(datalist)!=0:
        file_path = write_json_records(
            records=datalist,
            source_name='CNA',
            category=folder,
            base_output_dir=OUTPUT_BASE_DIR,
            file_prefix='cna',
        )
        print(f"saved: {file_path}")

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div','paragraph')[0].find_all('p')
        content = join_text(contents)
    except Exception:
        pass
    return content    
        
if __name__ == '__main__':
    end_date = build_cna_end_date(days_back=1)
    
    url = 'https://www.cna.com.tw/cna2018api/api/WNewsList'
    session = create_session(headers={'x-requested-with': 'XMLHttpRequest'})
    cates = [('政治','aipl','politics'),
             ('社會','asoc','society'),
             ('國際','aopl','global'),
             ('生活','ahel','life'),
             ('產經','aie','finance'),
             ('科技','ait','technology'),
             ('證券','asc','finance')]
    for cate,cate1,folder in cates:
        parse_cateurl(session, url, cate, cate1, folder, end_date)
