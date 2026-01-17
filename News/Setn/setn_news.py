import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
import os

def Setn(url,cate,cate1):
    article = []
    # total 20 pages
    for num in range(1,21):
        page_url = url+ '&p=' + str(num)
        res = requests.get(page_url)
        print(page_url)
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.find_all('div','col-sm-12 newsItems')
        for item in items:
            label = extract_label(item)
            title = extract_title(item)
            link = extract_link(item)
            
            res = requests.get(link)
            soup = BeautifulSoup(res.text,'lxml')

            date_time = extract_date(soup)
            content = extract_content(soup)
            keyword = extract_keyword(soup)
            
            if date_time < end_date:
                break
            else:
                article.append({'date_time':date_time,'title':title,'label':label,
                                'link':link,'content':content,'keyword':keyword})
        if date_time < end_date:
            break
    
    if len(article)!=0:
        outputjson(article)

def extract_label(item):
    #label
    try:
        label = item.find('a').text
    except:
        label = ''
    return label

def extract_title(item):
    #title
    try:
        title = item.find('h3','view-li-title').text
    except:
        title = ''
    return title

def extract_link(item):
    #link
    try:
        link = 'https://www.setn.com' + item.find('h3','view-li-title').a.get('href')
    except:
        link = ''
    return link

def extract_date(soup):
    try:
        date_time = soup.find('time','page-date').text
    except:
        date_time = ''
    return date_time

def extract_content(soup):
    content = ''
    try:
        contents = soup.select('article')[0].find_all('p')
        for c in contents:
            content += c.text.replace('\n','').replace('\r','')
    except:
        pass
    return content
            
def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','keyword page-keyword-area')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except:
        pass
    return keyword

def outputjson(article):
    ##bulid folder by yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/Setn/{cate}/'+time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = 'setn_' + cate + time.strftime('%Y%m%d') + '.json'
    with open( folder_path + '/' + filename,'w',encoding='utf8') as jf:
        json.dump(article,jf,ensure_ascii=False,indent=2)
    jf.close()
    
if __name__ == '__main__':
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days=1)
    end_date = (start_date - d).strftime('%Y/%m/%d')

    cates = {('politics','6'),('society','41'),('global','5'),
            ('life','4'),('health','65'),('finance','2'),('technology','7')}

    for cate,cate1 in cates:
        url = f'https://www.setn.com/ViewAll.aspx?PageGroupID={cate1}'
        Setn(url,cate,cate1)
