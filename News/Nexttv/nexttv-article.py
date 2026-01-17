import requests
import json
from bs4 import BeautifulSoup
import datetime
import os
import time

def scrape_link(category,label,number):
    page = 1
    urls = []
    while True:
        page_link = 'http://www.nexttv.com.tw/m2o/loadmore.php'
        payload = {'offset' : 3+(page-1)*6, 'count' : 6, 'column_id' : number}
        res = requests.post(page_link,data=payload)
        for item in res.json():
            url = item['content_url']
            print(url)
            date = item['file_name'].split('/')[0]
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
    # 可自己調整
    folder_path = '/home/ftp_246/data_1/news_data/nexttv/urls/'+time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = f'nexttv-{category}-'+time.strftime('%Y-%m-%d') + '.txt'
    with open(folder_path+'/'+filename,'w',encoding='utf8') as txtf:
        for url in urls:
            txtf.write(url+'\n')
    txtf.close()
        
def scrape_content(label,urls):
    data_collect = []
    for url in urls:
        r = requests.get(url)
        r.encoding = 'utf8' # 避免亂碼出現
        soup = BeautifulSoup(r.text)        
        try:
            title = soup.find(class_='articletitle').text
            date = soup.find(class_='time').text
            content = soup.find(class_='article-main').text.strip()
            article = {'url':url,'title':title,'date':date,'label':label,'content':content}
            print(article)
            data_collect.append(article)
        except Exception as e:
            print(e)
    if len(data_collect)!=0:
        write_to_json(data_collect)

def write_to_json(data_collect):
    # 可自己調整
    folder_path = f'/home/ftp_246/data_1/news_data/nexttv/json/{category}/'+time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = f'nexttv-{category}-'+time.strftime('%Y-%m-%d') + '.json'
    with open(folder_path+'/'+filename,'w',encoding='utf8') as jf:
        json.dump(data_collect,jf,ensure_ascii=False,indent=2)
    jf.close()

if __name__=='__main__':
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days=1)
    end_date = (start_date - d).strftime('%Y-%m-%d')

    categories = [('politics', '政治',144),
                  ('society' , '社會',145),
                  ('finance' , '財經',147),
                  ('world'   , '國際',148),
                  ('life'    , '生活',149)]

    for category, label,number in categories:
        scrape_link(category,label,number)
