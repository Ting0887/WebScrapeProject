import requests
from bs4 import BeautifulSoup
import time
import datetime
import os
import json

def Ctitv(url):
    num = 1
    article = []
    while True: 
         try:
            base_url = url + cate1 + '/page/' + str(num)
            print(base_url)
         except:
             continue
         res = requests.get(base_url)
         soup = BeautifulSoup(res.text,'lxml')
         items = soup.find_all('div','column half b-col')
         for item in items:
             title = extract_title(item)
             link = extract_link(item)
             label = cate
             print(link)
             try:
                 res = requests.get(link)
                 soup = BeautifulSoup(res.text,'lxml')
                 
                 author = extract_author(soup)
                 date_time = extract_date(soup)
                 content = extract_content(soup)
                 keyword = extract_keyword(soup)

                 if date_time < end_date:
                     break
                 else:
                     article.append({'date_time':date_time,'title':title,'author':author,
                                     'label':label,'link':link,'content':content,'keyword':keyword})
             except:
                 continue
         if date_time < end_date:
             break
         else:
             num += 1
    if len(article)!=0:
        write_to_json(article)

def extract_title(item):
    try:
        title = item.find('h2','post-title').a.text
    except:
        title = ''
    return title

def extract_link(item):
    try:
        link = item.find('h2','post-title').a['href']
    except:
        link = ''
    return link

def extract_author(soup):
    try:
        author = soup.find('span','reviewer').text
    except:
        author = ''
    return author

def extract_date(soup):
    try:
        date_time = soup.find('time','value-title').text
    except:
        date_time = ''
    return date_time  

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div','post-content description')[0].find_all('p')
        for c in contents:
            content += c.text
    except:
        pass
    return content
           
def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','tagcloud')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except:
        pass
    return keyword
            
def write_to_json(article):
    #bulid folder yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/Ctitv/{cate2}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = 'ctitv_' + cate2 + time.strftime('%Y%m%d') + '.json'
    with open(folder_path +'/'+ filename,'w',encoding='utf8') as jf:
        json.dump(article,jf,ensure_ascii=False,indent=2)
    jf.close()

if __name__ == '__main__':
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days = 1)
    end_date = (start_date - d).strftime('%Y-%m-%d')
    print(end_date)
    cates = [('政治要聞','politics-news','politics'),
            ('社會萬象','local-news','society'),
            ('國際兩岸','international','global'),
            ('生活休閒','share-shopping','life'),
            ('健康新知','健康新知-2','health')]

    url = 'https://gotv.ctitv.com.tw/category/'
    for cate,cate1,cate2 in cates:
        Ctitv(url)
