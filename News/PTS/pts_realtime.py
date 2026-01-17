import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
import os

def Scrape(url):
    page = 1
    article = []
    while True:
        base_url = url + str(page)
        print(base_url)
        res = requests.get(base_url)
        soup = BeautifulSoup(res.text,'lxml')
        try:
            items = soup.find_all('ul','list-unstyled news-list')[0].find_all('li','d-flex')
            for item in items:
                title = extract_title(item)
                date_time = extract_date(item)
                link = extract_link(item)
                keyword = extract_keyword(item)

                res = requests.get(link)
                soup = BeautifulSoup(res.text,'lxml')
                label = extract_label(soup)
                author = extract_author(soup)
                content = extract_content(soup)

                if date_time < end_date:
                    break
                else:
                    article.append({'date_time':date_time,'author':author,
                                    'title':title,'link':link,'label':label,
                                    'content':content,'keyword':keyword})
            if date_time < end_date:
                    break
            else:
                page += 1
        except:
            continue

    if len(article)!=0:
        write_to_json(article)

def extract_title(item):
    try:
        title = item.find('h2').text
    except:
        title = ''
    return title

def extract_date(item):
    try:
        date_time = item.find('time')['datetime']
    except:
        date_time = ''
    return date_time 

def extract_link(item):
    try:
        link = item.find('h2').a.get('href')
    except:
        link = ''
    return link

def extract_keyword(item):                        
    keyword = ''
    try:
        keywords = item.find_all('ul','list-unstyled tag-list d-flex flex-wrap')[0].find_all('a')
        for k in keywords:
            keyword += k.text.replace('...','') + ' '
    except:
        print('no keyword')
    return keyword 

def extract_label(soup):
    try:
        label = soup.find_all('ol','breadcrumb')[0].find_all('li','breadcrumb-item')[1].text.replace('\n','')
    except:
        label = ''
    return label 

def extract_author(soup):
    try:
        author = soup.find('span','article-reporter mr-2').text
    except:
        author = ''
    return author  

def extract_content(soup):
    try:
        content = soup.find('article','post-article').text.replace('\n','').strip()
    except:
        content = ''
    return content

def write_to_json(article):
    #bulid folder yyyy-mm
    folder_path = '/home/ftp_246/data_1/news_data/PTS/2020~2021/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = 'pts_' + time.strftime('%Y%m%d') + '.json'
    with open(folder_path+'/'+ filename,'w',encoding='utf8') as jf:
        json.dump(article,jf,ensure_ascii=False,indent=2)
    jf.close()

if __name__ == '__main__':
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days = 1)
    end_date = (start_date - d).strftime('%Y-%m-%d')
    url = 'https://news.pts.org.tw/dailynews?page='
    Scrape(url)
