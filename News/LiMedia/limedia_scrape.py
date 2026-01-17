from selenium import webdriver
import os
import time
import datetime
from bs4 import BeautifulSoup
import json
import requests

def scrape_link(cate,url,folder):
    js = 'window.scrollTo(0, document.body.scrollHeight)'
    last_height = browser.execute_script("return document.body.scrollHeight")
    browser.get(url)
    while True:
        browser.execute_script(js)
        time.sleep(2)
        soup = BeautifulSoup(browser.page_source,'lxml')
        bar = soup.find_all('div','td-ss-main-content')[0].find_all('div','td-block-span6')

        for item in bar:
            try:
                date_time = item.find('time').text
            except:
                pass
        time.sleep(3)
        if date_time < end_date:
            break

        #if scroll down to bottom
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
             break
        last_height = new_height
        
    newsdata = []
    soup = BeautifulSoup(browser.page_source,'lxml')
    bar = soup.find_all('div','td-ss-main-content')[0].find_all('div','td-block-span6')
    for item in bar:
        title = item.find('h3').text
        author = item.find('span','td-post-author-name').text.replace('-','')
        date_time = item.find('time').text
        link = item.find('h3').a.get('href')
        print(link)
        if date_time < end_date:
            break
        else:
            newsdata.append((title,author,date_time,link))
    if len(newsdata)!=0:
        scrape_content(newsdata)
    
def scrape_content(newsdata):
    article = []
    for item in newsdata:
        title = item[0]
        author = item[1]
        date_time = item[2]
        link = item[3]
        res = requests.get(link,headers=headers)
        time.sleep(2)
        soup = BeautifulSoup(res.text,'lxml')
        content = ''
        try:
            contents = soup.find_all('p')
            for c in contents:
                content += c.text.replace('\n','').replace('\r','')
        except:
            print('no content')

        keyword = ''
        try:
            keywords = soup.find_all('div','td-post-source-tags')[0].find_all('a')
            for k in keywords:
                keyword += k.text + ' '
        except:
            print('no keyword')

        article.append({'title':title,'author':author,
                        'date_time':date_time,'label':cate,
                        'link':link,'content':content,
                        'keyword':keyword})
    if len(article)!=0:
        write_to_json(article)

def write_to_json(article):
    folder_path = f'/home/ftp_246/data_1/news_data/limedia/{folder}/'+ time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    filename = 'limedia_'+folder+time.strftime('%Y%m%d')+'.json'
    with open(folder_path+'/'+filename,'w',encoding='utf-8')  as jf:
        json.dump(article,jf,ensure_ascii=False,indent=2)
    jf.close()

if __name__ == '__main__':
    #headers
    headers = {"referer": "https://www.limedia.tw/",
            "cookie":"_ga=GA1.2.2123242271.1631784474; _gid=GA1.2.1716343220.1631784474; _gat=1",
               "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"}
     #Start date,End date
    start_date = datetime.datetime.today() #today
    months = datetime.timedelta(days=1)  #last month
    end_date = (start_date - months).strftime('%Y-%m-%d')
    print(end_date)

    #driver path
    driverPath = '/home/cdna/chromedriver'
    #chromedriver setting
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    # if you don't want to open browser, add 18th line
    chrome_options.add_argument("--headless")

    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option('prefs', prefs)
    prefs = {'profile.managed_default_content_settings.images':2, 'disk-cache-size': 4096, 'intl.accept_languages': 'en-US'}
    chrome_options.add_argument('--dns-prefetch-disable')
    #chrome_options.add_argument('disable-infobars')
    chrome_options.add_argument('blink-settings=imagesEnabled=false')
    #chrome_options.add_argument("--disable-javascript")
    #chrome_options.add_argument("--disable-images")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--in-process-plugins")
    chrome_options.add_argument('--no-sandbox')

    ua = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"
    chrome_options.add_argument("user-agent={}".format(ua))
    browser = webdriver.Chrome(driverPath,options=chrome_options)
    time.sleep(3)

    cate_url = [('大學社會責任','https://www.limedia.tw/category/usr/','society'),
                ('傳播','https://www.limedia.tw/category/comm/','comm'),
                ('科技','https://www.limedia.tw/category/tech/','tech'),
                ('藝文','https://www.limedia.tw/category/art/','art')]

    for cate,url,folder in cate_url:
        scrape_link(cate,url,folder)
    browser.close()

