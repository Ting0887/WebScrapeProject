import os
import datetime
import time
import json
import requests
from bs4 import BeautifulSoup

def scrape_link(label,url,foldername):
    newsdata = []
    page = 1
    while True:
        page_url = url + '/page/' + str(page)
        res = requests.get(page_url)
        soup = BeautifulSoup(res.text,'lxml')
        bar = soup.find_all('div','tipi-row content-bg clearfix')[0].find_all('div','preview-mini-wrap clearfix')
        for item in bar:
            try:
                title = item.find('h3','title').text
            except:
                title = ''
            try:
                link = item.find('h3','title').a.get('href')
            except:
                link = ''
            try:
                date_time = item.find('time')['datetime'][:10]
            except:
                date_time = ''

            if link != '' and date_time >= end_date:
                newsdata.append((title,link,date_time))
            print(link)
        if date_time < end_date:
            break
        else:
            page += 1
        
        # if end page ,break
        mes = soup.find('h1').text
        if '不好意思呢，找不到這個頁面' in mes:
            break
    if len(newsdata)!=0:
        scrape_content(label,newsdata,foldername)

def scrape_content(label,newsdata,foldername):
    article = []
    for item in newsdata:
        title = item[0]
        link = item[1]
        date_time = item[2]

        res = requests.get(link)
        soup = BeautifulSoup(res.text,'lxml')
        try:
            author = soup.find('span','byline-part author').text
        except:
            author = ''

        content = ''
        try:
            content = soup.find('div','entry-content').text.replace('\n','')
            content.split('延伸閱讀')[0]
        except:
            print('no content!')
        
        keyword = ''
        try:
            keywords = soup.find_all('div','post-tags')[0].find_all('a')
            for k in keywords:
                keyword += k.text.replace('\n','').strip() + ' '
        except:
            print('no keyword')

        article.append({'title':title,
                        'author':author,
                        'date_time':date_time,
                        'label':label,
                        'link':link,
                        'content':content,
                        'keyword':keyword})
        print(article)

    if len(article)!=0:
        write_to_json(article,foldername)

def write_to_json(article,foldername):
    folder_path = f'/home/ftp_246/data_1/news_data/Newsmarket/{foldername}'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = f'newsmarket_{foldername}'+time.strftime('%Y%m%d')+'.json'
    with open(folder_path +'/'+ filename,'w',encoding='utf-8')  as jf:
        json.dump(article,jf,ensure_ascii=False,indent=2)
    jf.close()

if __name__ == '__main__':
    #start date end date
    start_date = datetime.datetime.today() #today
    months = datetime.timedelta(days=1)  #last month
    end_date = (start_date - months).strftime('%Y-%m-%d') 
    print(end_date)

    categories = [
                ('時事-政策','https://www.newsmarket.com.tw/blog/category/news-policy','news-policy'),
                ('食安','https://www.newsmarket.com.tw/blog/category/food-safety','food-safety'),
                ('新知','https://www.newsmarket.com.tw/blog/category/knowledge','knowledge'),
                ('綠生活-旅遊-國際通信','https://www.newsmarket.com.tw/blog/category/living-green-travel','living-green-travel')
                ]
    for label,url,foldername in categories:
        scrape_link(label,url,foldername)
