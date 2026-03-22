from bs4 import BeautifulSoup
import os
import sys
import time
import datetime
from selenium import webdriver
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_chrome_browser, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def Chinatime(browser, cate, cate1, mydir, url, end_date):
    num = 1
    urls = []
    while True:
        if 'realtimenews' in cate1:
            base_url = url + cate1 + '/?page='+ str(num) +'&chdtv'
        else:
            base_url = url + cate1 + '/total?page=' + str(num) + '&chdtv'
        print(base_url)
        try:
            browser.get(base_url)
        except Exception:
            continue
        time.sleep(1.5)
        soup = BeautifulSoup(browser.page_source,'lxml')
        list_wrap = soup.find_all('ul', 'vertical-list list-style-none')
        if not list_wrap:
            break
        items = list_wrap[0].find_all('div','row')
        if len(items) < 10:
            break

        last_date_time = ''
        for item in items:
            title = extract_title(item)
            date_time = extract_date(item)
            link = extract_link(item)
            last_date_time = date_time
            if 'beap.gemini' not in link:
                print(link)
                urls.append((title,link,date_time))
        if last_date_time and last_date_time < end_date:
            break
        else:
            num += 1

    scrape_article(browser, cate, mydir, urls)

def extract_title(item):
    try:
        title = item.find('h3','title').text
    except Exception:
        title = ''
    return title

def extract_date(item):
    try:
        date_time = item.find('time')['datetime']
    except Exception:
        date_time = ''
    return date_time 

def extract_link(item):
    try:
        link =  'https://www.chinatimes.com' + item.find('h3','title').a.get('href')
    except Exception:
        link = ''
    return link

def scrape_article(browser, cate, mydir, urls):
    article = []
    for item in urls:
        title = item[0]
        link = item[1]
        date_time = item[2]

        browser.get(link)
        time.sleep(0.5)
        soup = BeautifulSoup(browser.page_source,'lxml')
        content = extract_content(soup)
        keyword = extract_keyword(soup)
        article.append({'date_time':date_time,'title':title,'link':link,
                        'label':cate,'content':content,'keyword':keyword})

    if len(article)!=0:
        write_to_json(mydir, article)

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div','article-body')[0].find_all('p')
        for c in contents:
            content += c.text
    except Exception:
        pass
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','article-hash-tag')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except Exception:
        pass
    return keyword

def write_to_json(mydir, article):
    file_path = write_json_records(
        records=article,
        source_name='ChinaTimes',
        category=mydir,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='chinatimes',
    )
    print(f"saved: {file_path}")
    
if __name__ == '__main__':
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--no-sandbox')
    browser = create_chrome_browser(chrome_options)

    end_date = build_end_date(days_back=1)
     
    cates = [('政治','politic','politics'),('國際','world','global'),
             ('社會','society','society'),('生活','life','life'),
             ('財經','money','finance'),('健康','health','health'),
             ('科技','technologynews','tech'),('即時新聞','realtimenews','realtime')]
    
    url = 'https://www.chinatimes.com/'
    for cate,cate1,mydir in cates:  
        Chinatime(browser, cate, cate1, mydir, url, end_date)
    browser.close()
