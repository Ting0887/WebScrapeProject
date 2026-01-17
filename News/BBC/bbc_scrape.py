import os
import time
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
import json
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def scrape_link(cate_id,label,category):
    urls = []
    num = 1
    domain_url = 'https://www.bbc.com/zhongwen/trad/topics/'
    while True:
        url = domain_url + str(cate_id) + '/page/' + str(num)
        browser.get(url)
        print(url)
        time.sleep(1)
        soup = BeautifulSoup(browser.page_source,'lxml')
        bar = soup.find_all('article')
        for item in bar:
            try:
                title = item.find('span','lx-stream-post__header-text gs-u-align-middle').text
            except:
                title = ''
            try:
                link = 'https://www.bbc.com' + item.find('a','qa-heading-link lx-stream-post__header-link')['href']
            except:
                link = ''
            try:
                date_time = item.find('span','qa-post-auto-meta').text
                if len(date_time)>10:
                    date_time = datetime.datetime.strptime(date_time,'%H:%M %B %d, %Y').strftime('%Y-%m-%d')
                else:
                    continue
            except:
                date_time = ''
            print(date_time)

            if date_time < end_date:
                break
            else:
                urls.append((title,link,date_time))
        if date_time < end_date:
            break

        try:
            mes = soup.find('span','gs-u-display-block gs-u-mb qa-no-content-message').text
            if 'Oops! It looks like there is no content' in mes:
                break
        except Exception as e:
            num += 1
            continue

    if len(urls)!=0:
        scrape_content(label,urls)

def scrape_content(label,urls):
    data_collect = []
    for item in urls:
        title = item[0]
        link = item[1]
        date_time = item[2]
        
        res = requests.get(link)
        time.sleep(1)
        soup = BeautifulSoup(res.text,'lxml')

        content = ''
        try:
            contents = soup.find_all('p','bbc-mj7obe e1cc2ql70')
            for c in contents:
                content += c.text
        except:
            pass
        article = {'title':title,
                   'author':'',
                   'date_time':date_time,
                   'label':label,
                   'link':link,
                   'content':content,
                   'keyword':''}
        data_collect.append(article)
    if len(data_collect)!=0:
        write_to_json(data_collect)

def write_to_json(data_collect):
    folder_path = f'/home/ftp_246/data_1/news_data/BBC/{category}/'+time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    file_name = f'bbc_{category}'  + time.strftime('%Y%m%d') + '.json'
    with open(folder_path + '/' + file_name,'w',encoding='utf8') as f:
        json.dump(data_collect,f,ensure_ascii=False,indent=2)
    f.close()

if __name__ == '__main__':
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
    chrome_options.add_argument("--headless")

    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option('prefs', prefs)
    prefs = {'profile.managed_default_content_settings.images':2, 'disk-cache-size': 4096, 'intl.accept_languages': 'en-US'}
    chrome_options.add_argument('--dns-prefetch-disable')
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_argument('blink-settings=imagesEnabled=false')
    chrome_options.add_argument("--disable-javascript")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--in-process-plugins")
    chrome_options.add_argument('--no-sandbox')

    ua = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"
    chrome_options.add_argument("user-agent={}".format(ua))
    browser = webdriver.Chrome(driverPath,options=chrome_options)
    time.sleep(1.5)

    categories = [('c83plve5vmjt','國際','global'),
                  ('c9wpm0e5zv9t','兩岸','china'),
                  ('c32p4kj2yzqt','科技','tech'),
                  ('cq8nqywy37yt','財經','finance')]
    for cate_id,label,category in categories:
        scrape_link(cate_id,label,category)

