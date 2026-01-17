import json
import os
import datetime
import time
import requests
from bs4 import BeautifulSoup

def determine_datetime(url,cate,cate1):
    link_collect = []
    num = 1
    while True:
        base_url = url + cate + '/page/' + str(num)
        print(base_url)
        res = requests.get(base_url)
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.find_all('div','listing listing-grid listing-grid-1 clearfix columns-2')[0]\
                .find_all('div','item-inner')
        for item in items:
            date_time = item.find('time').text
            link = item.find('h2').a.get('href')
            
            if date_time < end_date:
                break
            else:
                link_collect.append(link)

        if date_time < end_date:
            break
        else:
            num += 1
    if len(link_collect)!=0:
        extract_info(link_collect,cate,cate1)

def extract_info(link_collect,cate,cate1):
    article = []
    for link in link_collect:
        print(link)
        res = requests.get(link)
        soup = BeautifulSoup(res.text,'lxml')

        title = extract_title(soup)
        date_time = extract_date(soup)
        label = extract_label(soup)
        content = extract_content(soup)
        keyword = extract_keyword(soup)

        article.append({'title':title,'author':'芋傳媒',
                        'date_time':date_time,'link':link,
                        'content':content,'keyword':keyword[:-1],
                        'label':label[:-1],'website':'芋傳媒'})

    if len(article)!=0:
        write_to_json(article,cate1)

def extract_title(soup):
    try:
        title = soup.find('span','post-title').text
    except:
        title = ''
    return title

def extract_date(soup):
    try:
        date_time = soup.find('time').b.text
    except:
        date_time = ''
    return date_time

def extract_label(soup):
    label = ''
    try:
        labels = soup.find_all('div','term-badges floated')[0].find_all('a')
        for l in labels:
            label += l.text + '、'
    except:
        print('no label')
    return label 

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('p')
        for c in contents:
            content += c.text.replace('\n','')
    except:
        pass
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','post-tags')[0].find_all('a')
        for k in keywords:
            keyword += k.text + '、'
    except:
        print('no keyword')
    return keyword
        
def write_to_json(article,cate1):
    #bulid folder by yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/taronews/{cate1}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    filename = 'taro_' + cate1 + time.strftime('%Y%m%d') + '.json'
    with open(folder_path +'/'+filename,'w',encoding='utf8') as jf:
        json.dump(article,jf,ensure_ascii=False,indent=2)
    jf.close()

if __name__ == '__main__':
    start_date = datetime.datetime.today() #today
    months = datetime.timedelta(days=1)  #last month
    end_date = (start_date - months).strftime('%Y-%m-%d')
    print(end_date)
    url = 'https://taronews.tw/category/'
    
    category = [('politics','politics'),('world','global'),
                ('lifestyle','life'),('finance','finance'),('lifestyle/health','health')]

    for cate,cate1 in category:
        determine_datetime(url,cate,cate1)

