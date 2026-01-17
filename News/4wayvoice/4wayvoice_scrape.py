import os
import datetime
import time
import json
from bs4 import BeautifulSoup
import requests
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


def scrape_link(cate,url,folder):
    newsdata = []
    page = 1
    while True:
        page_url = url + '/page/' + str(page)
        print(page_url)
        res = requests.get(page_url)
        soup = BeautifulSoup(res.text,'lxml')
        bar = soup.find_all('div',{'role':'main'})[0].find_all('li')
        for item in bar:
            try:
                title = item.find('h2','post-title').text
            except:
                title = ''
            try:
                link = item.find('h2','post-title').a['href']
            except:
                link = ''
            try:
                date_time = link.split('/')[-3]
                date_time = datetime.datetime.strptime(date_time,'%Y%m%d').strftime('%Y-%m-%d')
            except:
                date_time = ''
            if date_time < end_date:
                break
            elif link !='':
                newsdata.append((title,link,date_time))
            print(link)
        if date_time < end_date:
            break
        else:
            page += 1
        
        #if end page
        mes = soup.find('div',{'role':'main'}).text
        if 'That page can’t be found' in mes:
            break
    if len(newsdata)!=0:
        scrape_content(newsdata)

def scrape_content(newsdata):
    article = []
    for item in newsdata:
        title = item[0]
        link = item[1]
        date_time = item[2]

        res = requests.get(link)
        soup = BeautifulSoup(res.text,'lxml')

        content = ''
        try:
            contents = soup.find_all('div',{'itemprop':'articleBody'})[0].find_all('p')
            for c in contents:
                content += c.text
        except:
            print('no content')
        keyword = ''
        try:
            keywords = soup.find_all('div','post-bottom-meta post-bottom-tags')[0].find_all('a')
            for k in keywords:
                keyword += k.text + ' '
        except:
            print('no keyword')

        article.append({'title':title,
                        'date_time':date_time,
                        'label':cate,
                        'link':link,
                        'content':content,
                        'keyword':keyword})
    if len(article)!=0:
        write_to_json(article)

def write_to_json(article):
    folder_path = f'/home/ftp_246/data_1/news_data/4wayvoice/{folder}/'+time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = '4wayvoice_'+folder+time.strftime('%Y%m%d')+'.json'
    with open(folder_path+'/'+filename,'w',encoding='utf-8')  as f:
        json.dump(article,f,ensure_ascii=False,indent=2)
    f.close()

if __name__ == '__main__':
    start_date = datetime.datetime.today() #today
    months = datetime.timedelta(days=1)  #last month
    end_date = (start_date - months).strftime('%Y-%m-%d') 
    print(end_date)
    
    cates = [('從四方看世界','https://4wayvoice.nownews.com/news/category/top-news-ch/4w-taiwan-ch/%E5%BE%9E%E5%9B%9B%E6%96%B9%E7%9C%8B%E4%B8%96%E7%95%8C','world'),
            ('從四方看亞洲','https://4wayvoice.nownews.com/news/category/top-news-ch/4w-taiwan-ch/%e5%be%9e%e5%9b%9b%e6%96%b9%e7%9c%8b%e4%ba%9e%e6%b4%b2/','asia'),
            ('從四方看臺灣','https://4wayvoice.nownews.com/news/category/top-news-ch/4w-taiwan-ch/%e5%be%9e%e5%9b%9b%e6%96%b9%e7%9c%8b%e8%87%ba%e7%81%a3/','taiwan')]
    for cate,url,folder in cates:
        scrape_link(cate,url,folder)
