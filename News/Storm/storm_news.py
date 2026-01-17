import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
import os

def parse_cateurl(url,cate):
    page = 1
    posts = []
    while True:
        page_url = url + '/' + str(page)
        print(page_url)
        res = requests.get(page_url,headers=headers)
        soup = BeautifulSoup(res.text,'lxml')
        bar = soup.find_all('div',{'id':'category_content'})[0].find_all('div','category_card card_thumbs_left')

        for item in bar:
            label = extract_label(item)
            title = extract_title(item)
            author = extract_author(item)
            date_time = extract_date(item)
            link = extract_link(item)
            
            if date_time < end_date:
                break
            else:
                posts.append((title,date_time,link,author,label))

        if date_time < end_date:
            break
        else:
            page += 1
    if len(posts)!=0:
        parse_info(posts,cate)

def extract_label(item):
    label = ''
    try:
        labels = item.find_all('div','tags_wrapper')[0].find_all('a')
        for l in labels:
            label += l.text+ ' '
    except:
        pass
    return label
        
def extract_title(item):
    try:
        title = item.find('h3','card_title').text
    except:
        title = ''
    return title

def extract_author(item):
    try:
        author = item.find('span','info_author').text
    except:
        author = ''
    return author

def extract_date(item):
    try:
        date_time = item.find('span','info_time').text
    except:
        date_time = ''
    return date_time

def extract_link(item):
    try:
        link = item.find('a','card_link link_title').get('href')
    except:
        link = ''
    return link

def parse_info(posts,cate):
    article = []
    for item in posts:
        title = item[0]
        date_time = item[1]
        link = item[2]
        author = item[3]
        label = item[4]
        
        res = requests.get(link,headers=headers)
        soup = BeautifulSoup(res.text,'lxml')

        content = extract_content(soup)
        keyword = extract_keyword(soup)

        article.append({'date_time':date_time,'author':author,'title':title,
                        'label':label,'link':link,'content':content,'keyword':keyword})

    article.sort(key=lambda x: x['date_time'],reverse=True)
    if len(article)!=0:
        write_to_json(article,cate)

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div',{'id':'CMS_wrapper'})[0].find_all('p')
        for c in contents:
            content += c.text
    except:
        pass
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div',{'id':'tags_list_wrapepr'})[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except:
        pass
    return keyword

def write_to_json(article,cate):
    #bulid folder by yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/Storm/{cate}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = 'storm_' + cate + time.strftime('%Y%m%d') + '.json'
    with open(folder_path+'/'+filename,'w',encoding='utf8') as jf:
        json.dump(article,jf,ensure_ascii=False,indent=2)
    jf.close()

if __name__ == '__main__':
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days = 1)
    end_date = (start_date - d).strftime('%Y-%m-%d %H:%M')
    
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
               "referer": "https://www.storm.mg/category"}
    cates = [('politics','https://www.storm.mg/category/118'),
             ('global','https://www.storm.mg/category/117'),
             ('domestic','https://www.storm.mg/category/22172'),
             ('finance','https://www.storm.mg/category/23083'),
             ('local','https://www.storm.mg/localarticles'),
             ('tech','https://www.storm.mg/technology'),
             ('health','https://www.storm.mg/life-category/s24252'),
             ('stylish','https://www.storm.mg/stylish-category')]
    
    for cate,cate1 in cates:
        url = cate1
        parse_cateurl(url,cate)
