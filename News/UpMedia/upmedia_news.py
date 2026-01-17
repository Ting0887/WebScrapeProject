import requests
from bs4 import BeautifulSoup
import json
import time
import os
import datetime

def parse_cateurl(end_date,url,cate):
    num = 1
    collect_url = []
    while True:
        base_url = url + 'currentPage=' + str(num) + '&Type=' + cate1
        res = requests.get(base_url,headers=headers)
        print(base_url)
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.find_all('div','top-dl')
        
        for item in items:
            date_time = extract_date(item)
            print(date_time)
            link = extract_newslink(item)
            if date_time < end_date:
                break
            else:
                collect_url.append((date_time,link))
        if date_time < end_date:
            break
        else:
            num += 1

    if len(collect_url)!=0:
        extract_newsinfo(collect_url,cate)

def extract_date(item):
    try:
        date_time = item.find('div','time').text.strip()
    except:
        date_time = ''
    return date_time

def extract_newslink(item):
    try:
        link = 'https://www.upmedia.mg/' + item.find('a')['href']
    except:
        link = ''
    return link

def extract_newsinfo(collect_url,cate):
    article = []
    for item in collect_url:
        date_time = item[0]
        link = item[1]
        try:
            res = requests.get(link,headers=headers)
            soup = BeautifulSoup(res.text,'lxml')

            title = extract_title(soup)
            author = extract_author(soup)
            label = extract_label(soup)
            content = extract_content(soup)
            keyword = extract_keyword(soup)

            article.append({'date_time':date_time,'title':title,'author':author,
                            'label':label,'link':link,'content':content,'keyword':keyword})
        except Exception as e:
            print(e)

    if len(article)!=0:
        write_to_json(article,cate)

def extract_title(soup):
    try:
        title = soup.find('h2',{'id':'ArticleTitle'}).text
    except:
        title = ''
    return title

def extract_author(soup):
    try:
        author = soup.find('div','author').a.text
    except:
        author = ''
    return author

def extract_label(soup):
    label = ''
    try:
        labels = soup.find_all('div','tag')[0].find_all('a')
        for l in labels:
            label += l.text + ' '
    except:
        pass
    return label

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div','editor')[0].find_all('p')
        for c in contents:
            content += c.text
    except:
        pass
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','label')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except:
        pass
    return keyword
                            
def write_to_json(article,cate):
    #bulid folder by yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/upmedia/{cate}/'+time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = 'upmedia_' + cate +  time.strftime('%Y%m%d') +'.json'
    with open(folder_path +'/'+ filename,'w',encoding='utf8') as jf:
        json.dump(article,jf,ensure_ascii=False,indent=2)
    jf.close()
        
if __name__ == '__main__':
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days = 1)
    end_date = (start_date - d).strftime('%Y年%m月%d日 %H:%M')
    print(end_date)

    cates = [('global','3'),('focus','24'),('life','5')]

    headers = {'referer': 'https://www.upmedia.mg/news_list.php?',
               'upgrade-insecure-requests': '1',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}
    
    for cate,cate1 in cates:
        url = 'https://www.upmedia.mg/news_list.php?'
        parse_cateurl(end_date,url,cate)
