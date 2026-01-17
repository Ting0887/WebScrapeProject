import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import json
import datetime
import os

def Daai(url):
    num = 1
    article = []
    while True:
        base_url = url + cate1 + '?p=' + str(num)
        browser.get(base_url)
        time.sleep(1)
        soup = BeautifulSoup(browser.page_source)
        items = soup.find_all('div',{'style':'display:none'})[0].find_all('a')
        for item in items:
            link = item.get('href')
            browser.get(link)
            soup = BeautifulSoup(browser.page_source)
            try:
                title = soup.find('div','modal-title').h1.text
            except:
                title = ''
            try:
                date_time = soup.find('div','news-modal-airtime').span.text
            except:
                date_time = ''
            
            label = cate
            
            try:
                content = soup.find('p').text.strip()
            except:
                content = ''
            
            keyword = ''
            if date_time < end_date:
                break
            else:
                article.append({'date_time':date_time,
                                'title':title,
                                'label':label,
                                'link':link,
                                'content':content,
                                'keyword':keyword})
        if date_time < end_date:
            break
        else:
            num += 1
    if len(article)!=0:
        write_to_json(article)

def write_to_json(article):
    #bulid folder by yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/Daai/{cate1}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = 'Daai_' + cate1 + time.strftime('%Y%m%d') + '.json'
    with open(folder_path + '/' + filename,'w',encoding='utf8') as f:
        json.dump(article,f,ensure_ascii=False,indent=2)
    f.close()
    
if __name__ == '__main__':
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days = 1)
    end_date = (start_date - d).strftime('%Y-%m-%d')
    
    cates = [('生活要聞','life'),
             ('國際新聞','international')]
    
    #chromedriver setting
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--dns-prefetch-disable')
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_argument('blink-settings=imagesEnabled=false') 
    chrome_options.add_argument("--disable-javascript") 
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--in-process-plugins")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--headless")
    
    driverPath = '/home/tingyang0518/chromedriver'
    browser = webdriver.Chrome(driverPath,chrome_options=chrome_options)
    
    url = 'https://www.daai.tv/news/'
    for cate,cate1 in cates:
        Daai(url)
