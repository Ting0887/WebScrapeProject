import requests
from bs4 import BeautifulSoup
import datetime
import time
import os
import json

def scrape_link(category):
    urls = []
    page = 1
    while True:
        page_link = f'https://www.thenewslens.com/category/{category}?page={page}'
        res = requests.get(page_link)
        soup = BeautifulSoup(res.text,'lxml')
        print(page_link)
        all_containers = set(soup.select('.list-container'))
        sponsored_containers = set(soup.select('.sponsoredd-container'))
        containers = all_containers - sponsored_containers

        for item in containers:
            link = item.find('a')['href'] 
            if '/feature/' in link:
                continue
            date_time = item.find('span','time').text.replace('|','').replace('/','-').strip()
            if len(date_time)!=10:
                continue
            print(date_time)
            if date_time < end_date:
                break
            else:
                urls.append(link)
                print(link)
        if date_time < end_date:
            break
        else:
            page += 1

    if len(urls)!=0:
        write_to_txt(category,urls)
        scrape_content(category,urls)

def write_to_txt(category,urls):
    #bulid folder yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/TheNewsLens/urls/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = f'tnl-{category}-'+ time.strftime('%Y-%m-%d') + '.txt'
    with open(folder_path+'/'+filename,'w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url+'\n')
    txtf.close()

def scrape_content(category,urls):
    data_collect = []
    for url in urls:
        try:
            soup = BeautifulSoup(requests.get(url).text,'lxml')
            title = soup.find(class_='article-title').text.strip()
            info = soup.find(class_='article-info').text.strip().split(', ')
            date = info[0]
            if 'Sponsored' in date:
                continue
            label = info[1]

            summary = soup.find(class_='WhyNeedKnow').p.text.strip()
            content = ''.join(p.text for p in soup.select('.article-content > p'))
            # Not all articles have tags/keywords
            keywords = []
            try:
                for a in soup.find(class_='tags').select('a'):
                    keywords.append(a.text)
            except:
                pass
            article = {'url':url,'title':title,'date':date,
                       'label':label,'summary':summary,
                       'content':content,'keywords':keywords}
            data_collect.append(article)
        except Exception as e:
            print(e)
            pass

    if len(data_collect)!=0:
        write_to_json(category,data_collect)

def write_to_json(category,data_collect):
    #bulid folder yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/TheNewsLens/json/{category}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = f'tnl-{category}-'+ time.strftime('%Y-%m-%d') + '.json'
    with open(folder_path+'/'+filename,'w',encoding='utf-8') as jf:
        json.dump(data_collect,jf,ensure_ascii=False,indent=2)
    jf.close()

if __name__ == '__main__':
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days=7)
    end_date = (start_date - d).strftime('%Y-%m-%d')
    print(end_date)
    categories = ['world','china','health',
                  'lifestyle','politics','economy',
                  'society','science','tech']

    for category in categories:
        scrape_link(category)

