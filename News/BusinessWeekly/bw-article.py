import requests
from bs4 import BeautifulSoup
from datetime import date
import datetime
import time
import glob
import json
import os

def scrape_link(category,number):
    urls = []
    page = 1
    while True:
        page_link = f"https://www.businessweekly.com.tw/ChannelAction/LoadBlock/"
        payload = {'Start': 1 + (20 * (page - 1)),
                'End': 20 * page,
                'ID': number}
        res =requests.post(page_link,data=payload)
        soup = BeautifulSoup(res.text,'lxml')
        articles = soup.find_all(class_='Article-img-caption flex-xs-fill')
        for article in articles:
            try:
                dates = article.find('span','Article-date d-xs-none d-sm-inline').text.strip()
            except:
                dates = ''
            links = article.find('div','Article-content d-xs-flex').a.get('href')
            if 'https' not in links:
                links = 'https://www.businessweekly.com.tw' + links
            if dates < end_date:
                break
            print(links)
            urls.append(links)
        if dates < end_date:
            break
        else:
            page += 1
    
    if len(urls)!=0:
        write_urls_to_txt(category,urls)
        scrape_content(category,urls)
        
def write_urls_to_txt(category,urls):
    #bulid folder yyyy-mm
    folder_path = '/home/ftp_246/data_1/news_data/BusinessWeekly/urls'+ '/' + time.strftime('%Y-%m') 
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(folder_path + '/'+f'bw-{category}-urls_'+time.strftime('%Y-%m-%d')+'.txt','w',encoding='utf-8') as txtf:
        for url in urls:
            txtf.write(url)
            txtf.write('\n')
    txtf.close()
        
def scrape_content(category,urls):
    data_collect = []
    for link in urls:
        try:
            soup = BeautifulSoup(requests.get(link).text,'lxml')
            article = {}

            # blog
            article['url'] = link
            article['label'] = ':'.join(x.text for x in soup.select('.breadcrumb-item')[1:])
            article['title'] = soup.find('h1', class_='Single-title-main').text
            article['author'] = soup.find(class_='Single-author-row-name').text.strip()
            article['date'] = soup.select('.Single-author-row > .Padding-left > span')[1].text
            article['summary'] = ''.join(
                p.text for p in
                soup.select('.Single-summary-content > p'))
            article['content'] = ''.join(
                p.text for p in
                soup.select('.Single-article > p'))
            # Not all articles have tags/keywords
            try:
                article['keywords'] = [a.text for a in soup.select('.Single-tag-list > a')]
            except:
                pass          
            data_collect.append(article)
            
        except Exception as err:
            print('Error: could not parse.')
            print(err)
            
    if len(data_collect)!=0:
        write_to_json(data_collect)
                   
def write_to_json(data_collect):
    #bulid folder yyyy-mm
    folder_path = '/home/ftp_246/data_1/news_data/BusinessWeekly/json/' + category + '/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    with open(folder_path + '/' + 'bw-'+category+'-'+time.strftime('%Y-%m-%d')+'.json','w',encoding='utf-8') as jf:
        json.dump(data_collect,jf,ensure_ascii=False,indent=2)
    jf.close()
    
if __name__ == '__main__':
    start_date = datetime.datetime.today() #today
    months = datetime.timedelta(days=1)  #last month
    end_date = (start_date - months).strftime('%Y.%m.%d')
    print(end_date)

    categories = [
                ('business', '0000000319'),
                ('style' , '0000000337'),
                ('world','0000000317'),
                ('china','0000000318'),
                ('insight','0000000320'),
                ('realestate','0000000324'),
                ('money','0000000323'),
                ('digitaltransformation','0000000327'),
                ('Innovation','0000000328'),
                 ]

    for category, number in categories:
        scrape_link(category,number)
