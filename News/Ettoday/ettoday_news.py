import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
import os

def parse_cateurl(url,start_date,end_date,cate,cate1,cate2):
    newslink = set()
    while str(start_date) > end_date:
        baseurl = url + str(start_date) + '-' + cate1 +'.htm'
        res = requests.get(baseurl)
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.find_all('div','part_list_2')[0].find_all('h3')
        for item in items:
            link = 'https://www.ettoday.net' + item.find('a')['href']
            print(link)
            date_f = link.split('/news/')[-1].split('/')[0]
            date_f = datetime.datetime.strptime(date_f,'%Y%m%d').strftime('%Y-%m-%d')
            if date_f < end_date:
                break
            else:
                newslink.add(link)
        if date_f < end_date:
            break
            
        start_date -= delta
    parse_info(sorted(newslink,reverse=False),cate,cate2)

def parse_info(urls,cate,cate2):
    data_collect = []
    for link in urls:
        time.sleep(1)
        try:
            res = requests.get(link)
        except:
            continue
        soup = BeautifulSoup(res.text,'lxml')

        title = extract_title(soup)
        date_time = extract_date(soup)
        content = extract_content(soup)
        keyword = extract_keyword(soup)

        article  = {'date_time':date_time,'title':title,
                    'link':link,'label':cate,
                    'content':content,'keyword':keyword}
        print(article)
        data_collect.append(article)

    if len(data_collect)!=0:
        outputjson(data_collect,cate2)

def extract_title(soup):
    try:
        title = soup.find('h1','title').text
    except:
        title = ''
    return title
            
def extract_date(soup):
    try:
        date_time = soup.find('time').text.strip()
    except:
        date_time = ''
    return date_time
        
def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div','story')[0].find_all('p')
        for c in contents:
            content += c.text.replace('\n','').replace('\r','')
    except:
        pass
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','part_tag_1 clearfix')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except:
        keyword = ''
    
    if keyword == '':
        try:
            keywords = soup.find_all('div','tag')[0].find_all('a')
            for k in keywords:
                keyword += k.text + ' '
        except:
            keyword = ''

    elif keyword == '':
        try:
            keywords = soup.find_all('p','tag')[0].find_all('a')
            for k in keywords:
                keyword += k.text + ' '
        except:
            keyword = ''

    return keyword

def outputjson(data_collect,cate2):
    folder_path = f'/home/ftp_246/data_1/news_data/Ettoday/{cate2}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = 'ettoday_' + cate2 + time.strftime('%Y%m%d') + '.json'
    with open(folder_path +'/'+filename,'w',encoding='utf8') as f:
        json.dump(data_collect,f,ensure_ascii=False,indent=2)
    f.close()
        
if __name__ == '__main__':
    start_date = datetime.datetime.strptime(time.strftime('%Y-%m-%d'),'%Y-%m-%d')
    one_day = datetime.timedelta(days=1)
    delta = datetime.timedelta(days=1)
    end_date = (start_date - one_day).strftime('%Y-%m-%d')
    print(end_date) 

    cates = [('政治','1','politics'),('社會','6','society'),('國際','2','global'),
             ('生活','5','life'),('財經','17','finance'),('健康','21','health'),('3C家電','20','3C')]

    url = 'https://www.ettoday.net/news/news-list-'
    for cate,cate1,cate2 in cates:
        parse_cateurl(url,start_date,end_date,cate,cate1,cate2)
