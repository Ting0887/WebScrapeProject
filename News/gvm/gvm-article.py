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
        page_link = f"https://www.gvm.com.tw/category/{label}?page={page}"
        res = requests.get(page_link)
        print(page_link)
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.find_all('div','article-list-item__intro')
    
        for item in items:
            link = item.find('a')['href']
            date = item.find('div','time').text
            print(link)
        
            if date < end_date:
                break
            else:
                urls.append(link)
        if date < end_date:
            break
        page += 1
    if len(urls)!=0:
        write_to_txt(label,urls)
        scrape_content(category,urls)

def write_to_txt(label,urls):
    folder_path =  '/home/ftp_246/data_1/news_data/gvm/urls/' + time.strftime('%Y-%m') 
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(folder_path + '/'+f'ctv-{label}-urls_'+time.strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url+'\n')
    txtf.close()

def scrape_content(category,urls):
    data_collect = []
    for url in urls:
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text,'lxml')
            title = soup.find('h1').text
            author = soup.find('div', class_="pc-bigArticle").a.text
            date = soup.find(class_='article-time').text
            content = soup.find(class_='article-content').text.strip()
        except:
            pass
        try:
            keywords = [k.text for k in soup.find(class_='article-keyword').find_all('a')]
        except:
            keywords = ''
        
        article = {'url':url,'title':title,'author':author,
                   'date':date,'label':category,'content':content,'keywords':keywords}      
        data_collect.append(article)
        
    if len(data_collect)!=0:
        write_to_json(label,data_collect)

def write_to_json(label,data_collect):
    folder_path =  f'/home/ftp_246/data_1/news_data/gvm/json/{label}/' + time.strftime('%Y-%m') 
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = f'gvm-{label}-'+time.strftime('%Y-%m-%d')+'.json'
    with open(folder_path +'/'+ filename,'w',encoding='utf-8') as jf:
        json.dump(data_collect,jf,ensure_ascii=False,indent=2)
    jf.close()
    
if __name__ == '__main__':
    
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days=1)
    end_date = (start_date - d).strftime('%Y-%m-%d')
    
    categories = [('news','時事熱點'),('world','國際'),('money','金融'),
                  ('tech','科技'),('business','產經'),('life','生活')]

    for label,category in categories:
        scrape_link(label,category)
