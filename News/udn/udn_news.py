import requests
from bs4 import BeautifulSoup
import time
import datetime
import json
import os

def scrape_health(health_cate):
    data_collect = []
    page = 1
    while True:
        url = 'https://health.udn.com/rank/newest/1005/' + str(page)
        print(url)
        res = requests.get(url)
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.find_all('tbody')[0].find_all('tr')[1:]
        page += 1
        for item in items:
            try:
                title = item.find('a').text
                label = item.find('td','only_web').text
                link = item.find('a')['href']
                res = requests.get(link)
                soup = BeautifulSoup(res.text,'lxml')
                
                date_time = soup.find('div','shareBar__info--author').span.text
                author = soup.find('div','shareBar__info--author').text.replace(date_time,'')
                
                content = ''
                try:
                    contents = soup.find_all('p')
                    for c in contents:
                        content += c.text
                except:
                    continue

                keyword = ''
                try:
                    keywords = soup.find_all('dl','tabsbox')[0].find_all('a')
                    for k in keywords:
                        keyword += k.text + ' '
                except:
                    print('no keyword')
                if date_time < end_date:
                    break
                article = {'title':title,'date_time':date_time,
                           'author':author,'link':link,
                           'label':label,'content':content,
                           'keyword':keyword}
                print(article)
                data_collect.append(article)
            except Exception as e:
                pass
        if date_time < end_date:
            break

    if len(data_collect)!=0:
        write_to_json(health_cate,data_collect)
        
def scrape_finance_url(finance_cate):
    urls = []
    for category,cate_id,sub_id in finance_cate:
        page = 0
        while True:
            try:
                page_link = f'https://udn.com/api/more?page={page}&channelId=2\
                               &type=subcate_articles&cate_id={cate_id}&sub_id={sub_id}'
                res = requests.get(page_link)
                print(page_link)
                for item in res.json()['lists']:
                    title = item['title']
                    link = 'https://udn.com/news' + item['titleLink'].replace('//story','/story')
                    date_time = item['time']['date']
                    if date_time < end_date:
                        break
                    print(link)
                    urls.append((title,link,date_time))
                if date_time < end_date:
                    break
                else:
                    page += 1
            except Exception as e:
                print(e)
                break
    if len(urls)!=0:
        scrape_content(category,urls)

def scrape_link(category,cate_id,sub_id):
    urls = []
    page = 1
    while True:
        try:
            page_link = f'https://udn.com/api/more?page={page}&channelId=2\
                        &type=subcate_articles&cate_id={cate_id}&sub_id={sub_id}'
            res = requests.get(page_link)
            print(page_link)
            for item in res.json()['lists']:
                title = item['title']
                link = 'https://udn.com/news' + item['titleLink'].replace('//story','/story')
                date_time = item['time']['date']
                if date_time < end_date:
                    break
                print(link)
                urls.append((title,link,date_time))
            if date_time < end_date:
                break
            else:
                page += 1
        except Exception as e:
            print(e)
            break

    if len(urls)!=0:
        scrape_content(category,urls)

def scrape_content(category,urls):
    data_collect = []
    for item in urls:
        
        link = item[1]
        title = item[0]
        date_time = item[2]

        res = requests.get(link)
        soup = BeautifulSoup(res.text,'lxml')
        try:
            author = soup.find('span','article-content__author').text.strip()
        except:
            author = ''
        content = ''
        try:
            contents = soup.find_all('section','article-content__editor')[0].find_all('p')
            for c in contents:
                content += c.text.replace('\n','').replace('\r','').replace('\t','')
        except:
            continue
        try:
            label = soup.select('.article-content__info')[0].find_all('a')[-1].text
        except:
            label = ''

        keyword = ''
        try:
            keywords = soup.find_all('section','keywords')[0].find_all('a')
            for k in keywords:
                keyword += k.text + ' '
        except:
            pass
        
        if label != '':
            article = {'date_time':date_time,'title':title,'link':link,
                       'label':label,'content':content,'keyword':keyword}
            print(article)
        data_collect.append(article)
    if len(data_collect)!=0:
        write_to_json(category,data_collect)

def write_to_json(category,data_collect):
    folder_path = f'/home/ftp_246/data_1/news_data/udn/{category}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file = 'udn_' + category + time.strftime('%Y%m%d') + '.json'
    with open(folder_path + '/'  + file,'w',encoding='utf8') as jf:
        json.dump(data_collect,jf,ensure_ascii=False,indent=2)
    jf.close()

if __name__ == '__main__':
    start_date = datetime.datetime.today()
    delta = datetime.timedelta(days=1)
    end_date = (start_date - delta).strftime('%Y-%m-%d %H:%M')
    print(end_date)

    categories = [('politics','6638','6656'),
                  ('society','6639','7320'),
                  ('global','7225','6809'),
                  ('life','6649','7266'),
                  ('tech','6644','7240'),]

    finance_cate = [('finance','6644','7238'),
                    ('finance','6644','7239'),
                    ('finance','6644','7243'),
                    ('finance','6644','7241'),
                    ('finance','6644','121591')]

    for category,cate_id,sub_id in categories:
        scrape_link(category,cate_id,sub_id)

    scrape_finance_url(finance_cate)
    
    health_cate = 'health'
    scrape_health(health_cate)



