import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
import os

def parse_cateurl(url,cate,cate1,cate2,folder):
    collect_url = []
    page = 5
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
               ,'x-requested-with': 'XMLHttpRequest'}
    for num in range(1,page+1):
        payloads = {"action": "0", "category": cate1, "pagesize": "20", "pageidx": num}
        print(url)
        res = requests.post(url,data=payloads,headers=headers)
        r = res.json()
        for item in r['ResultData']['Items']:
            date_time = extract_date(item)
            title = extract_title(item)
            link = extract_link(item)
            if date_time < end_date:
                break
            else:
                collect_url.append((date_time,title,link))

        if date_time < end_date:
            break
    
    if len(collect_url)!=0:
        extract_info(collect_url,cate,cate2,folder)

def extract_date(item):
    try:
        date_time = item['CreateTime'] #datetime
    except:
        date_time = ''
    return date_time

def extract_title(item):
    try:
        title = item['HeadLine'] #title
    except:
        title = ''
    return title
            
def extract_link(item):
    try:
        link = item['PageUrl'] #link
    except:
        link = ''
    return link

def extract_info(collect_url,cate,cate2,folder):
    datalist = []
    for item in collect_url:
        date_time = item[0]
        title = item[1]
        link = item[2]
        res = requests.get(link)
        soup = BeautifulSoup(res.text,'lxml')

        content = extract_content(soup)
        article= {'date_time':date_time,'title':title,
                  'label':cate,'link':link,
                  'content':content,'keyword':''}
        datalist.append(article)

    if len(datalist)!=0:
        outputjson(datalist,cate2,folder)

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div','paragraph')[0].find_all('p')
        for c in contents:
            content += c.text
    except:
        pass
    return content    

def outputjson(datalist,cate2,folder):
    #bulid folder yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/CNA/{folder}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = 'cna_' + cate2 +time.strftime('%Y%m%d') + '.json'
    with open(folder_path + '/' + filename,'w',encoding='utf8') as f:
        json.dump(datalist,f,ensure_ascii=False,indent=2)
    f.close()
        
if __name__ == '__main__':
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days=1)
    end_date = (start_date - d).strftime('%Y/%m/%d')
    
    url = 'https://www.cna.com.tw/cna2018api/api/WNewsList'
    cates = {('政治','aipl','politics','politics'),
             ('社會','asoc','society','society'),
             ('國際','aopl','global','global'),
             ('生活','ahel','life','life'),
             ('產經','aie','sankei','finance'),
             ('科技','ait','tech','technology'),
             ('證券','asc','security','finance')}
    for cate,cate1,cate2,folder in cates:
        parse_cateurl(url,cate,cate1,cate2,folder)
