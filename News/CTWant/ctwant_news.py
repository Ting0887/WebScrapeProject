import json
import os
from bs4 import BeautifulSoup
import requests
import datetime
import time

def CTWant(url,cate,cate1):
    page = 1 
    article = []
    while True:
        base_url = url + cate1 + '?page=' + str(page)
        print(base_url)
        res = requests.get(base_url)
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.find_all('a','m-card col-sm-4 col-6')
        for item in items:
            title = extract_title(item)
            link = extract_link(item)
            
            resq = requests.get(link)
            soup = BeautifulSoup(resq.text,'lxml')
            time.sleep(0.5)
            
            date_time = extract_date(soup)
            author = extract_author(soup)
            content = extract_content(soup)
            keyword = extract_keyword(soup)

            if date_time < end_date:
                break
            else:
                article.append({'date_time':date_time,'title':title,'author':author,
                                'link':link,'label':cate1,'content':content,'keyword':keyword})
        if date_time < end_date:
            break
        else:
            page += 1

    if len(article)!=0:
        write_to_json(article,cate)

def extract_title(item):
    try:
        title = item.find('h3').text.replace('\n','').strip()
    except:
        title = ''
    return title

def extract_link(item):
    try:
        link = 'https://www.ctwant.com' + item['href']
    except:
        link = ''
    return link

def extract_date(soup):    
    try:
        date_time = soup.find('time')['datetime']
    except:
        date_time = ''
    return date_time

def extract_author(soup):
    try:
        author = soup.find('span','p-article-info__author').text.split(':').strip()
    except:
        author = ''
    return author
            
def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('article')[0].find_all('p')
        for c in contents:
            content += c.text
    except:
        pass
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','l-tags__wrapper')[0].find_all('a')
        for k in keywords:
            keyword += k.text.replace('\n','').replace(' ','') + ' '
    except Exception as e:
        print(e)
    return keyword
        
def write_to_json(article,cate):
    #bulid folder by yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/CTWant/{cate}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file = 'ctwant_' + cate + time.strftime('%Y%m%d') + '.json'
    with open(folder_path +'/'+ file,'w',encoding='utf8') as f:
        json.dump(article,f,ensure_ascii=False,indent=2)
    f.close()
    
if __name__ == '__main__':
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days = 1)
    end_date = (start_date - d).strftime('%Y-%m-%d')
    print(end_date)                                     
    cates = [('society','社會'),('finance','財經'),('politics','政治'),
            ('life','生活'),('global','國際')]

    url = 'https://www.ctwant.com/category/'
    for cate,cate1 in cates:
        CTWant(url,cate,cate1)
