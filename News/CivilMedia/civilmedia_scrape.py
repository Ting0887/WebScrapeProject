import time
import datetime
import os
import json
import requests
from bs4 import BeautifulSoup

def scrape_link(url,cate,folder):
    page = 1
    newslink = []
    while True:
        link = url + '/page/' + str(page)
        res = requests.get(link)
        soup = BeautifulSoup(res.text,'lxml')
        article_bar = soup.select('section')[0].find_all('div','post-box one-half')
        for item in article_bar:
            try:
                link = item.find('a')['href']
            except:
                link = ''
            try:
                date_time = item.find('div','entry-meta').text
            except:
                date_time = ''
            print(date_time)
            if date_time < end_date:
                break
            elif link != '':
                newslink.append(link)

        if date_time < end_date:
            break
        else:
            page += 1
    if len(newslink)!=0:
        scrape_content(newslink)

def scrape_content(newslink):
    article = []
    for link in newslink:
        res = requests.get(link)
        soup = BeautifulSoup(res.text,'lxml')
        try:
            title = soup.find('h1').text
        except:
            title = ''
        try:
            date_time = soup.find_all('div','entry-meta clearfix')[0].text[:11].replace('\n','').strip()
        except:
            date_time = ''

        content = ''
        try:
            contents = soup.find_all('section','entry-content clearfix')[0].find_all('p')
            for c in contents:
                content += c.text + ' '
        except:
            pass

        keyword = ''
        try:
            keywords = soup.find_all('a',{'rel':'tag'})
            for k in keywords:
                keyword += k.text + ' '
        except:
            pass

        article.append({'date_time':date_time,
                        'author':'',
                        'title':title,
                        'label':cate,
                        'link':link,
                        'content':content,
                        'keyword':keyword})
    if len(article)!=0:
        write_to_json(article)

def write_to_json(article):
    #bulid folder by yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/civilmedia/{folder}/'+ time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(folder_path+'/'+'civilmedia_'+folder+time.strftime('%Y%m%d')+'.json','w')  as f:
        json.dump(article,f,ensure_ascii=False,indent=2)
    f.close()

if __name__ == '__main__':
    #start date , end date
    start_date = datetime.datetime.today() #today
    months = datetime.timedelta(days=1)  #last month
    end_date = (start_date - months).strftime('%Y-%m-%d')
    print(end_date)
    
    #categories
    cate_url = [('https://www.civilmedia.tw/archives/category/environment','環境','environment'),
                ('https://www.civilmedia.tw/archives/category/%e4%ba%ba%e6%ac%8a','人權','humanrights'),
                ('https://www.civilmedia.tw/archives/category/%e5%8b%9e%e5%b7%a5','勞工','labor'),
                ('https://www.civilmedia.tw/archives/category/aborigines','原民','aborigine'),
                ('https://www.civilmedia.tw/archives/category/migrant','移民','migrant')]

    for url,cate,folder in cate_url:
        scrape_link(url,cate,folder)
