import requests
from bs4 import BeautifulSoup
import time
import datetime
import os
import json

def category_url(cate,cate1,cate2):
    page = 1
    collect_url = []
    while True:
        url = f'https://bccnews.com.tw/archives/category/{cate2}/page/{page}'
        print(url)
        res = requests.get(url,headers=headers)
        soup = BeautifulSoup(res.text,'lxml')
        article = soup.find_all('div',id='tdi_65')[0].find_all('div','td-module-thumb')
        for item in article:
            link = item.find('a','td-image-wrap')['href']
            res = requests.get(link,headers=headers)
            soup = BeautifulSoup(res.text,'lxml')
            date_time = soup.find('time')['datetime'][0:10]
            print(date_time)

            if date_time < end_date:
                break
            else:
                collect_url.append(link)
        if date_time < end_date:
            break
        else:
            page += 1
    if len(collect_url)!=0:
        scrape_info(collect_url,cate,cate1)

def scrape_info(collect_url,cate,cate1):
    article = []
    for link in collect_url:
        res = requests.get(link,headers=headers)
        soup = BeautifulSoup(res.text,'lxml')
        
        date_time = extract_date(soup)
        title = extract_title(soup)
        content = extract_content(soup)
        keyword = extract_keyword(soup)
        post = {'title':title,'author':'','date_time':date_time,
                'content':content,'keyword':keyword,'link':link,
                'label':cate,'website':'中國廣播公司'}
        print(post)
        article.append(post)
    if len(article)!=0:
        write_to_json(article,cate1)

def extract_date(soup):
    try:
        date_time = soup.find('time')['datetime'][0:10]
    except:
        date_time = ''
    return date_time

def extract_title(soup):
    try:
        title = soup.find('h1').text
    except:
        title = ''
    return title

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('p')
        for c in contents:
            if '本網站內容屬於中國' in c.text:
                break
            else:
                content += c.text
    except:
        pass
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('ul','tdb-tags')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except:
        keyword = ''
    return keyword

def write_to_json(article,cate1):
    folder_path = f'/home/ftp_246/data_1/news_data/BCC/{cate1}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    file_name = f'BCC_{cate1}'  + time.strftime('%Y%m%d') + '.json'
    with open(folder_path + '/' + file_name,'w',encoding='utf8') as f:
        json.dump(article,f,ensure_ascii=False,indent=2)
    f.close()

if __name__ == '__main__':
    #Start date,End date
    start_date = datetime.datetime.today() #today
    months = datetime.timedelta(days=1)  #last month
    end_date = (start_date - months).strftime('%Y-%m-%d')
    print(end_date)
    
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"}
    categories = [('政治','politics','c-03'),
                  ('國際','internation','c-04'),
                  ('社會','society','c-08'),
                  ('生活','life','c-07'),
                  ('財經','finance','c-06')]

    for cate,cate1,cate2 in categories:
        category_url(cate,cate1,cate2)

