import os
import datetime
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, get_soup, join_text, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")


def scrape_link(session, cate, url, folder, end_date):
    newsdata = []
    page = 1
    while True:
        page_url = url + '/page/' + str(page)
        print(page_url)
        try:
            soup = get_soup(session, page_url, sleep_seconds=0.3)
        except Exception as error:
            print(f"skip page by request error: {error}")
            break

        bar = soup.find_all('div',{'role':'main'})[0].find_all('li')
        date_time = ''
        for item in bar:
            try:
                title = item.find('h2','post-title').text
            except Exception:
                title = ''
            try:
                link = item.find('h2','post-title').a['href']
            except Exception:
                link = ''
            try:
                date_time = link.split('/')[-3]
                date_time = datetime.datetime.strptime(date_time,'%Y%m%d').strftime('%Y-%m-%d')
            except Exception:
                date_time = ''
            if date_time < end_date:
                break
            elif link !='':
                newsdata.append((title,link,date_time))
            print(link)
        if date_time and date_time < end_date:
            break
        else:
            page += 1
        
        #if end page
        mes = soup.find('div',{'role':'main'}).text
        if 'That page can’t be found' in mes:
            break
    if len(newsdata)!=0:
        scrape_content(session, cate, folder, newsdata)

def scrape_content(session, cate, folder, newsdata):
    article = []
    for item in newsdata:
        title = item[0]
        link = item[1]
        date_time = item[2]

        try:
            soup = get_soup(session, link, sleep_seconds=0.2)
        except Exception as error:
            print(f"skip article by request error: {error}")
            continue

        content = ''
        try:
            contents = soup.find_all('div',{'itemprop':'articleBody'})[0].find_all('p')
            content = join_text(contents)
        except Exception:
            print('no content')
        keyword = ''
        try:
            keywords = soup.find_all('div','post-bottom-meta post-bottom-tags')[0].find_all('a')
            keyword = ' '.join(k.text for k in keywords)
        except Exception:
            print('no keyword')

        article.append({'title':title,
                        'date_time':date_time,
                        'label':cate,
                        'link':link,
                        'content':content,
                        'keyword':keyword})
    if len(article)!=0:
        file_path = write_json_records(
            records=article,
            source_name='4wayvoice',
            category=folder,
            base_output_dir=OUTPUT_BASE_DIR,
            file_prefix='4wayvoice',
        )
        print(f"saved: {file_path}")

if __name__ == '__main__':
    end_date = build_end_date(days_back=1)
    print(end_date)
    session = create_session()
    
    cates = [('從四方看世界','https://4wayvoice.nownews.com/news/category/top-news-ch/4w-taiwan-ch/%E5%BE%9E%E5%9B%9B%E6%96%B9%E7%9C%8B%E4%B8%96%E7%95%8C','world'),
            ('從四方看亞洲','https://4wayvoice.nownews.com/news/category/top-news-ch/4w-taiwan-ch/%e5%be%9e%e5%9b%9b%e6%96%b9%e7%9c%8b%e4%ba%9e%e6%b4%b2/','asia'),
            ('從四方看臺灣','https://4wayvoice.nownews.com/news/category/top-news-ch/4w-taiwan-ch/%e5%be%9e%e5%9b%9b%e6%96%b9%e7%9c%8b%e8%87%ba%e7%81%a3/','taiwan')]
    for cate,url,folder in cates:
        scrape_link(session, cate, url, folder, end_date)
