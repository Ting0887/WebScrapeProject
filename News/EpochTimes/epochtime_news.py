import requests
from bs4 import BeautifulSoup
import time
import os
import datetime
import json
import re

def EpochTime(url,cate,cate1,cate2):
    article = []
    num = 1
    while True:
        base_url = url + cate1 + '_' + str(num) + '.htm'
        res = requests.get(base_url)
        print(base_url)
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.find_all('div','posts-list')[0].find_all('li')
        for item in items:
            link = extract_link(item)
            print(link)
            label = extract_label(item)

            resp = requests.get(link)
            soup = BeautifulSoup(resp.text,'lxml')
            title = extract_title(soup)
            date_time = extract_date(soup)
            content = extract_content(soup)
            keyword = extract_keyword(soup)
            if date_time < end_date:
                break
            else:
                article.append({'date_time':date_time,'title':title,
                                'label':label,'link':link,
                                'content':content,'keyword':keyword})
        if date_time < end_date:
            break
        else:
            num += 1
    # if no data,pass
    if len(article)!=0:
        outputjson(article,cate2)

def extract_link(item):
    try:
        link = item.find('a')['href']
    except:
        link = ''
    return link

def extract_label(item):
    try:
        label = item.find('span','sub-cat').text.strip()
    except:
        label = ''
    
    return label

def extract_title(soup):
    try:
        title = soup.find('h1').text
    except:
        title = ''
    return title

def extract_date(soup):
    try:
        date_time = soup.find('time')['datetime'][0:10]
    except:
        date_time = ''
    return date_time 

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div',{'itemprop':'articleBody'})[0].find_all('p')
        for c in contents:
            content += c.text
    except:
        print(e)
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','mbottom10 large-12 medium-12 small-12 columns')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except:
        pass
    return keyword

def outputjson(article,cate2):
    #bulid folder by yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/EpochTimes/{cate2}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = 'epoch_' + cate2 + time.strftime('%Y%m%d') + '.json'
    with open(folder_path +'/'+ filename,'w',encoding='utf8') as jf:
        json.dump(article,jf,ensure_ascii=False,indent=2)
    jf.close()
        
if __name__ == '__main__':
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days = 1)
    end_date = (start_date - d).strftime('%Y-%m-%d')
    print(end_date)
    url = 'https://www.epochtimes.com/b5/'

    cates=  [('台灣社會','ncid1077890','society'),
             ('台灣政治','ncid1077884','politics'),
             ('台灣生活','ncid1077891','life'),
             ('台灣經濟','ncid1077887','finance'),
             ('科技動向','ncid1185664','tech')
            ]
    for cate,cate1,cate2 in cates:
        EpochTime(url,cate,cate1,cate2)
