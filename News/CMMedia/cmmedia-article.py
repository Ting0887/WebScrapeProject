import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import date
import datetime
import time
import glob
import json
import os

def scrape_link(category,label):
    urls = []
    page = 1
    while True:
        page_link = f"https://www.cmmedia.com.tw/api/articles?num=12&page={page}&category={category}"
        res =requests.get(page_link,'lxml')
        try:
            for item in res.json():
                link = 'https://www.cmmedia.com.tw/home/articles/'+str(item['id'])
                resq = requests.get(link)
                soup = BeautifulSoup(resq.text,'lxml')
                dates = soup.find(class_="article_author-bar").span.next_sibling.text
                if dates < end_date:
                    break
                else:
                    print(link)
                    urls.append(link)

            if dates < end_date:
                break
            else:
                page += 1
        except Exception as e:
            print(e)
    
    if len(urls)!=0:
        write_urls_to_txt(category,urls)
        scrape_content(label,urls)
        
def write_urls_to_txt(category,urls):
    #bulid folder yyyy-mm
    folder_path =  '/home/ftp_246/data_1/news_data/CMMedia/urls/' + time.strftime('%Y-%m') 
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(folder_path + '/'+f'cmmedia-{category}-urls_'+time.strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url)
            txtf.write('\n')
    txtf.close()

def scrape_content(label,urls):
    data_collect = []
    for link in urls:
        browser.get(link)
        time.sleep(1)
        soup = BeautifulSoup(browser.page_source,'lxml')
        try:
            url = link.replace('\n','')
            title = soup.find(class_='article_title').text
            author = soup.find(class_="article_author-bar").span.text
            date = soup.find(class_="article_author-bar").span.next_sibling.text
            content = ''.join(p.text for p in soup.select(".article_content > p"))
            article = {'url':url,'title':title,
                        'author':author,'date':date,
                        'label':label,'content':content}
            print(article)
            data_collect.append(article)
        except Exception as e:
                print(e)
    if len(data_collect)!=0:
        write_to_json(data_collect)
                   
def write_to_json(data_collect):
    #bulid folder yyyy-mm
    folder_path = '/home/ftp_246/data_1/news_data/CMMedia/json/' + category + '/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    with open(folder_path + '/' + 'cmmedia-'+category+'-'+time.strftime('%Y-%m-%d')+'.json','w',encoding='utf-8') as jf:
        json.dump(data_collect,jf,ensure_ascii=False,indent=2)
    jf.close()
    
if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Chrome('/home/cdna/chromedriver', options=chrome_options)
    time.sleep(1)
    start_date = datetime.datetime.today() #today
    months = datetime.timedelta(days=1)  #last month
    end_date = (start_date - months).strftime('%Y-%m-%d')
    print(end_date)
    
    categories = [
                ('politics', '政治'),
                ('life'    , '生活'),
                ('finance' , '財經'),
                 ]
    
    for category, label in categories:
        scrape_link(category,label)
    browser.close()
