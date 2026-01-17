import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
import os

def scrape_link(url_cate,label,category):
    urls = []
    page = 1
    while True:
        page_link = f'https://www.ntdtv.com/b5/{url_cate}/{page}'
        print(page_link)
        res = requests.get(page_link)
        if res.status_code != 200:
            break
        soup = BeautifulSoup(res.text,'lxml')
        for h in soup.select('.post_list .text'):
            url = h.find(class_='title').a['href']
            
            #get date
            y = url.split('/b5/')[-1].split('/')[0]
            m = url.split('/b5/')[-1].split('/')[1]
            d = url.split('/b5/')[-1].split('/')[2]
            date = y+'-'+m+'-'+d
            print(url)
            if date < end_date:
                break
            urls.append(url)
        if date < end_date:
            break
        else:
            page += 1

    if len(urls)!=0:
        write_to_txt(category,urls)
        scrape_content(label,urls)

def write_to_txt(category,urls):
    folder_path = f'/home/ftp_246/data_1/news_data/ntdtv/urls/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = f'ntdtv-{category}-urls-' + time.strftime('%Y-%m-%d') + '.json'
    with open(folder_path+'/'+filename,'w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url+'\n')
    txtf.close()

def scrape_content(label,urls):
    data_collect = []
    for url in urls:
        soup = BeautifulSoup(requests.get(url).text,'lxml')
        try:
            title = soup.find(class_='article_title').h1.text
            date = soup.find(class_='time').span.text
            contents = soup.find(class_='post_content').find_all('p')
            content_strings = [x.text.strip() for x in contents]
            content = ''.join(content_strings)
            article = {'url':url,'title':title,'date':date,'label':label,'content':content}
            print(article)
            data_collect.append(article)
        except Exception as e:
            print(e)
            pass
    if len(data_collect)!=0:
        write_to_json(data_collect)

def write_to_json(data_collect):
    folder_path = f'/home/ftp_246/data_1/news_data/ntdtv/json/{category}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = f'ntdtv-{category}-' + time.strftime('%Y-%m-%d') + '.json'
    with open(folder_path+'/'+filename,'w',encoding='utf-8') as jf:
        json.dump(data_collect,jf,ensure_ascii=False,indent=2)
    jf.close()

if __name__ == '__main__':
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days=1)
    end_date = (start_date - d).strftime('%Y-%m-%d')
    
    categories = [('prog202', '國際', 'world'),
                  ('prog204', '大陸', 'china'),
                  ('prog203', '美國', 'usa'),
                  ('prog206', '台灣', 'taiwan'),
                  ('prog205', '港澳', 'hk'),
                  ('prog208', '財經', 'finance'),
                  ('prog1255', '健康', 'health')]

    for url_cate, label,category in categories:
        scrape_link(url_cate,label,category)
