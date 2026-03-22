from bs4 import BeautifulSoup
import datetime
import os
import sys
from selenium import webdriver
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, get_soup, join_text, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")


def Appledaily(session, browser, url, cate, cate1, end_date):
    article = []
    base_url = url + cate1
    browser.get(base_url)
    js_down = 'window.scrollTo(0, document.body.scrollHeight)'
    soup = BeautifulSoup(browser.page_source,'lxml')
    post = soup.find_all('div','text-container box--margin-left-md box--margin-right-md')
    last_height = browser.execute_script("return document.body.scrollHeight")
    while len(post) < 80:
        browser.execute_script(js_down)
        time.sleep(2.5)
        soup = BeautifulSoup(browser.page_source,'lxml')
        post = soup.find_all('div','text-container box--margin-left-md box--margin-right-md')
        print(len(post))
        #if scroll down to bottom
        
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
	
    list_wrap = soup.find_all('div', 'article-list-container')
    if not list_wrap:
        return
    items = list_wrap[0].find_all('div','flex-feature')
    if not items:
        return

    last_date_time = ''
    for item in items:
        date_time = extract_date(item)
        title = extract_title(item)
        link = extract_link(item)
        last_date_time = date_time
        if not date_time or not link:
            continue

        try:
            soup = get_soup(session, link, sleep_seconds=0.2)
        except Exception as error:
            print(f"skip article by request error: {error}")
            continue

        content = extract_content(soup)
        keyword = extract_keyword(soup)
        if date_time < end_date:
            break
        else:
            article.append({'date_time':date_time,'title':title,'link':link,
                            'label':cate,'content':content,'keyword':keyword})
            print(article)

    if last_date_time and last_date_time < end_date:
        print("reach end date for Appledaily")
    if len(article)!=0:
        outputjson(cate1, article)

def extract_date(item):
    try:
        date_time = item.find('div','timestamp').text.replace('出版時間: ','').strip()
    except Exception:
        date_time = ''
    return date_time

def extract_title(item):
    try:
        title = item.find('span','headline truncate truncate--3').text
    except Exception:
        title = ''
    return title

def extract_link(item):
    try:
        link = 'https://tw.appledaily.com' + item.find('a')['href']
    except Exception:
        link = ''
    return link

def extract_content(soup):
    try:
        contents = soup.find_all('div',{'id':'articleBody'})[0].find_all('p')
        content = join_text(contents)
    except Exception:
        content = ''
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','box--position-absolute-center ont-size--16 box--display-flex flex--wrap tags-container')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except Exception:
        pass
    return keyword

def outputjson(cate1, article):
    file_path = write_json_records(
        records=article,
        source_name='Appledaily',
        category=cate1,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='apple',
    )
    print(f"saved: {file_path}")
        
if __name__ == '__main__':
    end_date = build_end_date(days_back=1).replace('-', '/')

    driverPath = '/home/cdna/chromedriver'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    #chrome_options.add_argument('blink-settings=imagesEnabled=false') 
    #chrome_options.add_argument("--disable-javascript") 
    #chrome_options.add_argument("--disable-images")
    #chrome_options.add_argument('--disable-gpu')
    #chrome_options.add_argument("--disable-plugins")
    #chrome_options.add_argument("--in-process-plugins")
    browser = webdriver.Chrome(driverPath,options=chrome_options)
    session = create_session()
    cates = [('政治','politics'),('國際','international'),
             ('社會','local'),('生活','life'),('娛樂時尚','entertainment'),
             ('財經地產','property'),('3C車市','gadget'),]
    url = 'https://tw.appledaily.com/realtime/'
    for cate,cate1 in cates:
        Appledaily(session, browser, url, cate, cate1, end_date)
    browser.quit()
