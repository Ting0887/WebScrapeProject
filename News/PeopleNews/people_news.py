import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os
import datetime

def data_payloads(url,page):
    payloads = {'page': page,
                'status': '1'}
    return payloads

def data_headers(url,page):
     headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
               AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
               'x-requested-with': 'XMLHttpRequest'}
     return headers
 
def people_news(url,page,cate,cate1):
    article = []
    while True:
        base_url = url + cate1
        res = requests.post(base_url,\
                            headers=data_headers(url,page)\
                            ,data=data_payloads(url,page))
        try:
            parse_json = res.json()
            for item in parse_json['data_list']:
                title = extract_title(item)
                date_time = extract_date(item)
                author = extract_author(item)
                link = extract_link(item)
                content = extract_content(item)

                if date_time < end_date:
                    break
                else:
                    #collect every news data in article list
                    article.append({'date_time':date_time,'author':author,
                                    'title':title,'link':link,'label':cate1,
                                    'content':content,'keyword':''})
            #while datetime < enddate break
            if date_time < end_date:
                break
            else:
                page += 1
        except:
            print('can not parse json')

    if len(article)!=0:
        write_to_json(article,cate)

def extract_title(item):
    #title
    try:
        title = item['TITLE']
    except:
        title = ''
    return title

def extract_date(item):
    #datetime
    try:
        date_time = item['PUBTIME']
    except:
        date_time = ''
    return date_time

def extract_author(item):
    #author
    try:
        author = item['AUTHOR']
    except:
        author = ''
    return author

def extract_link(item):
    #link
    try:
        link = 'https://www.peoplenews.tw/news/' + item['EID']
    except:
        link = ''
    return link

def extract_content(item):
    #content
    try:
        content = BeautifulSoup(item['CONTENT'],'lxml').text.replace('\n','')
    except:
        content = ''
    return content

def write_to_json(article,cate):
    #bulid folder by yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/PeopleNews/{cate}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    filename = 'people_' + cate + time.strftime('%Y%m%d') + '.json'
    with open(folder_path +'/'+ filename,'w',encoding='utf8') as jf:
        json.dump(article,jf,ensure_ascii=False,indent=2)
    jf.close()
    
if __name__ == '__main__':
    page = 1
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days = 1)
    end_date = (start_date - d).strftime('%Y-%m-%d')
                                         
    cates = [('politics','政治'),
             ('society','社會'),
             ('global','全球'),
             ('life','生活'),
             ('finance','財經')]

    url = 'https://www.peoplenews.tw/resource/lists/NEWS/'
    for cate,cate1 in cates:
        people_news(url,page,cate,cate1)
