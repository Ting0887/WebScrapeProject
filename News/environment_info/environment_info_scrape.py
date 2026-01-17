import os
import time
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
import json
import requests

def scrape(url,cate,folder):
    newsdata = []
    page = 0
    while True:
        if page == 0:
            page_url = url
        else:
            page_url = url + '?page=' + str(page)
        print(page_url)
        res = requests.get(page_url)
        res.encoding = 'utf8'
        soup = BeautifulSoup(res.text,'lxml')
        bar = soup.find_all('div','view-display-id-page')[0].find_all('div','views-row')
        for item in bar:
            title = extract_title(item)
            date_time = extract_date(item)
            link = extract_link(item)
            if date_time < end_date:
                break
            else:
                print(link)
                newsdata.append((title,date_time,link))
        if date_time < end_date:
            break
        else:
            page += 1
    if len(newsdata)!=0:
        scrape_article(newsdata)

def extract_title(item):
    try:
        title = item.find('div','views-field-title').text
    except:
        title = ''
    return title

def extract_date(item):
    try:
        date_time = item.find('span','views-field views-field-created').text.strip()
    except:
        date_time = ''
    return date_time

def extract_link(item):
    try:
        link = 'https://e-info.org.tw' + item.find('div','views-field-title').a.get('href')
    except:
        link = ''
    return link

def scrape_article(newsdata):
    article = []
    for item in newsdata:
        title = item[0]
        date_time = item[1]
        link = item[2]
        res = requests.get(link)
        res.encoding = 'utf8'
        soup = BeautifulSoup(res.text,'lxml')
        
        content = extract_content(soup)
        keyword = extract_keyword(soup)

        article.append({'title':title,'author':'','date_time':date_time,
                        'label':cate,'link':link,'content':content,'keyword':keyword})
    if len(article)!=0:
        write_to_json(article)

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('p')[:-4]
        for c in contents:
            content += c.text.replace('\n','')
    except:
        content = ''
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','field-type-taxonomy-term-reference')
        for k in keywords:
            keyword += k.text + ' '
    except:
        keyword = ''
    return keyword

def write_to_json(article):
    folder_path = f'/home/ftp_246/data_1/news_data/environment_info/{folder}/'+time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = folder+time.strftime('%Y%m%d')+'.json'
    with open(folder_path+'/'+filename,'w',encoding='utf-8')  as jf:
        json.dump(article,jf,ensure_ascii=False,indent=2)
    jf.close()

if __name__ == '__main__':
    # start date, end date
    start_date = datetime.datetime.today() #today
    months = datetime.timedelta(days=1)  #last month
    end_date = (start_date - months).strftime('%Y-%m-%d') 
    print(end_date)

    cate_url = [('https://e-info.org.tw/taxonomy/term/5','台灣新聞','taiwan_news'),
                ('https://e-info.org.tw/taxonomy/term/14','國際新聞','global_news'),
                ('https://e-info.org.tw/taxonomy/term/13','中國新聞','china_news')]
    
    for url,cate,folder in cate_url:
        scrape(url,cate,folder)
