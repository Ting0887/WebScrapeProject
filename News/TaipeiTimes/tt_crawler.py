import os
import time
import argparse
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from urllib.parse import urljoin
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import create_session, write_json_records


HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15'}


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")

class TaipeiTimes():
    def __init__(self):
        self.domain_url = "https://www.taipeitimes.com/"
        self.cate_list = ['taiwan', 'world']
        self.session = create_session(headers=HEADERS)
        
    def request_api(self, page, category):
        """
        args:
            page: 1~25
            category: two cateogry [world, taiwan]
        return:
            response json file
        """
        resp = self.session.get('https://www.taipeitimes.com/ajax_json/{}/list/{}'.format(page,category), timeout=20)
        return resp.json()
    
    def write_json_articles(self, category, data):
        try:
            file_path = write_json_records(
                records=data,
                source_name='TaipeiTimes',
                category=category,
                base_output_dir=OUTPUT_BASE_DIR,
                file_prefix='TaipeiTimes',
            )
            print(f"saved: {file_path}")
        except Exception:
            print("articles list write to json file fail")
    
    
    def crawl_articles_list(self):
        category_list = {}
        today = date.today()
        last_month_day = today - timedelta(days=1)
        for category in self.cate_list:
            page = 1
            articles_list = []
            while True:
                ars = self.request_api(page, category)
                for ar in ars:
                    dt = ar['ar_pubdate']
                    newslink = urljoin(self.domain_url, ar['ar_url'])
                    _ = articles_list.append({'title': ar['ar_head'],'date':dt,'newslink':newslink})
                
                f_dt = datetime.strptime(dt, '%Y-%m-%d').date()
                if (f_dt >= last_month_day) and (page <= 25):
                    page = page + 1
                else:
                    # break while loop
                    print('\n{} ~ {} 完成'.format(f_dt, today))
                    break
            category_list[category] = articles_list
            self.write_json_articles(category, articles_list)
            self.category_list = category_list
        return category_list
    
    def crawl_articles_content(self):

        for category in self.category_list:
            articles = []
            for tt in self.category_list[category]:
                # print('Now ', tt['newslink'])
                resp = self.session.get(tt['newslink'], timeout=20)
                if resp.status_code != 200:
                    print('BAD REQUEST')
                else:
                    try:
                        soup = BeautifulSoup(resp.text, 'html.parser')
                        author = soup.find('div','name').text.strip()
                        ps = soup.find('div','archives').find_all('p')
                        content = ''
                        for p in ps:
                            content = content + str(p.text.strip())

                        articles.append({
                            'title': tt['title'],
                            'author': author,
                            'date_time': tt['date'],
                            'content': content,
                            'keyword': '',
                            'link': tt['newslink'],
                            'label': 'Taipei News',
                            'website': 'Taipei Times'
                        })
                    except Exception:
                        print("Web page structure might change")
                
                # print(category, " is successful!")
                self.write_json_articles(category, articles)

        return articles
    
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Taipei Times Web Crawler')
    #parser.add_argument('--out_dir', type=str, help='output directory')
    args = parser.parse_args()
    tt = TaipeiTimes()
    article_list = tt.crawl_articles_list()
    tt.crawl_articles_content()
