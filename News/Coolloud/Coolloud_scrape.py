import os
import datetime
import time
import json
import requests
from bs4 import BeautifulSoup

headers = {"referer": "https://www.coolloud.org.tw/story",
           "Connection": "keep-alive",
           "upgrade-insecure-requests": "1",
           "cache-control": "max-age=0",
           "if-modified-since": "",
            "if-none-match": "W/61501943-8991",
           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"}

def scrape_link(start_date,end_date):
    newsdata = []
    page = 0
    while True:
        if page == 0:
            url = 'https://www.coolloud.org.tw/story'
        elif page!=1:
            url = 'https://www.coolloud.org.tw/story?page=' + str(page)
        print(url)
        time.sleep(3)
        res = requests.get(url,headers=headers,allow_redirects=False)
        res.encoding = 'utf8'
        soup = BeautifulSoup(res.text,'lxml')
        bar = soup.find_all('div','view-content')[1].find_all('div','views-row')
        for item in bar:
            title = extract_title(item)
            link = extract_link(item)
            author = extract_author(item)
            date_time = extract_date(item)
            if date_time < end_date:
                break
            else:
                newsdata.append((title,link,author,date_time))
            print(link)
        if date_time < end_date:
            break
        else:
            page += 1
    if len(newsdata)!=0:
        scrape_content(newsdata)

def extract_title(item):
    try:
        title = item.find('span','field-content pc-style').text.replace('\n','')
    except:
        title = ''
    return title

def extract_link(item):
    try:
        link = 'https://www.coolloud.org.tw' + item.find('a')['href']
    except:
        link = ''
    return link

def extract_author(item):
    try:
        author = item.find('div','views-field-field-author').text
    except:
        author = ''
    return author

def extract_date(item):
    try:
        date_time = item.find('span','date-display-single').text
    except:
        date_time = 'no date'
    return date_time  

def scrape_content(newsdata):
    article = []
    for item in newsdata:
        title = item[0]
        link = item[1]
        author = item[2]
        date_time = item[3]
        try:
            res = requests.get(link,headers=headers,timeout=5,allow_redirects=False)
            res.encoding = 'utf8'
            soup = BeautifulSoup(res.text,'lxml')
            content = ''
            try:
                contents = soup.find_all('div','nodeinner')
                for c in contents:
                    content += c.text.replace('\n','') .replace('\r','') .replace('\t','')
            except:
                print('no content')
            keyword = ''
            try:
                keywords = soup.find_all('div','field-name-field-tag')[0].find_all('a')
                for k in keywords:
                    keyword += k.text + ' '
            except:
                print('no keyword')
            article.append({'title':title,
                            'date_time':date_time,
                            'label':'苦勞報導',
                            'link':link,
                            'content':content,
                            'keyword':keyword})
            print(article)
        except:
            break
    write_to_json(article)

def write_to_json(article):
    #if no dir,auto make dir
    folder_path = '/home/ftp_246/data_1/news_data/Coolloud/'+time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = 'coolloud_report' + time.strftime('%Y%m%d') + '.json'
    with open(folder_path+'/'+ filename,'w',encoding='utf-8') as f:
        json.dump(article,f,ensure_ascii=False,indent=2)
    f.close()

if __name__ == '__main__':
    #absolute path
    dirpath = os.path.dirname(os.path.abspath(__file__))

    #start date,end date
    start_date = datetime.datetime.today() #today
    months = datetime.timedelta(days=1)  #last month
    end_date = (start_date - months).strftime('%Y/%m/%d')
    print(end_date)
    scrape_link(start_date,end_date)
