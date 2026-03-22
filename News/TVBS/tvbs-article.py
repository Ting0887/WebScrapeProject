import datetime
import os
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import create_session, get_soup, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def scrape_link(session, start_date, end_date, label, category):
    urls = []
    current_date = start_date
    while str(current_date) > end_date:
        page_link = f'https://news.tvbs.com.tw/realtime/{category}'+'/'+str(current_date.strftime('%Y-%m-%d'))
        try:
            soup = get_soup(session, page_link, sleep_seconds=0.2)
        except Exception as error:
            print(f"skip list page by request error: {error}")
            break

        print(page_link)
        for item in soup.find_all('li'):
            try:
                title = item.find('h2').text
                link = 'https://news.tvbs.com.tw'+item.find('a')['href']
                print(link)
                urls.append((title,link))
            except Exception:
                pass
        current_date -= datetime.timedelta(days=1)
    if len(urls)!=0:
        write_to_txt(category,urls)
        scrape_content(session, label, category, urls)

def write_to_txt(category,urls):
    folder_path =  '/home/ftp_246/data_1/news_data/TVBS/urls/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    with open(folder_path + '/'+f'tvbs-{category}-urls_'+time.strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url[1]+'\n')
    txtf.close()

def scrape_content(session, label, category, urls):
    data_collect = []
    for item in urls:
        title = item[0]
        url = item[1]
        
        try:
            soup = get_soup(session, url, sleep_seconds=0.2)
        except Exception as error:
            print(f"skip article by request error: {error}")
            continue
        
        author_box = soup.find(class_='author')
        if not author_box:
            continue
        datestr = author_box.text
        if '最後更新時間' in datestr:
            date = datestr.split('最後更新時間：')[1].strip()
        else:
            date = datestr.split('發佈時間：')[1].strip()

        stopstrings = ['&nbsp',
                       '最HOT話題在這！想跟上時事，快點我加入TVBS新聞LINE好友！',
                       '～開啟小鈴鐺',
                       'TVBS YouTube頻道',
                       '新聞搶先看',
                       '快點我按讚訂閱',
                       '～',
                       '55直播線上看',
                       '現正直播']
        content_box = soup.find(class_='article_content')
        if not content_box:
            continue
        content = ''.join(s for s in content_box.stripped_strings if s not in stopstrings)

        keywords = []
        try:
            keyword_box = soup.select_one('.article_keyword')
            if keyword_box:
                keywords = [a.text.lstrip('#') for a in keyword_box.find_all('a')]
        except Exception:
            pass
        article = {'url':url,'title':title,'date':date,'label':label,'content':content,'keywords':keywords}
        print(article)
        data_collect.append(article)
    if len(data_collect)!=0:
        file_path = write_json_records(
            records=data_collect,
            source_name='TVBS',
            category=category,
            base_output_dir=OUTPUT_BASE_DIR,
            file_prefix='tvbs',
        )
        print(f"saved: {file_path}")


if __name__ == '__main__':
    start_date = datetime.datetime.strptime(time.strftime('%Y-%m-%d'),'%Y-%m-%d')
    oneday = datetime.timedelta(days=1)
    end_date = (start_date - oneday).strftime('%Y-%m-%d')
    print(start_date)
    session = create_session()
    categories = [('要聞', 'politics'),
                  ('社會', 'local'),
                  ('全球', 'world'),
                  ('健康', 'health'),
                  ('理財', 'money'),
                  ('科技', 'tech'),
                  ('生活', 'life')]
    for label,category in categories:
        scrape_link(session, start_date, end_date, label, category)
