import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import os
import time
import datetime
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import create_chrome_browser, create_session, ensure_dir, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")


def scrape_link(browser, session, category, label, end_date):
    urls = []
    js_down = 'window.scrollTo(0, document.body.scrollHeight)'
    last_height = browser.execute_script("return document.body.scrollHeight")
    page_link = f"https://news.cts.com.tw/{label}/index.html"
    browser.get(page_link)
    
    while True:
        browser.execute_script(js_down)
        time.sleep(1.5)
        
        #if scroll down to bottom
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        
        try:
            soup = BeautifulSoup(browser.page_source,'lxml')
            articles = soup.find_all('div','newslist-container flexbox')[0].find_all('a')
            dates = ''
            for article in articles:
                link = article['href']
                dates = link.split('/')[-1].split('.html')[0][0:8]
                print(link)
                if dates < end_date:
                    break
                else:
                    urls.append(link)

            if dates < end_date:
                break
        except Exception as e:
            print(e)
    if len(urls)!=0:
        write_to_txt(label,urls)
        scrape_content(session, category, label, urls)

def write_to_txt(label,urls):
    folder_path = os.path.join(OUTPUT_BASE_DIR, 'CTS', 'urls', time.strftime('%Y-%m'))
    ensure_dir(folder_path)
    with open(folder_path + '/'+f'cts-{label}-urls_'+time.strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url+'\n')
    txtf.close()

def scrape_content(session, category, label, urls):
    data_collect = []
    for url in urls:
        res = session.get(url, timeout=20)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text,'lxml')
        try:
            date = soup.find('time').text
            title = soup.find('h1','artical-title').text
            author = soup.find_all('div','artical-content')[0].find('p').text
            contents = soup.find('div','artical-content').text.replace('\n','').replace('\r','')
            keywords = []
            keyword = soup.find_all('div','news-tag')[0].find_all('a')
            for k in keyword:
                keywords.append(k.text)

            article = {'url':url,'label':category,
                       'contents':contents,'date':date,
                       'keywords':keywords,'author':author,
                       'title':title}
            print(article)
            data_collect.append(article)
        except Exception as e:
            print(e)
            pass
    if len(data_collect) != 0:
        write_to_json(label, data_collect)

def write_to_json(label, data_collect):
    file_path = write_json_records(
        records=data_collect,
        source_name='CTS',
        category=label,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='cts',
    )
    print(f"saved: {file_path}")
    
if __name__ == '__main__':
    start_date = datetime.datetime.today() #today
    months = datetime.timedelta(days=1)  #last month
    end_date = (start_date - months).strftime('%Y%m%d')
    print(end_date)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--no-sandbox')
    browser = create_chrome_browser(chrome_options)
    session = create_session()

    categories = [
                    ("政治" , "politics"),
                    ("國際" , "international"),
                    ("社會" , "society"),
                    ("生活" , "life"),
                    ("財經" , "money"),
                 ]

    for category, label in categories:
        scrape_link(browser, session, category, label, end_date)
