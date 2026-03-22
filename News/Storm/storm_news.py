from bs4 import BeautifulSoup
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def parse_cateurl(session, url, cate, end_date):
    page = 1
    posts = []
    while True:
        page_url = url + '/' + str(page)
        print(page_url)
        res = session.get(page_url, timeout=20)
        soup = BeautifulSoup(res.text,'lxml')
        categories = soup.find_all('div',{'id':'category_content'})
        if not categories:
            break

        bar = categories[0].find_all('div','category_card card_thumbs_left')
        date_time = ''

        for item in bar:
            label = extract_label(item)
            title = extract_title(item)
            author = extract_author(item)
            date_time = extract_date(item)
            link = extract_link(item)
            
            if date_time < end_date:
                break
            else:
                posts.append((title,date_time,link,author,label))

        if date_time < end_date:
            break
        else:
            page += 1
    if len(posts)!=0:
        parse_info(session, posts, cate)

def extract_label(item):
    label = ''
    try:
        labels = item.find_all('div','tags_wrapper')[0].find_all('a')
        for l in labels:
            label += l.text+ ' '
    except Exception:
        pass
    return label
        
def extract_title(item):
    try:
        title = item.find('h3','card_title').text
    except Exception:
        title = ''
    return title

def extract_author(item):
    try:
        author = item.find('span','info_author').text
    except Exception:
        author = ''
    return author

def extract_date(item):
    try:
        date_time = item.find('span','info_time').text
    except Exception:
        date_time = ''
    return date_time

def extract_link(item):
    try:
        link = item.find('a','card_link link_title').get('href')
    except Exception:
        link = ''
    return link

def parse_info(session, posts, cate):
    article = []
    for item in posts:
        title = item[0]
        date_time = item[1]
        link = item[2]
        author = item[3]
        label = item[4]
        
        res = session.get(link, timeout=20)
        soup = BeautifulSoup(res.text,'lxml')

        content = extract_content(soup)
        keyword = extract_keyword(soup)

        article.append({'date_time':date_time,'author':author,'title':title,
                        'label':label,'link':link,'content':content,'keyword':keyword})

    article.sort(key=lambda x: x['date_time'],reverse=True)
    if len(article)!=0:
        write_to_json(article,cate)

def extract_content(soup):
    content = ''
    try:
        contents = soup.find_all('div',{'id':'CMS_wrapper'})[0].find_all('p')
        for c in contents:
            content += c.text
    except Exception:
        pass
    return content

def extract_keyword(soup):
    keyword = ''
    try:
        keywords = soup.find_all('div',{'id':'tags_list_wrapepr'})[0].find_all('a')
        for k in keywords:
            keyword += k.text + ' '
    except Exception:
        pass
    return keyword

def write_to_json(article,cate):
    file_path = write_json_records(
        records=article,
        source_name='Storm',
        category=cate,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='storm',
    )
    print(f"saved: {file_path}")

if __name__ == '__main__':
    session = create_session(headers={"referer": "https://www.storm.mg/category"})
    end_date = build_end_date(days_back=1) + ' 00:00'
    cates = [('politics','https://www.storm.mg/category/118'),
             ('global','https://www.storm.mg/category/117'),
             ('domestic','https://www.storm.mg/category/22172'),
             ('finance','https://www.storm.mg/category/23083'),
             ('local','https://www.storm.mg/localarticles'),
             ('tech','https://www.storm.mg/technology'),
             ('health','https://www.storm.mg/life-category/s24252'),
             ('stylish','https://www.storm.mg/stylish-category')]
    
    for cate,cate1 in cates:
        url = cate1
        parse_cateurl(session, url, cate, end_date)
