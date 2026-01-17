import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import os
import json
import time
import datetime


def scrape_link(category,label):
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
        scrape_content(category,urls)

def write_to_txt(label,urls):
    #bulid folder yyyy-mm
    folder_path =  '/home/ftp_246/data_1/news_data/CTS/urls/' + time.strftime('%Y-%m') 
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    with open(folder_path + '/'+f'cts-{label}-urls_'+time.strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url+'\n')
    txtf.close()

def scrape_content(category,urls):
    data_collect = []
    for url in urls:
        res = requests.get(url)
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
    write_to_json(data_collect)

def write_to_json(data_collect):
    #bulid folder yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/CTS/json/{label}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = 'cts-'+label+'-'+time.strftime('%Y-%m-%d')+'.json'
    with open(folder_path + '/' + filename,'w',encoding='utf-8') as jf:
        json.dump(data_collect,jf,ensure_ascii=False,indent=2)
    jf.close()
    
if __name__ == '__main__':
    start_date = datetime.datetime.today() #today
    months = datetime.timedelta(days=1)  #last month
    end_date = (start_date - months).strftime('%Y%m%d')
    print(end_date)

    driverPath = '/home/cdna/chromedriver'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--no-sandbox')
    browser = webdriver.Chrome(driverPath,options=chrome_options)

    categories = [
                    ("政治" , "politics"),
                    ("國際" , "international"),
                    ("社會" , "society"),
                    ("生活" , "life"),
                    ("財經" , "money"),
                 ]

    for category, label in categories:
        scrape_link(category,label)
