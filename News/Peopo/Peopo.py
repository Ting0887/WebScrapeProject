import os
import datetime
import time
import json
import requests
from bs4 import BeautifulSoup

def select_date(url):
    num = 0
    collect_data = []
    while True:
        base_url = url + c2 + '?g=' + c1 + '&page=' + str(num)
        print(base_url)
        res = requests.get(base_url)
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.find_all('div','view-content')[0].find_all('div','views-row')
        for item in items:
            date_time = item.find('div','view-list-date').text
            author = item.find('span','author-name').text
            title = item.find('h3','view-list-title').text
            link = 'https://www.peopo.org' + item.find('h3','view-list-title').a.get('href')
            if date_time < end_date:
                break
            else:
                collect_data.append((date_time,author,title,link))
        if date_time < end_date:
            break
        else:
            num += 1
    if len(collect_data)!=0:
        extract_data(collect_data)

def extract_data(collect_data):
    article =[]
    for item in collect_data:
        try:
            date_time = item[0]
            author = item[1]
            title = item[2]
            link = item[3]
        except:
            pass
        res = requests.get(link)
        soup = BeautifulSoup(res.text,'lxml')
        content = ''
        try:
            contents = soup.find_all('div',{'id':'text-resize'})[0].find_all('p')
            for c in contents:
                content += c.text.replace('\t','').replace('\n','')
                if '延伸閱讀：' in c.text:
                    continue
        except:
            continue
        
        keyword = ''
        try:
            keywords = soup.find_all('ul','inline')[0].find_all('a')
            for k in keywords:
                keyword += k.text + '、'
        except:
            print('no keyword')
            
        article.append({'title':title,'author':author,'date_time':date_time,
                        'content':content,'keyword':keyword[:-1],'newslink':link,
                        'label':c1,'website':'Peopo公民新聞'})

        article.sort(key=lambda x: x['date_time'],reverse=False)
    if len(article)!=0:
        write_to_json(article)

def write_to_json(article):
    #bulid folder by yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/Peopo/{c3}/'  + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = 'Peopo_' + c3 + time.strftime('%Y%m%d') + '.json'
    with open(folder_path +'/'+filename,'w',encoding='utf8') as f:
        json.dump(article,f,ensure_ascii=False,indent=2)
    f.close()

if __name__ == '__main__':
    start_date = datetime.datetime.today()
    months = datetime.timedelta(days=1)
    end_date = (start_date - months).strftime('%Y-%m-%d')
    url = 'https://www.peopo.org/tag/'
    category = [
                ('社會關懷','28916%2B2','society'),
                ('政治經濟','25038%2B26995%2B27109%2B11','politics'),
                ('運動科技','25034%2B25682%2B567%2B10','tech'),
                ('生活休閒','24961%2B24943%2B43828%2B8','life')
                ]
    url = 'https://www.peopo.org/tag/'
    for c1,c2,c3 in category:
        select_date(url)
        
