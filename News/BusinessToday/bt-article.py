import requests
from bs4 import BeautifulSoup
from datetime import date
import datetime
import time
import glob
import json
import os

def scrape_link(category,number):
    urls = []
    page = 1
    while True:
        page_link = f"http://www.businesstoday.com.tw/catalog/{number}/list/page/{page}"
        res =requests.get(page_link)
        soup = BeautifulSoup(res.text,'lxml')
        articles = soup.find_all(class_='article__item')
        for article in articles:
            dates = article.find('p','article__item-date').text.strip()
            links = article['href']
            if dates < end_date:
                break
            print(links)
            urls.append(links)
        if dates < end_date:
            break
        else:
            page += 1
    
    if len(urls)!=0:
        write_urls_to_txt(category,urls)
        scrape_content(category,urls)
        
def write_urls_to_txt(category,urls):
    #bulid folder yyyy-mm
    folder_path = '/home/ftp_246/data_1/news_data/businesstoday' + '/urls/' +time.strftime('%Y-%m') 
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(folder_path + '/'+f'bt-{category}-urls_'+time.strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url)
            txtf.write('\n')
    txtf.close()
        
def scrape_content(category,urls):
    data_collect = []
    for link in urls:
        try:
            soup = BeautifulSoup(requests.get(link).text,'lxml')
            article = {}

            article['url'] = link
            article['author'] = soup.find(class_='context__info-item--author').text
            article['title'] = soup.find(class_='article__maintitle').text
            article['date'] = soup.find(class_='context__info-item--date').text
            article['label'] = soup.find(class_='context__info-item--type').text
            article['content'] = ''.join(p.text.strip() for p in soup.find(itemprop='articleBody').select('div > div > p'))
            data_collect.append(article)
            
        except Exception as err:
            print('Error: could not parse.')
            print(err)
    if len(data_collect)!=0:
        write_to_json(data_collect)
                   
def write_to_json(data_collect):
    #bulid folder yyyy-mm
    folder_path = '/home/ftp_246/data_1/news_data/businesstoday/json/' + category + '/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    with open(folder_path + '/' + 'bt-'+category+'-'+time.strftime('%Y-%m-%d')+'.json','w',encoding='utf-8') as jf:
        json.dump(data_collect,jf,ensure_ascii=False,indent=2)
    jf.close()
    
if __name__ == '__main__':
    start_date = datetime.datetime.today() #today
    months = datetime.timedelta(days=1)  #last month
    end_date = (start_date - months).strftime('%Y-%m-%d')

    categories = [('finance', '80391'),('health' , '183029'),
                  ('life&consume','183030'),('tech','183015'),
                  ('politics&society','183027'),('InternationalGeneralEconomics','183025')]

    for category, number in categories:
        scrape_link(category,number)

