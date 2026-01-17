import requests
from bs4 import BeautifulSoup
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
        page_link = f"https://www.ftvnews.com.tw/tag/{category}/{page}"
        print(page_link)
        resq =requests.get(page_link,headers=headers)
        if resq.status_code != 200:
            break
        try:
            soup = BeautifulSoup(resq.text,'lxml')
            items = soup.find_all('ul','row')[1].find_all('li','col-lg-4 col-sm-6')
            for item in items:
                links = 'https://www.ftvnews.com.tw'+item.find('a')['href']  
                print(links)
                dates = item.find('div','time').text.strip()
                if dates < end_date:
                    break
                else:
                    urls.append(links)
            if dates < end_date:
                break
            else:
                page += 1
        except Exception as e:
            break
    
    if len(urls)!=0:
        write_urls_to_txt(label,urls)
        scrape_article(category,urls)
        
def write_urls_to_txt(label,urls):
    #bulid folder yyyy-mm
    folder_path =  '/home/ftp_246/data_1/news_data/FTVNnews/urls/' + time.strftime('%Y-%m') 
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(folder_path + '/'+f'ftv-{label}-urls_'+time.strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url+'\n')
    txtf.close()
    
def scrape_article(category,urls):
    data_collect = []
    for url in urls:
        time.sleep(1)
        try:
            res = requests.get(url,headers=headers)
            soup = BeautifulSoup(res.text,'lxml')
            title = extract_title(soup)
            date = extract_date(soup)
            contents = extract_content(soup)
            summary = extract_summary(soup)
            article = {'contents':contents,'summary':summary,'label':category,
                       'date':date,'title':title,'url':url}
            print(article)
            data_collect.append(article)
        except Exception as e:
            print(e)
    if len(data_collect)!=0:
        write_to_json(data_collect)

def extract_title(soup):
    try:
        title = soup.find('h1','text-center').text.replace('\n','').replace('\r','').strip()
    except:
        title = ''
    return title

def extract_date(soup):
    try:
        date = soup.find('li','date').text.strip()
    except:
        date = ''
    return date

def extract_content(soup):
    contents = ''
    try:
        content = soup.find_all('article')[0].find_all('p')
        for c in content:
            contents += c.text.replace('\n','')
    except:
        pass
    return contents

def extract_summary(soup):
    try:
        summary = soup.find('div',id='preface').text
    except:
        summary = ''
    return summary

def write_to_json(data_collect):
    #bulid folder yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/FTVNnews/json/{label}' + '/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)        
    with open(folder_path + '/' + 'ftv-'+label+'-'+time.strftime('%Y-%m-%d')+'.json','w',encoding='utf-8') as jf:
        json.dump(data_collect,jf,ensure_ascii=False,indent=2)
    jf.close()
    
if __name__ == '__main__':
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    start_date = datetime.datetime.today() #today
    months = datetime.timedelta(days=1)  #last month
    end_date = (start_date - months).strftime('%Y/%m/%d')
    print(end_date)

    categories = [('政治','politics'),('國際','world'),('社會','society'),
                  ('生活','life'),('健康','health'),('財經', 'finance'),]
    for category, label in categories:
        scrape_link(category,label)
