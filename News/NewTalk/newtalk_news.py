import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
import os

def Newtalk(url):
    news_link = []
    page = 15
    for num in range(1,page+1):
        base_url = url + f'/{num}'
        print(base_url)
        time.sleep(2.5)
        res = requests.get(base_url,headers=headers)
        res.encoding = 'utf8'
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.find_all('div',{'id':'category'})[0].find_all('div','news-list-item clearfix')
        for item in items:
            link = item.find('a')['href']
            if 'plan' in link:
                continue
            print(link)
            date_f = link.split('/view/')[-1].split('/')[0]
            if date_f < end_date:
                break
            else:
                news_link.append(link)
        if date_f < end_date:
            break
    if len(news_link)!=0:
        parse_article(news_link)

def parse_article(news_link):
    article = []
    for link in news_link:
        time.sleep(2.6)
        try:
            res = requests.get(link,headers=headers)
            res.encoding = 'utf8'
        except:
            continue
        soup = BeautifulSoup(res.text,'lxml')
        try:
            title = soup.find('h1').text
        except:
            title = ''
        
        try:
            date_time = soup.find('div','content_date').text\
                .replace('發布','').replace('|','').strip()
        except:
            date_time = ''

        label = cate
        try:
            content = ''
            contents = soup.find_all('div',{'itemprop':'articleBody'})[0].find_all('p')
            for c in contents:
                content += c.text
        except:
            continue
        
        try:
            keyword = ''
            keywords = soup.find_all('div','keyword_tag')[0].find_all('a')
            for k in keywords:
                keyword += k.text + ' '
        except:
            continue
        
        article.append({'date_time':date_time,'title':title,'label':label,
                        'link':link,'content':content,'keyword':keyword})

    if len(article) !=0:
        outputjson(article)
def outputjson(article):
    #bulid folder yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/NewTalk/{cate2}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = 'newtalk_' + cate2 + time.strftime('%Y%m%d') + '.json'
    with open(folder_path + '/' + filename,'w',encoding='utf8') as jf:
        json.dump(article,jf,ensure_ascii=False,indent=2)
    jf.close()
    
if __name__ == '__main__':
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"}
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days = 1)
    end_date = (start_date - d).strftime('%Y-%m-%d')

    cates = [('政治','2','politics'),('社會','14','society'),
             ('國際','1','global'),('生活','5','life'),
             ('財經','3','finance'),('科技','8','tech')]

    for cate,cate1,cate2 in cates:    
        url = f'https://newtalk.tw/news/subcategory/{cate1}/{cate}'
        Newtalk(url)
