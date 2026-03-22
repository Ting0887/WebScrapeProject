from bs4 import BeautifulSoup
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, ensure_dir, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def scrape_link(session, label, category, end_date):
    urls = []
    page = 1
    while True:
        page_link = f"https://news.ttv.com.tw/category/{label}/{page}"
        res = session.get(page_link, timeout=20)
        print(page_link)
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.select('.news-list li')
        date = ''

        for item in items:
            link = item.find('a')['href']
            date = item.find('div','time').text.replace('.','-')
            print(link)
            print(date)

            if date < end_date:
                break
            else:
                urls.append(link)
        if date < end_date:
            break
        page += 1
    if len(urls)!=0:
        write_to_txt(category,urls)
        scrape_content(session, category, urls)

def write_to_txt(category,urls):
    import datetime

    folder_path = os.path.join(OUTPUT_BASE_DIR, 'TTV', 'urls', datetime.datetime.today().strftime('%Y-%m'))
    ensure_dir(folder_path)

    with open(folder_path + '/'+f'ttv-{category}-urls_'+datetime.datetime.today().strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url+'\n')
    txtf.close()

def scrape_content(session, category, urls):
    data_collect = []
    for url in urls:
        try:
            res = session.get(url, timeout=20)
            res.encoding = 'utf8'
            soup = BeautifulSoup(res.text,'lxml')

            title = soup.find('h1').text.strip()
            date = soup.find(class_='date time').text.strip()
            newslabel = soup.find('div', {'id': 'crumbs'}).find_all('li')[1].text
            content = soup.find('div', {'id': 'newscontent'}).text.strip()
            keywords = []
            try:
                keywords = [a.text for a in soup.select('.news-status > .tag > li')]
            except Exception:
                pass
            article = {'url':url,'title':title,'date':date,
                       'label':newslabel,'content':content,'keywords':keywords}
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
        source_name='TTV',
        category=category,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='ttv',
    )
    print(f"saved: {file_path}")

if __name__ == '__main__':
    session = create_session()
    end_date = build_end_date(days_back=1)

    categories = [('政治', 'politics'),
                  ('財經', 'finance'),
                  ('社會', 'society'),
                  ('國際', 'world'),
                  ('生活', 'life'),
                  ('健康', 'health')]

    for label,category in categories:
        scrape_link(session, label, category, end_date)
