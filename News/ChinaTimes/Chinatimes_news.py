import requests
from bs4 import BeautifulSoup
import json
import os
import time
import datetime
from selenium import webdriver

def Chinatime(cate,cate1,mydir,url):
    num = 1
    urls = []
    while True:
        if 'realtimenews' in cate1:
            base_url = url + cate1 + '/?page='+ str(num) +'&chdtv'
        else:
            base_url = url + cate1 + '/total?page=' + str(num) + '&chdtv'
        print(base_url)
        try:
            browser.get(base_url)
        except:
            continue
        time.sleep(1.5)
        soup = BeautifulSoup(browser.page_source,'lxml')
        items = soup.find_all('ul','vertical-list list-style-none')[0].find_all('div','row')
        if len(items) < 10:
            break
        for item in items:
            title = extract_title(item)
            date_time = extract_date(item)
            link = extract_link(item)
            if 'beap.gemini' not in link:
                print(link)
                urls.append((title,link,date_time))
        if date_time < end_date:
            break
        else:
            num += 1

    scrape_article(cate,urls)

def extract_title(item):
    try:
        title = item.find('h3','title').text
    except:
        title = ''
    return title

def extract_date(item):
    try:
        date_time = item.find('time')['datetime']
    except:
        date_time = ''
    return date_time 

def extract_link(item):
    try:
        link =  'https://www.chinatimes.com' + item.find('h3','title').a.get('href')
    except:
        link = ''
    return link

def scrape_article(cate,urls):
    article = []
    for item in urls:
        title = item[0]
        link = item[1]
        date_time = item[2]

        browser.get(link)
        time.sleep(0.5)
        soup = BeautifulSoup(browser.page_source,'lxml')
        content = extract_content(soup)
        keyword = extract_keyword(soup)
        article.append({'date_time':date_time,'title':title,'link':link,
                        'label':cate,'content':content,'keyword':keyword})

    if len(article)!=0:
        write_to_json(article)

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div','article-body')[0].find_all('p')
        for c in contents:
            content += c.text
    except:
        pass
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','article-hash-tag')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except:
        pass
    return keyword

def write_to_json(article):
    #build folder yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/ChinaTimes/{mydir}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = 'chinatimes_' + mydir + time.strftime('%Y%m%d') + '.json'
    with open(folder_path + '/' + filename,'w',encoding='utf8') as f:
        json.dump(article,f,ensure_ascii=False,indent=2)
    f.close() 
    
if __name__ == '__main__':
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--no-sandbox')
    browser = webdriver.Chrome('/home/cdna/chromedriver',options=chrome_options)

    start_date = datetime.datetime.today()
    d = datetime.timedelta(days = 1)
    end_date = (start_date - d).strftime('%Y-%m-%d')
     
    cates = [('政治','politic','politics'),('國際','world','global'),
             ('社會','society','society'),('生活','life','life'),
             ('財經','money','finance'),('健康','health','health'),
             ('科技','technologynews','tech'),('即時新聞','realtimenews','realtime')]
    
    url = 'https://www.chinatimes.com/'
    for cate,cate1,mydir in cates:  
        Chinatime(cate,cate1,mydir,url)
    browser.close()
