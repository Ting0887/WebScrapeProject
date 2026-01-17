import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
import time
import os
import datetime

def Appledaily(url):
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
	
    items = soup.find_all('div','article-list-container')[0].find_all('div','flex-feature')
    for item in items:
        date_time = extract_date(item)
        title = extract_title(item)
        link = extract_link(item)
        browser.get(link)
        soup = BeautifulSoup(browser.page_source,'lxml')
        time.sleep(1)
        content = extract_content(soup) 
        keyword = extract_keyword(soup)
        if date_time < end_date:
            break
        else:
            article.append({'date_time':date_time,'title':title,'link':link,
                            'label':cate,'content':content,'keyword':keyword})
            print(article)
    if len(article)!=0:
        outputjson(article)

def extract_date(item):
    try:
        date_time = item.find('div','timestamp').text.replace('出版時間: ','').strip()
    except:
        date_time = ''
    return date_time

def extract_title(item):
    try:
        title = item.find('span','headline truncate truncate--3').text
    except:
        title = ''
    return title

def extract_link(item):
    try:
        link = 'https://tw.appledaily.com' + item.find('a')['href']
    except:
        link = ''
    return link

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div',{'id':'articleBody'})[0].find_all('p')
        for c in contents:
            content += c.text
    except:
        pass
    return content

def extract_keyword(soup):
    try:
        keyword = ''
        keywords = soup.find_all('div','box--position-absolute-center ont-size--16 box--display-flex flex--wrap tags-container')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except:
        pass
    return keyword

def outputjson(article):
    #bulid folder by yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/Appledaily/{cate1}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    file = 'apple_' + cate1 + time.strftime('%Y%m%d') + '.json'
    with open(folder_path + '/' + file,'w',encoding='utf8') as f:
        json.dump(article,f,ensure_ascii=False,indent=2)
    f.close()
        
if __name__ == '__main__':
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days=1)
    end_date = (start_date - d).strftime('%Y/%m/%d')

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
    cates = [('政治','politics'),('國際','international'),
             ('社會','local'),('生活','life'),('娛樂時尚','entertainment'),
             ('財經地產','property'),('3C車市','gadget'),]
    url = 'https://tw.appledaily.com/realtime/'
    for cate,cate1 in cates:
        Appledaily(url)
    browser.quit()
