import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
import os

def Scrape_link(url,cate,cate1):
    news_link = []
    num = 1
    while True:
        base_url = url + cate1 + '/page/' + str(num)
        res = requests.get(base_url)
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.find_all('div','item-inner clearfix')
        for item in items:
            link = item.find('a')['href']
            date_time = item.find('time','post-published updated').text
            if date_time < end_date:
                break
            else:
                news_link.append(link)
            
        if date_time < end_date:
            break
        else:
            num += 1

    if len(news_link)!=0:
        Scrape_article(news_link)

def Scrape_article(news_link):
    article = []
    for link in news_link:
        print(link)
        res = requests.get(link)
        soup = BeautifulSoup(res.text,'lxml')
        date_time = extract_date(soup)
        author = extract_author(soup)
        title = extract_title(soup)
        content = extract_content(soup)
        keyword = extract_keyword(soup)
        if content == '':
            continue
        article.append({'date_time':date_time,'author':author,'title':title,
                        'label':cate,'link':link,'content':content,'keyword':keyword})
    if len(article)!=0:
        outputjson(article)

def extract_date(soup):
    try:
        date_time = soup.find('time','post-published updated').text
    except:
        date_time = ''
    return date_time  

def extract_author(soup):
    try:
        author = soup.find('a','author url fn').text
    except:
        author = ''
    return author

def extract_title(soup):
    try:
        title = soup.find('span','post-title').text
    except:
        title = ''
    return title

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div','entry-content clearfix single-post-content')[0].find_all('p')
        for c in contents:
            content += c.text
    except:
        pass
    return content
        
def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','entry-terms post-tags clearfix style-24')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except:
        pass
    return keyword
        
def outputjson(article):
    #bulid folder by yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/Ctee/{cate1}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = 'ctee_' + cate1 + time.strftime('%Y%m%d') + '.json'
    with open(folder_path +'/'+ filename,'w',encoding='utf8') as f:
        json.dump(article,f,ensure_ascii=False,indent=2)
    f.close()
    
if __name__ == '__main__':
    start_date  = datetime.datetime.today()
    d = datetime.timedelta(days=1)
    end_date = (start_date - d).strftime('%Y.%m.%d')
    
    cates = [('國際','global'),('要聞','policy'),('財經','finance'),('3c消費','3C')]

    for cate,cate1 in cates:
        if cate == '3c消費':
            url = 'https://ctee.com.tw/tag/'
        else:
            url =  'https://ctee.com.tw/category/news/'
        Scrape_link(url,cate,cate1)
