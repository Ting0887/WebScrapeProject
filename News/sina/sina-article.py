import requests
import time
import datetime
import os
from bs4 import BeautifulSoup
import json

def scrape_link(category,label,start_date,end_date):   
    urls = []
    while start_date.strftime('%Y%m%d') > end_date:
        page = 1
        while True:
            page_link = f'https://news.sina.com.tw/realtime/{category}/tw/'+\
                start_date.strftime('%Y%m%d')+'/list-'+str(page)+'.html'           
            time.sleep(3)
            res = requests.get(page_link)
            soup = BeautifulSoup(res.text,'lxml')
            try:
                items = soup.find_all('ul','realtime')[0].find_all('a')
                if len(items) == 0:
                    break
                else:
                    page += 1
                    print(page_link)
                for item in items:
                    link = 'https://news.sina.com.tw' + item['href']
                    urls.append(link)
                    
            except:
               break
        start_date -= delta
    if len(urls)!=0:
        write_to_txt(category,urls)
        scrape_content(label,urls)
        
def write_to_txt(category,urls):
    folder_path = f'/home/ftp_246/data_1/news_data/sina/{category}/urls'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    filename = f'sina-{category}-urls-'+time.strftime('%Y-%m-%d')+'.txt'
    with open(folder_path+'/'+filename,'w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url+'\n')
    txtf.close()

def scrape_content(label,urls):
    data_collect = []
    for url in urls:
        soup = BeautifulSoup(requests.get(url).text,'lxml')
        time.sleep(3)
        try:
            title = soup.find('h1').text.strip()
            source = soup.find('cite').a.text
            date = soup.find('cite').text.strip()\
                              [len(source):]\
                              .strip()\
                              .lstrip('(')\
                              .rstrip(')')
        except:
            pass
        
        try:
            content = soup.find(class_='pcont').text.replace('\n','').replace('\t','').strip()
        except:
            content = ''
        article = {'url':url,'title':title,
                   'source':source,'date':date,
                   'label':label,'content':content}
        print(article)
        data_collect.append(article)
    if len(data_collect)!=0:
        write_to_json(data_collect)

def write_to_json(data_collect):
    folder_path = f'/home/ftp_246/data_1/news_data/sina/{category}/'+time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = f'sina-{category}-'+time.strftime('%Y-%m-%d')+'.json'
    with open(folder_path+'/'+filename,'w',encoding='utf-8') as jf:
        json.dump(data_collect,jf,ensure_ascii=False,indent=2)
    jf.close()
                        
if __name__ == '__main__':
    #startdate enddate
    start_date = datetime.datetime.strptime(time.strftime('%Y%m%d'),'%Y%m%d')
    
    ten_days = datetime.timedelta(days=2)
    delta = datetime.timedelta(days=1)
    end_date = (start_date - ten_days).strftime('%Y%m%d')
    print(end_date)
    categories = [('politics', '政治'),
                  ('society' , '社會'),
                  ('china'   , '兩岸'),
                  ('global'  , '國際'),
                  ('life'    , '生活'),
                  ('finance' , '財經'),
                  ('tech'    , '科技')]
    for category,label in categories:
        scrape_link(category,label,start_date,end_date)

