import requests
from bs4 import BeautifulSoup
import json
import time
import os
import datetime

def parse_cateurl(start_date,end_date):
    domain_name = 'https://www.mirrormedia.mg/api/v2/getlist?max_results=9&sort=-publishedDate&where=%7B%22categories%22%3A%7B%22%24'
    cates = [
             ('政治','politics','in%22%3A%5B%225979ac0de531830d00e330a7%22%5D%7D%7D&'),
             ('社會','society','in%22%3A%5B%225979ac33e531830d00e330a9%22%5D%7D%7D&'),
             ('生活','life','in%22%3A%5B%225979ac22e531830d00e330a8%22%5D%7D%7D&'),
             ('國際','global','in%22%3A%5B%225e983017a66f9e0f00a03951%22%5D%7D%7D&'),
             ('財經','finance','in%22%3A%5B%2257e1e16dee85930e00cad4ec%22%5D%7D%7D&')
            ]
    for cate,cate1,cate2 in cates:
        collect_url = []
        page = 1
        while True:
            url = domain_name+ cate2 + 'page=' + str(page)
            print(url)
            res = requests.get(url)
            try:
                parse_json = res.json()
                for item in parse_json['_items']:
                    title = extract_title(item)
                    newslink = extract_article_link(item)
                    date_time = read_newsdate(item)

                    if date_time < end_date:
                        break
                    else:
                        collect_url.append((title,newslink))
            except:
                pass

            if date_time < end_date:
                break
            page += 1
        
        if len(collect_url)!=0:
            parse_link(collect_url,cate,cate1)
                    
def extract_title(item):
    try:
        title = item['title']
    except:
        title = ''
    return title

def extract_article_link(item):
    try:
        link = 'https://www.mirrormedia.mg/story/' + item['name']
    except:
        link = ''
    return link

# check date
def read_newsdate(item):
    try:
        date_f = item['slug'][0:8]
        date_time = datetime.datetime.strptime(date_f,"%Y%m%d").strftime('%Y-%m-%d')
    except:
        date_time = ''
    return date_time

def parse_link(collect_url,cate,cate1):
    article = []
    for item in collect_url:
        title = item[0]
        link = item[1]
        res = requests.get(link)
        soup = BeautifulSoup(res.text,'lxml')
        #scrape content and keyword
        content = extract_content(soup)
        keyword = extract_keyword(soup)
        date_time = extract_date(soup)

        article.append({'date_time':date_time[0:17],'title':title,
                        'link':link,'label':cate,
                        'content':content,'keyword':keyword})
    if len(article)!=0:
        return write_to_json(article,cate1)

def extract_date(soup):
    try:
        date_time = soup.find('p','story__published-date').text
    except:
        date_time = ''
    return date_time

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('p','g-story-paragraph')
        for c in contents[:-1]:
            content += c.text.replace('\n','')
    except:
        pass
    return content
                
def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div','story__tags')[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except:
        pass
    return keyword
                    
def write_to_json(article,cate1):
    #bulid folder by yyyy-mm
    folder_path = f'/home/ftp_246/data_1/news_data/Mirror_media/{cate1}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    filename = 'mirror_' + cate1 + time.strftime('%Y%m%d') + '.json'
    with open(folder_path + '/' + filename,'w',encoding='utf8') as jf:
        json.dump(article,jf,ensure_ascii=False,indent=2)
    jf.close()

def main():
    start_date = datetime.datetime.today()
    d = datetime.timedelta(days=1)
    end_date = (start_date - d).strftime('%Y-%m-%d')
    print(end_date)
    # parse category url
    parse_cateurl(start_date,end_date)

if __name__ == '__main__':
    main()
     
