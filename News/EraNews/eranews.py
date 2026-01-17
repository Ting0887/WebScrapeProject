import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
import os

requests.packages.urllib3.disable_warnings()

def eranews(url):
    newslink = []
    page = 19
    for num in range(0,page+1):
        cate_url = url + f'/?pp={num}0'
        res = requests.get(cate_url,verify=False)
        res.encoding = 'utf8'
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.find_all('p','tib-title')
        for item in items:
            link = item.find('a')['href']
            date_f = link.split('/')[-2]
            if date_f < end_date:
                break
            else:
                print(link)
                newslink.append(link)
        if date_f < end_date:
                break

    if len(newslink)!=0:
        parse_article(newslink)

def parse_article(newslink):
    eradata = []
    for link in newslink:
        res = requests.get(link,verify=False)
        res.encoding = 'utf8'
        if res.status_code == requests.codes.ok:
            soup = BeautifulSoup(res.text,'lxml')
            items = soup.select('.cell_416_')
            for item in items:
                try:
                    title = item.find('h1').text
                    print(title)
                except:
                    title = ''
                try:
                    date_time = item.find('span','time').text
                except:
                    date_time = ''
                label = cate1
                try:
                    content = item.find('div','article-main').text
                except:
                    content = ''
                
                keyword = ''

                eradata.append({'date_time':date_time,
                                'title':title,
                                'link':link,
                                'label':label,
                                'content':content,      
                                'keyword':keyword})
    if len(eradata)!=0:
        outputjson(eradata)

def outputjson(eradata):
    #bulid folder by yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/era_news/{cate2}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = 'era_' + cate2 + time.strftime('%Y%m%d') + '.json'
    with open(folder_path +'/'+filename,'w',encoding='utf8') as jf:
        json.dump(eradata,jf,ensure_ascii=False,indent=2)
    jf.close()
    
if __name__ == '__main__':
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days=1)
    end_date = (start_date - d).strftime('%Y-%m-%d')

    #categories
    cates = {('political','政治','politic'),
              ('Society','社會','society'),
              ('WorldNews','國際','global'),
              ('Life','生活','life'),
              ('Finance','財經','finance')}
    
    for cate,cate1,cate2 in cates:
        url = f'http://www.eracom.com.tw/EraNews/Home/{cate}/'   
        eranews(url)


