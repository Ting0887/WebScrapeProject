from bs4 import BeautifulSoup
import time
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def Newtalk(session, url, cate, cate2, end_date):
    news_link = []
    page = 15
    for num in range(1,page+1):
        base_url = url + f'/{num}'
        print(base_url)
        time.sleep(1)
        res = session.get(base_url, timeout=20)
        res.encoding = 'utf8'
        soup = BeautifulSoup(res.text,'lxml')
        categories = soup.find_all('div',{'id':'category'})
        if not categories:
            break

        items = categories[0].find_all('div','news-list-item clearfix')
        date_f = ''
        for item in items:
            link = item.find('a')['href']
            if 'plan' in link:
                continue
            print(link)
            date_f = link.split('/view/')[-1].split('/')[0]
            if date_f < end_date:
                break
            else:
                news_link.append(link)
        if date_f < end_date:
            break
    if len(news_link)!=0:
        parse_article(session, news_link, cate, cate2)

def parse_article(session, news_link, cate, cate2):
    article = []
    for link in news_link:
        time.sleep(1)
        try:
            res = session.get(link, timeout=20)
            res.encoding = 'utf8'
        except Exception:
            continue
        soup = BeautifulSoup(res.text,'lxml')
        try:
            title = soup.find('h1').text
        except Exception:
            title = ''
        
        try:
            date_time = soup.find('div','content_date').text\
                .replace('發布','').replace('|','').strip()
        except Exception:
            date_time = ''

        label = cate
        try:
            content = ''
            contents = soup.find_all('div',{'itemprop':'articleBody'})[0].find_all('p')
            for c in contents:
                content += c.text
        except Exception:
            continue
        
        try:
            keyword = ''
            keywords = soup.find_all('div','keyword_tag')[0].find_all('a')
            for k in keywords:
                keyword += k.text + ' '
        except Exception:
            keyword = ''
        
        article.append({'date_time':date_time,'title':title,'label':label,
                        'link':link,'content':content,'keyword':keyword})

    if len(article) !=0:
        outputjson(article, cate2)

def outputjson(article, cate2):
    file_path = write_json_records(
        records=article,
        source_name='NewTalk',
        category=cate2,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='newtalk',
    )
    print(f"saved: {file_path}")
    
if __name__ == '__main__':
    session = create_session()
    end_date = build_end_date(days_back=1)

    cates = [('政治','2','politics'),('社會','14','society'),
             ('國際','1','global'),('生活','5','life'),
             ('財經','3','finance'),('科技','8','tech')]

    for cate,cate1,cate2 in cates:    
        url = f'https://newtalk.tw/news/subcategory/{cate1}/{cate}'
        Newtalk(session, url, cate, cate2, end_date)
