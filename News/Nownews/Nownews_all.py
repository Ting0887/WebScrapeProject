import requests
from bs4 import BeautifulSoup
import json
import os
import time
import datetime

def Nownews(url):
    base_url = url  + cate2 + '/'
    res = requests.get(base_url)
    try:
        parse_js = res.json()
        for item in parse_js['data']['newsList']:
            last_pid = item['id']
    except:
        pass

    data_article = []
    while True:
        try:
            base_url = url + cate2 + '/' + '?pid=' + last_pid
            print(base_url)
            res = requests.get(base_url)
            if len(parse_js['data']) == 0:
                break
            parse_js = res.json()
            for item in parse_js['data']['newsList']:
                title = extract_title(item)
                link = extract_link(item)
                date_time = extract_date(item)
                res = requests.get(link)


                soup = BeautifulSoup(res.text,'lxml')
                [x.extract() for x in soup.findAll(['script','br'])]
            
                label = cate
                author = extract_author(soup)
                content = extract_content(soup)
                keyword = extract_keyword(soup)
                if date_time < end_date:
                    break
                else:
                    data_article.append({'date_time':date_time,'title':title,
                                         'author':author,'label':label,
                                         'link':link,'content':content,
                                         'keyword':keyword})
            last_pid = item['id']
        except:
            break
        if date_time < end_date:
            break
    
    if len(data_article)!=0:
        write_into_json(data_article)
            
def extract_title(item):
    try:
        title = item['postTitle']
    except:
        title = ''
    return title

def extract_link(item):
    try:
        link = 'https://www.nownews.com' + item['postUrl']
    except:
        link = ''
    return link 

def extract_date(item):
    try:
        date_time = item['newsDate']
    except:
        date_time = ''
    return date_time    

def extract_author(soup):
    try:
        author = soup.find('div','info').p.text
    except:
        author = ''
    return author

def extract_content(soup):
    try:
        content = soup.find('article').text.replace('\n','').replace('\t','').strip()
    except:
        content = ''
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('ul','tag')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except:
        pass
    return keyword

def write_into_json(data_article):
    #bulid folder by yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/Nownews/{cate1}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = 'Nownews_' + cate1 + time.strftime('%Y%m%d') + '.json'
    with open(folder_path + '/' + filename,'w',encoding='utf8') as f:
        json.dump(data_article,f,ensure_ascii=False,indent=2)
    f.close()
    
if __name__ == '__main__':
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days = 7)
    end_date = (start_date - d).strftime('%Y-%m-%d')
    
    cates = [
            ('政治','politics','news-summary'),
            ('社會','society','society'),
            ('國際','global','news-global'),
            ('生活','life','life'),
            ('健康','health','health-life'),
            ('財經','finance','finance')
            ]
    
    url ='https://www.nownews.com/nn-client/api/v1/cat/'
    for cate,cate1,cate2 in cates:
        Nownews(url)
