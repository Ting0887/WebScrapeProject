import requests
from bs4 import BeautifulSoup
import json
import time
import datetime
import os

def Yahoo_news(label,cate,tag,url):
    article = []
    for num in range(0,2000,10):
        base_url = url + f'count=10;loadMore=true;mrs=%7B%22size%22%3A%7B%22w%22%3A220%2C%22h%22%3A128%7D%7D;newsTab={cate};start={num};tag={tag};usePrefetch=false?bkt=ybar_twnews'
        res = requests.get(base_url)
        print(base_url)
        try:
            parse_json = res.json()
        except:
            continue
        if parse_json == None:
            continue
        for item in parse_json:
            title = extract_title(item)
            source = extract_source(item)
            date_time = extract_date(item)
            link = extract_link(item)

            try:
                res = requests.get(link)
            except:
                print('link is 404')

            soup = BeautifulSoup(res.text,'lxml')
            content = extract_content(soup)
            if date_time < end_date:
                break
            else:
                article.append({'date_time':date_time,
                                'title':title,
                                'source':source,
                                'link':link,
                                'label':label,
                                'content':content,
                                'keyword':''})
        if date_time < end_date:
            break
    outputjson(cate,article)

def extract_title(item):
    try:
        title = item['title']
    except:
        title = ''
    return title

def extract_source(item):
    try:
        source = item['provider_name']
    except:
        source = ''
    return source

def extract_date(item):
    try:
        utime = item['published_at']
        date_time = datetime.datetime.utcfromtimestamp(float(utime))
        date_time = date_time.strftime('%Y-%m-%d')
    except:
        date_time = ''
    return date_time


def extract_link(item):
    try:
        link = 'https://tw.news.yahoo.com' + item['url']
    except:
        link = ''
    return link

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div','caas-content-wrapper')[0].find_all('p')
        for c in contents:
            if c.text.startswith('更多'):
                break
            else:
                content += c.text.replace('原始連結','')
    except:
        pass
    return content
            
def outputjson(cate,article):
    #bulid folder yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/yahoo_news/{cate}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    filename = 'yahoo_' + cate + time.strftime('%Y%m%d') + '.json'
    with open(folder_path + '/'  + filename,'w',encoding='utf8') as f:
        json.dump(article,f,ensure_ascii=False,indent=2)
    f.close()
    
if __name__ == '__main__':
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days=1)
    end_date = (start_date - d).strftime('%Y-%m-%d')
    print(end_date)
    categories = [
            ('政治','politics','%5B%22yct%3A001000661%22%5D'),
             ('社會','society','%5B%22ymedia%3Acategory%3D000000179%22%2C%22yct%3A001000798%22%2C%22yct%3A001000667%22%5D'),
             ('國際','global','%5B%22ymedia%3Acategory%3D000000030%22%2C%22ymedia%3Acategory%3D000000032%22%5D'),
             ('生活','life','%5B%22ymedia%3Acategory%3D000000126%22%2C%22yct%3A001000560%22%2C%22yct%3A001000374%22%2C%22yct%3A001001117%22%2C%22yct%3A001000659%22%2C%22yct%3A001000616%22%5D'),
             ('財經','finance','%5B%22yct%3A001000298%22%2C%22yct%3A001000123%22%5D'),
             ('健康','health','%5B%22yct%3A001000395%22%5D'),
             ('科技','tech','%5B%22yct%3A001000931%22%2C%22yct%3A001000742%22%2C%22ymedia%3Acategory%3D000000175%22%5D')]
    url = 'https://tw.news.yahoo.com/_td-news/api/resource/IndexDataService.getExternalMediaNewsList;'
    for label,cate,tag in categories:
        Yahoo_news(label,cate,tag,url)
    
