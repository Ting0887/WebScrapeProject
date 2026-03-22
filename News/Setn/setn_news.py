import datetime
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import create_session, get_soup, join_text, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def build_setn_end_date(days_back=1):
    target_date = datetime.datetime.today() - datetime.timedelta(days=days_back)
    return target_date.strftime('%Y/%m/%d')


def Setn(session, url, cate, end_date):
    article = []
    # total 20 pages
    for num in range(1,21):
        page_url = url+ '&p=' + str(num)
        print(page_url)
        try:
            soup = get_soup(session, page_url, sleep_seconds=0.2)
        except Exception as error:
            print(f"skip list page by request error: {error}")
            break

        items = soup.find_all('div','col-sm-12 newsItems')
        if not items:
            break

        last_date_time = ''
        for item in items:
            label = extract_label(item)
            title = extract_title(item)
            link = extract_link(item)
            if not link:
                continue
            
            try:
                detail_soup = get_soup(session, link, sleep_seconds=0.2)
            except Exception as error:
                print(f"skip article by request error: {error}")
                continue

            date_time = extract_date(detail_soup)
            content = extract_content(detail_soup)
            keyword = extract_keyword(detail_soup)
            last_date_time = date_time
            if not date_time:
                continue
            
            if date_time < end_date:
                break
            else:
                article.append({'date_time':date_time,'title':title,'label':label,
                                'link':link,'content':content,'keyword':keyword})
        if last_date_time and last_date_time < end_date:
            break
    
    if len(article)!=0:
        file_path = write_json_records(
            records=article,
            source_name='Setn',
            category=cate,
            base_output_dir=OUTPUT_BASE_DIR,
            file_prefix='setn',
        )
        print(f"saved: {file_path}")

def extract_label(item):
    #label
    try:
        label = item.find('a').text
    except Exception:
        label = ''
    return label

def extract_title(item):
    #title
    try:
        title = item.find('h3','view-li-title').text
    except Exception:
        title = ''
    return title

def extract_link(item):
    #link
    try:
        link = 'https://www.setn.com' + item.find('h3','view-li-title').a.get('href')
    except Exception:
        link = ''
    return link

def extract_date(soup):
    try:
        date_time = soup.find('time','page-date').text
    except Exception:
        date_time = ''
    return date_time

def extract_content(soup):
    try:
        contents = soup.select('article')[0].find_all('p')
        content = join_text(contents).replace('\n','').replace('\r','')
    except Exception:
        content = ''
    return content
            
def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','keyword page-keyword-area')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except Exception:
        pass
    return keyword
    
if __name__ == '__main__':
    end_date = build_setn_end_date(days_back=1)
    session = create_session()

    cates = {('politics','6'),('society','41'),('global','5'),
            ('life','4'),('health','65'),('finance','2'),('technology','7')}

    for cate,cate1 in cates:
        url = f'https://www.setn.com/ViewAll.aspx?PageGroupID={cate1}'
        Setn(session, url, cate, end_date)
