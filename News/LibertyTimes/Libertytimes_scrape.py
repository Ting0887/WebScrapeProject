import time
import datetime
from bs4 import BeautifulSoup
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import create_session, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def scrape_link(session, label, category, page, end_date):
    urls = []
    # 如果遇到健康類
    if 'health' in label:
        while True:
            time.sleep(1)
            url = f'https://health.ltn.com.tw/ajax/breakingNews/9/{page}'
            print(url)
            res = session.get(url, timeout=20)
            if res.json()['data'] == []:
                break
            else:
                date_time = ''
                for item in res.json()['data']:   
                    try:
                        link = item['url']
                        title = item['title']
                        date_time = item['time'].replace('-','/')
                        print(link)
                        print(date_time)
                        if date_time < end_date:
                            break
                        urls.append((title,link,date_time))  
                    except Exception as e:
                        pass
            if date_time and date_time < end_date:
                break
            else:
                page += 1            

        if len(urls)!=0:
            scrape_content(session, label, category, urls)
    
    #如果爬科技類    
    elif '3C' in label:
        while True:
            time.sleep(1)
            url = f'https://3c.ltn.com.tw/indexAjax/{page}'
            print(url)
            res = session.get(url, timeout=20)
            if res.json() == []:
                break
            else:
                date_time = ''
                for item in res.json():
                    try:
                        title = item['title']
                        date_time = item['date']
                        label = item['tag_name']
                        link = 'https://3c.ltn.com.tw/news/' + item['no']
                        if date_time < end_date:
                            break
                        urls.append((title,link,date_time))
                    except Exception as e:
                        print(e)
                        break
            if date_time and date_time < end_date:
                break
            page += 1
        # if have url
        if len(urls)!=0:
            scrape_content(session, label, category, urls)
    #如果爬財經類              
    elif ('財經' in category) or\
         ('產業' in category) or\
         ('理財' in category) or\
         ('房產' in category):
        while True:
            time.sleep(1)
            url = f'https://ec.ltn.com.tw/list_ajax/{label}/{page}'
            print(url)
            res = session.get(url, timeout=20)
            if res.json() == 1:
                break
            else:
                date_time = ''
                for item in res.json():
                    try:
                        link = item['url']
                        date_time = item['A_ViewTime']
                        title = item['LTNA_Title']
                        if date_time < end_date:
                            break
                        urls.append((title,link,date_time))
                    except Exception as e:
                        print(e)
                        break
            if date_time and date_time < end_date:
                break
            page += 1
        # if have url
        if len(urls)!=0:
            scrape_content(session, label, category, urls)
                      
    else:
        start = 20
        while True:
            time.sleep(1)
            url = f'https://news.ltn.com.tw/ajax/breakingnews/{label}/{page}'
            print(url)
            res = session.get(url, timeout=20) 
            if res.json()['data'] == []:
                break
            elif page == 1:
                date_time = ''
                for item in res.json()['data']:
                    try:
                        link = item['url']
                        title = item['title']  
                        date_time = item['time']
                        
                        if len(date_time) < 10:
                            date_time = time.strftime('%Y/%m/%d') + ' ' + date_time
                        print(link,title,date_time)
                        urls.append((title,link,date_time))
                    except Exception as e:
                        print(e)
                        break
            else:     
                date_time = ''
                for _id in range(start,start+20):
                    try:
                        link = res.json()['data'][str(_id)]['url']
                        title = res.json()['data'][str(_id)]['title']
                        date_time =  res.json()['data'][str(_id)]['time']
                        if len(date_time) < 10:
                            date_time = time.strftime('%Y/%m/%d') + ' ' + date_time
                        print(link,title,date_time)
                        urls.append((title,link,date_time))
                    except Exception as e:
                        print(e)
                        pass
                start += 20
            if date_time and date_time < end_date:
                break
            page += 1
            
        # if have url
        if len(urls)!=0:
            scrape_content(session, label, category, urls)
            
def scrape_content(session, label, category, urls):
    data_collect = []
    for post in urls:
        title = post[0]
        link = post[1]
        date_time = post[2]
        res = session.get(link, timeout=20)
        time.sleep(1)
        soup = BeautifulSoup(res.text,'lxml')
        
        content = ''
        if 'health' in label:
            try:
                health_label = soup.select('.breadcrumbs')[0].find_all('a')[1].text
            except Exception:
                health_label = category
            items = soup.find_all('div','text boxTitle boxText')
            for item in items:
                try:
                    contents = item.select('p')
                    last_p = item.select('p')[-1].text #ad remove
                    for c in contents:
                        if ('健康新聞不漏接' in c.text):
                            break
                        else:
                            content += c.text.replace(last_p,'').replace('\n','')
                except Exception as e:
                    print(e)
                    pass
        else:
            try:
                contents = soup.select('.text')[0].find_all('p')
                for c in contents:
                    if ('《你可能還想看》' in c.text) or\
                           ('健康新聞不漏接' in c.text) or\
                           ('一手掌握經濟脈動' in c.text) or\
                           ('不用抽 不用搶' in c.text):
                            break
                    content += c.text.replace('\n','')
            except Exception:
                continue
                                                      
        if '3C' in label:
            keyword = ''
            try:
                keywords= soup.select('.keyword')[0].find_all('a')
                for k in keywords:
                    keyword += k.text + ' '
            except Exception:
                pass
        elif 'health' in label:
            keyword = ''
            try:
                keywords = soup.select('ul.keyword')[0].find_all('a')
                for k in keywords:
                    keyword += k.text + ' '
            except Exception:
                pass
        else:
            keyword = ''

        if 'health' in label:
            article =  {'date_time':date_time,
                        'title':title,
                        'link':link,
                        'label':health_label,
                        'content':content,
                        'keyword':keyword}
        else:
            article =  {'date_time':date_time,
                        'title':title,
                        'link':link,
                        'label':category,
                        'content':content,
                        'keyword':keyword}
        print(article)
        data_collect.append(article)
        
    if len(data_collect)!=0:
        write_to_json(label,data_collect)

def resolve_output_category(label):
    if ('strategy' in label) or ('international' in label) or ('investment' in label) or ('securities' in label) or ('estate' in label):
        return 'finance'
    if 'all' in label:
        return 'realtime'
    return label


def write_to_json(label,data_collect):
    file_path = write_json_records(
        records=data_collect,
        source_name='LibertyTimes',
        category=resolve_output_category(label),
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='liberty',
    )
    print(f"saved: {file_path}")

if __name__ == '__main__':
    end_date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y/%m/%d')
    session = create_session(headers={'x-requested-with': 'XMLHttpRequest'})
    
    categories = [('society','社會'),
                  ('world','國際'),
                  ('politics','政治'),
                  ('life','生活'),
                  ('all','即時'),
                  ('health','健康'),
                  ('3C','科技'),
                  ('strategy','財經政策'),
                  ('international','國際財經'),
                  ('investment','投資理財'),
                  ('securities','證券產業'),
                  ('estate','房產資訊')
                  ]
    
    for label,category in categories:
        scrape_link(session, label, category, page=1, end_date=end_date)
