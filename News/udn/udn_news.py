import datetime
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import create_session, get_soup, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def build_udn_end_date(days_back=1):
    target_date = datetime.datetime.today() - datetime.timedelta(days=days_back)
    return target_date.strftime('%Y-%m-%d %H:%M')


def scrape_health(session, health_cate, end_date):
    data_collect = []
    page = 1
    while True:
        url = 'https://health.udn.com/rank/newest/1005/' + str(page)
        print(url)
        try:
            soup = get_soup(session, url, sleep_seconds=0.2)
        except Exception as error:
            print(f"skip health list page by request error: {error}")
            break

        tbody = soup.find_all('tbody')
        if not tbody:
            break
        items = tbody[0].find_all('tr')[1:]
        if not items:
            break

        page += 1
        last_date_time = ''
        for item in items:
            try:
                title = item.find('a').text
                label = item.find('td','only_web').text
                link = item.find('a')['href']
                detail_soup = get_soup(session, link, sleep_seconds=0.2)
                
                author_box = detail_soup.find('div','shareBar__info--author')
                if not author_box or not author_box.span:
                    continue
                date_time = author_box.span.text
                author = author_box.text.replace(date_time,'')
                last_date_time = date_time
                
                content = ''
                try:
                    contents = detail_soup.find_all('p')
                    for c in contents:
                        content += c.text
                except Exception:
                    continue

                keyword = ''
                try:
                    keywords = detail_soup.find_all('dl','tabsbox')[0].find_all('a')
                    for k in keywords:
                        keyword += k.text + ' '
                except Exception:
                    print('no keyword')
                if date_time < end_date:
                    break
                article = {'title':title,'date_time':date_time,
                           'author':author,'link':link,
                           'label':label,'content':content,
                           'keyword':keyword}
                print(article)
                data_collect.append(article)
            except Exception:
                pass
        if last_date_time and last_date_time < end_date:
            break

    if len(data_collect)!=0:
        write_to_json(health_cate, data_collect)
        
def scrape_finance_url(session, finance_cate, end_date):
    urls = []
    for category,cate_id,sub_id in finance_cate:
        page = 0
        while True:
            try:
                page_link = f'https://udn.com/api/more?page={page}&channelId=2\
                               &type=subcate_articles&cate_id={cate_id}&sub_id={sub_id}'
                res = session.get(page_link, timeout=20)
                res.raise_for_status()
                print(page_link)
                lists = res.json().get('lists', [])
                if not lists:
                    break
                last_date_time = ''
                for item in lists:
                    title = item['title']
                    link = 'https://udn.com/news' + item['titleLink'].replace('//story','/story')
                    date_time = item['time']['date']
                    last_date_time = date_time
                    if date_time < end_date:
                        break
                    print(link)
                    urls.append((title,link,date_time))
                if last_date_time and last_date_time < end_date:
                    break
                else:
                    page += 1
            except Exception as error:
                print(error)
                break
    if len(urls)!=0:
        scrape_content(session, 'finance', urls)

def scrape_link(session, category, cate_id, sub_id, end_date):
    urls = []
    page = 1
    while True:
        try:
            page_link = f'https://udn.com/api/more?page={page}&channelId=2\
                        &type=subcate_articles&cate_id={cate_id}&sub_id={sub_id}'
            res = session.get(page_link, timeout=20)
            res.raise_for_status()
            print(page_link)
            lists = res.json().get('lists', [])
            if not lists:
                break
            last_date_time = ''
            for item in lists:
                title = item['title']
                link = 'https://udn.com/news' + item['titleLink'].replace('//story','/story')
                date_time = item['time']['date']
                last_date_time = date_time
                if date_time < end_date:
                    break
                print(link)
                urls.append((title,link,date_time))
            if last_date_time and last_date_time < end_date:
                break
            else:
                page += 1
        except Exception as error:
            print(error)
            break

    if len(urls)!=0:
        scrape_content(session, category, urls)

def scrape_content(session, category, urls):
    data_collect = []
    for item in urls:
        
        link = item[1]
        title = item[0]
        date_time = item[2]

        try:
            soup = get_soup(session, link, sleep_seconds=0.2)
        except Exception as error:
            print(f"skip article by request error: {error}")
            continue

        try:
            author = soup.find('span','article-content__author').text.strip()
        except Exception:
            author = ''

        content = ''
        try:
            contents = soup.find_all('section','article-content__editor')[0].find_all('p')
            for c in contents:
                content += c.text.replace('\n','').replace('\r','').replace('\t','')
        except Exception:
            continue
        try:
            label = soup.select('.article-content__info')[0].find_all('a')[-1].text
        except Exception:
            label = ''

        keyword = ''
        try:
            keywords = soup.find_all('section','keywords')[0].find_all('a')
            for k in keywords:
                keyword += k.text + ' '
        except Exception:
            pass
        
        if label != '':
            article = {'date_time':date_time,'title':title,'link':link,
                       'author':author,'label':label,'content':content,'keyword':keyword}
            print(article)
            data_collect.append(article)
    if len(data_collect)!=0:
        write_to_json(category, data_collect)

def write_to_json(category,data_collect):
    file_path = write_json_records(
        records=data_collect,
        source_name='udn',
        category=category,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='udn',
    )
    print(f"saved: {file_path}")

if __name__ == '__main__':
    end_date = build_udn_end_date(days_back=1)
    print(end_date)
    session = create_session()

    categories = [('politics','6638','6656'),
                  ('society','6639','7320'),
                  ('global','7225','6809'),
                  ('life','6649','7266'),
                  ('tech','6644','7240'),]

    finance_cate = [('finance','6644','7238'),
                    ('finance','6644','7239'),
                    ('finance','6644','7243'),
                    ('finance','6644','7241'),
                    ('finance','6644','121591')]

    for category,cate_id,sub_id in categories:
        scrape_link(session, category, cate_id, sub_id, end_date)

    scrape_finance_url(session, finance_cate, end_date)
    
    health_cate = 'health'
    scrape_health(session, health_cate, end_date)



