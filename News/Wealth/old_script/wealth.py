import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
import os

def select_date(label,number_id,category):
    num = 1
    urls = []
    while True:
        base_url = url + 'category_id=' + number_id + '&page=' + str(num)
        res = requests.get(base_url)
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.find_all('div','entry-main')
        for item in items:
            date_time = item.find('div','entry-meta').select('.entry-meta__item')[0].text.strip()
            author = item.find('div','entry-meta').select('.entry-meta__item')[1].text.strip()
            link = 'https://www.wealth.com.tw' + item.find('a')['href']
            if date_time < end_date:
                break
            else:
                urls.append((link,date_time,author))

        if date_time < end_date:
            break 
        num += 1
    if len(urls)!=0:
        extract_data(label,urls)

def extract_data(label,urls):
    article = []
    for item in urls:
        link = item[0]
        date_time = item[1]
        author = item[2]

        res = requests.get(link)
        soup = BeautifulSoup(res.text,'lxml')
        try:
            title = soup.find('h1','entry-title').text.replace('\r','').strip()
        except:
            title = ''
        
        content = ''
        try:
            contents = soup.find_all('div',{'id':'cms-article'})[0].find_all('p')
            for con in contents:
                content += con.text.replace('\n','').replace('\r','')
                if '延伸閱讀：' in con.text:
                    continue
        except:
            continue

        keyword = ''
        try:
            keywords = soup.find_all('p','f-s14')[0].find_all('a')
            for k in keywords:
                keyword += k.text + '、'
        except:
            print('no keyword')

        article.append({'title':title,
                        'author':author,
                        'date_time':date_time,
                        'link':link,
                        'label':label,
                        'website':'財訊',
                        'content':content,
                        'keyword':keyword[:-1]
                        })
    if len(article)!=0:
        write_to_json(article)

def write_to_json(article):
    #bulid folder by yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/wealth/{category}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = 'wealth_' + category + time.strftime('%Y%m%d') + '.json'
    with open(folder_path + '/' + filename,'w',encoding='utf8') as jf:
        json.dump(article,jf,ensure_ascii=False,indent=2)
    jf.close()

if __name__ == '__main__':
    start_date = datetime.datetime.today() #today
    months = datetime.timedelta(days=1)  #last month
    end_date = (start_date - months).strftime('%Y-%m-%d') 
    print(end_date)
    categories = [ 
                ('焦點新聞-國際','1','global'),
                ('財經動態','3','finance'),
                ('政治風雲','2','politics'),
                ('科技風雲','11','tech'),
                ('生技醫療','13','biotech_medical')
                ]
    url = 'https://www.wealth.com.tw/home/articles?'
    for label,number_id,category in categories:
        select_date(label,number_id,category)

