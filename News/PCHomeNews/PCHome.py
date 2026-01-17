import requests.packages.urllib3
from bs4 import BeautifulSoup
import time
import datetime
import json
import os

start_date = datetime.datetime.today()
d = datetime.timedelta(hours=12)
end_date = (start_date - d).strftime('%Y-%m-%d %H:%M:%S')

headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"}

requests.packages.urllib3.disable_warnings()

def Scrape(cate,cate1,folder):
    datalist = []
    for num in range(1,17):
        url = f'https://news.pchome.com.tw/cat/{cate}/hot/{num}'
        print(url)
        res = requests.get(url,headers=headers,verify=False)
        res.encoding = 'utf8'
        soup = BeautifulSoup(res.text,'lxml')
        items = soup.find_all('div','channel_newssection')
        for item in items:
            try:
                title = item.find('a')['title']  #title
                print(title)
                link = 'https://news.pchome.com.tw' + item.find('a')['href'] #link
                    
                res = requests.get(link,headers=headers,verify=False)
                soup = BeautifulSoup(res.text,'lxml')
                date_time = soup.find('time')['datetime']  #date_time
                author = soup.find('time').text.replace(date_time,'').strip() #author
                    
                content = soup.find('div',{'calss':'article_text'}).text.replace('\n','').strip() #content
                   
                keyword = ''
                keywords = soup.select('.ent_kw')[0].find_all('a')
                for k in keywords:
                    keyword += k.text + ' '
                print(keyword)              
            except:
                pass
                
            if date_time < end_date:
                break
                
            article = {'date_time':date_time,'title':title,
                       'author':author,'link':link,
                       'label':cate1,'content':content,
                       'keyword':keyword}

            datalist.append(article)
        if date_time < end_date:
            break
    if len(datalist)!=0:
        write_to_json(datalist,cate,folder)

def write_to_json(datalist,cate,folder):
    #build dictionary
    folder_path = f'/home/ftp_246/data_1/news_data/PCHome/{folder}/' + time.strftime('%Y-%m')
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = 'PCHome_' + cate + time.strftime('%Y%m%d%H') + '.json'
    with open(folder_path + '/' + filename,'w',encoding='utf8') as f:
        json.dump(datalist,f,ensure_ascii=False,indent=2)

def main():
    cates = [('politics','政治','politics'),
             ('society', '社會','society'),
             ('internation' , '國際','global'),
             ('healthcare', '健康','health'),
             ('finance','財經','finance'),
             ('living' , '生活','life'),
             ('science','科技','tech')]

    for cate,cate1,folder in cates:
        Scrape(cate,cate1,folder)

if __name__ == '__main__':
    main()
