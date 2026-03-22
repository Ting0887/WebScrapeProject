import datetime
import os
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import create_session, get_soup, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

def build_bw_end_date(days_back=1):
    target_date = datetime.datetime.today() - datetime.timedelta(days=days_back)
    return target_date.strftime('%Y.%m.%d')


def scrape_link(session, category, number, end_date):
    urls = []
    page = 1
    while True:
        page_link = f"https://www.businessweekly.com.tw/ChannelAction/LoadBlock/"
        payload = {'Start': 1 + (20 * (page - 1)),
                'End': 20 * page,
                'ID': number}
        try:
            res = session.post(page_link, data=payload, timeout=20)
            res.raise_for_status()
        except Exception as error:
            print(f"skip list page by request error: {error}")
            break

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(res.text,'lxml')
        articles = soup.find_all(class_='Article-img-caption flex-xs-fill')
        if not articles:
            break

        last_date = ''
        for article in articles:
            try:
                dates = article.find('span','Article-date d-xs-none d-sm-inline').text.strip()
            except Exception:
                dates = ''
            link_node = article.find('div', 'Article-content d-xs-flex')
            links = link_node.a.get('href') if link_node and link_node.a else ''
            if 'https' not in links:
                links = 'https://www.businessweekly.com.tw' + links
            last_date = dates
            if not dates or not links:
                continue
            if dates < end_date:
                break
            print(links)
            urls.append(links)
        if last_date and last_date < end_date:
            break
        else:
            page += 1
    
    if len(urls)!=0:
        write_urls_to_txt(category,urls)
        scrape_content(session, category, urls)
        
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
        
def scrape_content(session, category, urls):
    data_collect = []
    for link in urls:
        try:
            soup = get_soup(session, link, sleep_seconds=0.2)
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
            except Exception:
                pass          
            data_collect.append(article)
            
        except Exception as err:
            print('Error: could not parse.')
            print(err)
            
    if len(data_collect)!=0:
        write_to_json(category, data_collect)
                   
def write_to_json(category, data_collect):
    file_path = write_json_records(
        records=data_collect,
        source_name='BusinessWeekly',
        category=category,
        base_output_dir=OUTPUT_BASE_DIR,
        file_prefix='bw',
    )
    print(f"saved: {file_path}")
    
if __name__ == '__main__':
    end_date = build_bw_end_date(days_back=1)
    print(end_date)
    session = create_session()

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
        scrape_link(session, category, number, end_date)
