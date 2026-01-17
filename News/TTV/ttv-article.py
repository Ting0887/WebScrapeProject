import requests
from bs4 import BeautifulSoup
import datetime
import time
import os
import json

def scrape_link(label,category):
    urls = []
    page = 1
    while True:
        page_link = f"https://news.ttv.com.tw/category/{label}/{page}"
        res = requests.get(page_link)
        print(page_link)
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.select('.news-list li')

        for item in items:
            link = item.find('a')['href']
            date = item.find('div','time').text.replace('.','-')
            print(link)
            print(date)

            if date < end_date:
                break
            else:
                urls.append(link)
        if date < end_date:
            break
        page += 1
    if len(urls)!=0:
        write_to_txt(category,urls)
        scrape_content(urls)

def write_to_txt(category,urls):
    folder_path =  '/home/ftp_246/data_1/news_data/TTV/urls/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(folder_path + '/'+f'ttv-{category}-urls_'+time.strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url+'\n')
    txtf.close()

def scrape_content(urls):
    data_collect = []
    for url in urls:
        try:
            res = requests.get(url)
            res.encoding = 'utf8'
            soup = BeautifulSoup(res.text,'lxml')

            title = soup.find('h1').text.strip()
            date = soup.find(class_='date time').text.strip()
            newslabel = soup.find('div', {'id': 'crumbs'}).find_all('li')[1].text
            content = soup.find('div', {'id': 'newscontent'}).text.strip()
            try:
                keywords = [a.text for a in soup.select('.news-status > .tag > li')]
            except:
                pass
            article = {'url':url,'title':title,'date':date,
                       'label':newslabel,'content':content,'keywords':keywords}
            print(article)
            data_collect.append(article)

        except Exception as e:
            print(e)
            pass

    if len(data_collect)!=0:
        write_to_json(data_collect)

def write_to_json(data_collect):
    folder_path =  f'/home/ftp_246/data_1/news_data/TTV/{category}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = f'ttv-{category}-'+time.strftime('%Y-%m-%d')+'.json'
    with open(folder_path +'/'+ filename,'w',encoding='utf-8') as jf:
        json.dump(data_collect,jf,ensure_ascii=False,indent=2)
    jf.close()

if __name__ == '__main__':
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days=1)
    end_date = (start_date - d).strftime('%Y-%m-%d')

    categories = [('政治', 'politics'),
                  ('財經', 'finance'),
                  ('社會', 'society'),
                  ('國際', 'world'),
                  ('生活', 'life'),
                  ('健康', 'health')]

    for label,category in categories:
        scrape_link(label,category)
