import requests
from bs4 import BeautifulSoup
import time
import datetime
import os
import json

def scrape_link(start_date,end_date,label,category):
    urls = []
    while str(start_date) > end_date:
        page_link = f'https://news.tvbs.com.tw/realtime/{category}'+'/'+str(start_date.strftime('%Y-%m-%d'))
        res = requests.get(page_link)
        soup = BeautifulSoup(res.text,'lxml')
        print(page_link)
        for item in soup.find_all('li'):
            try:
                title = item.find('h2').text
                link = 'https://news.tvbs.com.tw'+item.find('a')['href']
                print(link)
                urls.append((title,link))
            except:
                pass
        start_date -= delta
    if len(urls)!=0:
        write_to_txt(category,urls)
        scrape_content(label,urls)

def write_to_txt(category,urls):
    folder_path =  '/home/ftp_246/data_1/news_data/TVBS/urls/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    with open(folder_path + '/'+f'tvbs-{category}-urls_'+time.strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url[1]+'\n')
    txtf.close()

def scrape_content(label,urls):
    data_collect = []
    for item in urls:
        title = item[0]
        url = item[1]
        
        res = requests.get(url)
        soup = BeautifulSoup(res.text,'lxml')
        
        datestr = soup.find(class_='author').text
        if '最後更新時間' in datestr:
            date = datestr.split('最後更新時間：')[1].strip()
        else:
            date = datestr.split('發佈時間：')[1].strip()

        stopstrings = ['&nbsp',
                       '最HOT話題在這！想跟上時事，快點我加入TVBS新聞LINE好友！',
                       '～開啟小鈴鐺',
                       'TVBS YouTube頻道',
                       '新聞搶先看',
                       '快點我按讚訂閱',
                       '～',
                       '55直播線上看',
                       '現正直播']
        content = ''.join(s for s in soup.find(class_='article_content').stripped_strings if s not in stopstrings)

        try:
            keywords = [a.text.lstrip('#') for a in soup.select_one('.article_keyword')]
        except:
            pass
        article = {'url':url,'title':title,'date':date,'label':label,'content':content,'keywords':keywords}
        print(article)
        data_collect.append(article)
    if len(data_collect)!=0:
         write_to_json(category,data_collect)


def write_to_json(category,data_collect):
    folder_path =  f'/home/ftp_246/data_1/news_data/TVBS/{category}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    with open(folder_path +'/'+ f'tvbs-{category}-'+time.strftime('%Y-%m-%d')+'.json','w',encoding='utf-8') as jf:
        json.dump(data_collect,jf,ensure_ascii=False,indent=2)
    jf.close()


if __name__ == '__main__':
    start_date = datetime.datetime.strptime(time.strftime('%Y-%m-%d'),'%Y-%m-%d')
    oneday = datetime.timedelta(days=1)
    delta = datetime.timedelta(days=1)
    end_date = (start_date - oneday).strftime('%Y-%m-%d')
    print(start_date)
    categories = [('要聞', 'politics'),
                  ('社會', 'local'),
                  ('全球', 'world'),
                  ('健康', 'health'),
                  ('理財', 'money'),
                  ('科技', 'tech'),
                  ('生活', 'life')]
    for label,category in categories:
        scrape_link(start_date,end_date,label,category)
