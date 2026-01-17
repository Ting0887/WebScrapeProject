import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
import os

def parse_cateurl(cate,cate1,url):
    num = 1
    article = []
    while True:
        time.sleep(1)
        payloads = {'cate_code': cate1,
                    'exclude':'295762,295760,295759,295752,295748',
                    'page': num}

        res = requests.post(url,data=payloads,headers=headers)
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.find_all('div','white-box news-list-area')[0].find_all('div','style1 white-box')
        for item in items:
            link = extract_newslink(item)
            print(link)
            res = requests.get(link,headers=headers)
            soup = BeautifulSoup(res.text,'lxml')
            time.sleep(0.5)

            title = extract_title(soup)
            date_time = extract_date(soup)
            content = extract_content(soup)
            keyword = extract_keyword(soup)
            post = {'date_time':date_time,'title':title,'label':cate,
                        'link':link,'content':content,'keyword':keyword}
            print(post)
            article.append(post)
        if date_time < end_date:
            break
        else:
            num += 1
    if len(article)!=0:
        write_to_json(article,cate1)

def extract_newslink(item):
    try:
        link = 'https://news.ebc.net.tw' + item.find('a')['href']
    except:
        link = ''
    return link

def extract_title(soup):
    try:
        title = soup.find('h1').text
    except:
        title = ''
    return title

def extract_date(soup):
    try:
        date_time = soup.find('span','small-gray-text').text[0:17]
    except:
        date_time = ''
    return date_time
        
def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div','raw-style')[0].find_all('p')
        for c in contents:
            content += c.text.replace('\n','').replace('\r','')
    except Exception as e:
        pass    
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','keyword')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except Exception as e:
        pass
    return keyword
            
def write_to_json(article,cate1):
    #bulid folder by yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/EBC/{cate1}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = 'ebc_' + cate1 + time.strftime('%Y%m%d') + '.json'
    with open(folder_path +'/'+filename,'w',encoding='utf8') as jf:
        json.dump(article,jf,ensure_ascii=False,indent=2)
    jf.close()
    
if __name__ == '__main__':
    start_date = datetime.datetime.today() #today
    months = datetime.timedelta(days=1)  #last month
    end_date = (start_date - months).strftime('%Y/%m/%d') 
    
    url = 'https://news.ebc.net.tw/News/List_Category_Realtime'
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
               ,'x-requested-with': 'XMLHttpRequest'}

    cates = [('政治','politics'),('社會','society'),
             ('國際','world'),('生活','living'),
             ('財經','business'),('健康','health')]
    for cate,cate1 in cates:
        parse_cateurl(cate,cate1,url)
