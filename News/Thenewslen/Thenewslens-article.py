from bs4 import BeautifulSoup
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import create_session, ensure_dir, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def scrape_link(session, category, end_date):
    urls = []
    page = 1
    while True:
        page_link = f'https://www.thenewslens.com/category/{category}?page={page}'
        res = session.get(page_link, timeout=20)
        soup = BeautifulSoup(res.text,'lxml')
        print(page_link)
        all_containers = set(soup.select('.list-container'))
        sponsored_containers = set(soup.select('.sponsoredd-container'))
        containers = all_containers - sponsored_containers
        date_time = ''

        for item in containers:
            link = item.find('a')['href'] 
            if '/feature/' in link:
                continue
            date_time = item.find('span','time').text.replace('|','').replace('/','-').strip()
            if len(date_time)!=10:
                continue
            print(date_time)
            if date_time < end_date:
                break
            else:
                urls.append(link)
                print(link)
        if date_time < end_date:
            break
        else:
            page += 1

    if len(urls)!=0:
        write_to_txt(category,urls)
        scrape_content(session, category, urls)

def write_to_txt(category,urls):
    import datetime

    folder_path = os.path.join(OUTPUT_BASE_DIR, 'TheNewsLens', 'urls', datetime.datetime.today().strftime('%Y-%m'))
    ensure_dir(folder_path)
    filename = f'tnl-{category}-'+ datetime.datetime.today().strftime('%Y-%m-%d') + '.txt'
    with open(folder_path+'/'+filename,'w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url+'\n')
    txtf.close()

def scrape_content(session, category, urls):
    data_collect = []
    for url in urls:
        try:
            soup = BeautifulSoup(session.get(url, timeout=20).text,'lxml')
            title = soup.find(class_='article-title').text.strip()
            info = soup.find(class_='article-info').text.strip().split(', ')
            date = info[0]
            if 'Sponsored' in date:
                continue
            label = info[1]

            summary = soup.find(class_='WhyNeedKnow').p.text.strip()
            content = ''.join(p.text for p in soup.select('.article-content > p'))
            # Not all articles have tags/keywords
            keywords = []
            try:
                for a in soup.find(class_='tags').select('a'):
                    keywords.append(a.text)
            except Exception:
                pass
            article = {'url':url,'title':title,'date':date,
                       'label':label,'summary':summary,
                       'content':content,'keywords':keywords}
            data_collect.append(article)
        except Exception as e:
            print(e)
            pass

    if len(data_collect)!=0:
        write_to_json(category,data_collect)

def write_to_json(category,data_collect):
    file_path = write_json_records(
        records=data_collect,
        source_name='TheNewsLens',
        category=category,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='tnl',
    )
    print(f"saved: {file_path}")

if __name__ == '__main__':
    import datetime

    session = create_session()
    end_date = (datetime.datetime.today() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    print(end_date)
    categories = ['world','china','health',
                  'lifestyle','politics','economy',
                  'society','science','tech']

    for category in categories:
        scrape_link(session, category, end_date)

