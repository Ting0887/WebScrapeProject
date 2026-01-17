import requests
from bs4 import BeautifulSoup
from datetime import date
import datetime
import time
import glob
import json
import os

headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

def scrape_link(category,label):
    urls = []
    page = 1
    article = {}
    while True:
        if page != 1:
            page_link = f"https://cnews.com.tw/category/{category}/page/{page}/"
        elif page == 1:
            page_link = f"https://cnews.com.tw/category/{category}/"
        res =requests.get(page_link,headers=headers,allow_redirects=False)
        print(page_link)
        try:
            soup = BeautifulSoup(res.text,'lxml')
            figures = soup.find_all('figure','special-format')
            for f in figures:
                links = f.find('a')['href']
                print(links)
                if '/category/' in links:
                    continue
                dates = f.find('li','date').text.strip()
                if dates < end_date:
                    break
                else:
                    urls.append(links)
            if dates < end_date:
                break
            else:
                page += 1
        except Exception as e:
            print(e)
    
    if len(urls)!=0:
        write_urls_to_txt(category,urls)
        scrape_content(category,urls)
        
def write_urls_to_txt(category,urls):
    #bulid folder yyyy-mm
    folder_path =  '/home/ftp_246/data_1/news_data/CNews/urls/' + time.strftime('%Y-%m') 
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(folder_path + '/'+f'cnews-{category}-urls_'+time.strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url+'\n')
    txtf.close()
    
def scrape_content(category,urls):
    data_collect = []
    article = {}
    for url in urls:
        print(url)
        time.sleep(4)
        try:
            soup = BeautifulSoup(requests.get(url,headers=headers,allow_redirects=False).text,'lxml')
            title = soup.find(id='articleTitle')\
                                   .find(class_='_line')\
                                   .strong.text.strip()
            date = soup.find(class_='date').text.strip()
            author = soup.find(class_='user').text.strip()
            label = category
            content = soup.find(
                class_='theme-article-content').article.text.strip()

            try:
                keywords = [a.text for a in soup.select('.tags > a')]
            except:
                pass
            article = {'url':url,'title':title,
                       'date':date,'author':author,
                       'label':label,'content':content,
                       'keywords':keywords}
            print(article)
            data_collect.append(article)
        except Exception as e:
            print(e)
            pass
    if len(data_collect)!=0:
        write_to_json(data_collect)
                   
def write_to_json(data_collect):
    #bulid folder yyyy-mm
    folder_path = '/home/ftp_246/data_1/news_data/CNews/json/' + label + '/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    with open(folder_path + '/' + 'cnews-'+label+'-'+time.strftime('%Y-%m-%d')+'.json','w',encoding='utf-8') as jf:
        json.dump(data_collect,jf,ensure_ascii=False,indent=2)
    jf.close()
    
if __name__ == '__main__':
    
    start_date = datetime.datetime.today() #today
    months = datetime.timedelta(days=1)  #last month
    end_date = (start_date - months).strftime('%Y-%m-%d')
    print(end_date)

    categories = [
                 ('新聞匯流', 'news'),
                 ('政治匯流', 'politics'),
                 ('國際匯流', 'global'),
                 ('生活匯流', 'life'),
                 ('健康匯流', 'health'),
                 ('金融匯流', 'finance'),
                 ('數位匯流', 'tech')
                 ]

    for category, label in categories:
        scrape_link(category,label)
