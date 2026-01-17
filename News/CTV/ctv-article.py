import requests
from bs4 import BeautifulSoup
import time
import datetime
import os
import json

def scrape_link(label,category):
    urls = []
    page = 1
    while True:
        if page == 1:
            page_link = f"http://new.ctv.com.tw/Category/{category}"
        else:
            page_link = f"http://new.ctv.com.tw/Category/{category}?PageIndex={page}"
        res = requests.get(page_link,headers=headers)
        soup = BeautifulSoup(res.text,'lxml')
        for a in soup.select("div.list")[1].find_all('a'):
            link = 'http://new.ctv.com.tw' + a['href']
            print(link)
            date = a.find('div','time').text
            print(date)
            if date < end_date:
                break
            else:
                print(link)
                urls.append(link)
        if date < end_date:
            break
        else:
            page += 1
    if len(urls)!=0:
        write_to_txt(label,urls)
        scrape_content(category,urls)

def write_to_txt(label,urls):
    folder_path =  '/home/ftp_246/data_1/news_data/CTV/urls/' + time.strftime('%Y-%m') 
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(folder_path + '/'+f'ctv-{label}-urls_'+time.strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url+'\n')
    txtf.close()

def scrape_content(category,urls):
    data_collect = []
    for link in urls:
        try:
            res = requests.get(link)
            soup = BeautifulSoup(res.text,'lxml')
            time.sleep(2.5)
            title = soup.find(class_='title').text.split('│')[0].strip()
            date = soup.find(class_='author').text.split('|')[1].strip()
            content = soup.find(class_='editor').text.strip()
            article = {'url':link,'title':title,'date':date,'label':category,'content':content}
            print(article)
            data_collect.append(article)
        except Exception as e:
            print(e)
    
    if len(data_collect)!=0:
        write_to_json(label,data_collect)

def write_to_json(label,data_collect):
    folder_path =  f'/home/ftp_246/data_1/news_data/CTV/json/{label}/' + time.strftime('%Y-%m') 
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = f'ctv-{label}'+time.strftime('%Y-%m-%d')+'.json'
    with open(folder_path +'/'+ filename,'w',encoding='utf-8') as jf:
        json.dump(data_collect,jf,ensure_ascii=False,indent=2)
    jf.close()
    
if __name__ == '__main__':
    headers = {'Host': 'new.ctv.com.tw',
               'Connection': 'keep-alive',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36','Connection': 'keep-alive','Host': 'new.ctv.com.tw'}
    
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days=1)
    end_date = (start_date - d).strftime('%Y/%m/%d')
    
    categories = [
        ('popular', '十大發燒新聞'),
        ('life', '生活'),
        ('society', '社會'),
        ('world', '國際'),
        ('politics','政治')
    ]
    for label,category in categories:
        scrape_link(label,category)
