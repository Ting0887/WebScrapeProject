import requests
from bs4 import BeautifulSoup
import os
import json
import datetime
import time

def scrape_link(url):
    page = 1
    urls = []
    while True:
        url = f'https://daaimobile.com/api/news?size=500&page={page}&order=createdAt&desc=true&detail=undefined&onShelf=true'
        try:
            res = requests.get(url)
            r = res.json()['rows']
            for item in r:
                title = item['title']
                date_time = item['createdAt']
                link = 'https://daaimobile.com/news/'+item['_id']
                if date_time < end_date:
                    break
                else:
                    print(link)
                    urls.append((title,link,date_time))
            if date_time < end_date:
                break
            else:
                page += 1
        except Exception as e:
            print(e)
    if len(urls)!=0:
        scrape_content(urls)

def scrape_content(urls):
    data_collect = []
    for item in urls:
        title = item[0]
        link = item[1]
        date_time = item[2]
        try:
            res = requests.get(link)
        except:
            continue
        soup = BeautifulSoup(res.text,'lxml')
        try:
            content = soup.find('div','description').text.replace('\n','').strip()
        except:
            content = ''

        data_collect.append({'date_time':date_time,'title':title,
                             'label':'即時新聞','link':link,
                             'content':content,'keyword':''})
    if len(data_collect)!=0:
        write_to_json(data_collect)

def write_to_json(data_collect):
    #bulid folder by yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/Daai/realtime/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = 'Daai_realtime' + time.strftime('%Y%m%d') + '.json'
    with open(folder_path + '/' + filename,'w',encoding='utf8') as jf:
        json.dump(data_collect,jf,ensure_ascii=False,indent=2)
    jf.close()

if __name__ == '__main__':
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days = 1)
    end_date = (start_date - d).strftime('%Y/%m/%d')

    url = 'https://daaimobile.com/api/news?size=500&page=1&order=createdAt&desc=true&detail=undefined&onShelf=true'
    scrape_link(url)
