import re
import os
import random
import json
import time
import requests
import argparse
from bs4 import BeautifulSoup
import datetime
from datetime import date, timedelta
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

Nas_path = '/home/ftp_246/data_1/news_data/BCC/'

HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15'}

class BCC():
    def __init__(self,driver_path,period=15):
        self.domain_url = "https://www.bcc.com.tw"
        self.cate_list = [
                          ('政治','politics'),
                          ('國際','internation'),
                          ('社會','society'),
                          ('生活','life'),
                          ('財經','finance')
                          ]
        self.period = period
        self.driver_path = driver_path
    
    def write_json_articles(self, category, data):
        today = time.strftime("%Y%m%d")
        
        folder_path = Nas_path + category
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        filename = 'BCC' +'_' + category + '_' + today +'.json'
        try:
            with open(folder_path + '/' + filename, 'w') as outfile:
                json.dump(data, outfile, ensure_ascii=False,indent=2)
                print("articles list write to json file successfully")
        except Exception as E:
            print("articles list write to json file fail")
            print(E)
            
    def req_content_page(self, newslink):
        resp = requests.get(newslink, headers=HEADERS)
        soup = BeautifulSoup(resp.text, 'html.parser')
        soup.find('div', 'ft').extract()
        soup.find('span', {'name':'iclickAdBody_Start'}).find_parent().find('script').extract()
        content = soup.find('div', {'id':'some-class-name'}).get_text().strip()
        return content
    
    def crawl_articles_list(self):
        user_agent = 'UA = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"'
        # category = "newsList.社會"
        cate_article_list = {}
        options = Options()
        options.add_argument("user-agent={}".format(user_agent))
        options.add_argument('--headless')
        today = date.today()
        last_month_day = today - datetime.timedelta(days=self.period)
        for category in self.cate_list:
            driver = webdriver.Chrome(self.driver_path, options=options)
            driver.get(urljoin(self.domain_url, 'newsList.{}'.format(category[0])))
            
            articles_list, page = [], 1
            while True:
                try:
                    ls10s = driver.find_elements_by_class_name('ls10')
                    for ls10 in ls10s:
                        title = ls10.find_element_by_class_name('tt16').text
                        dt = ls10.find_element_by_class_name('dat').text[0:17].strip()
                        newslink = ls10.find_element_by_tag_name('a').get_attribute('href')
                        content = self.req_content_page(newslink)
                        data = {
                            'title': title,
                            'author': '',
                            'date_time': dt,
                            'content': content,
                            'keyword': '',
                            'link': newslink,
                            'label': category[0],
                            'website': "中國廣播公司",
                        }
                        print(dt)
                        articles_list.append(data)
                    try:
                        dtf = datetime.datetime.strptime(dt,'%Y/%m/%d %H:%M').date()
                        if (dtf >= last_month_day):
                            page = page + 1
                            driver.find_element(By.LINK_TEXT, "下一頁").click()
                            # print("NEXT PAGE: ", _+2)
                            time.sleep(random.randint(3,6))
                        else:
                            # break while loop
                            print('\n{} ~ {} 完成'.format(dtf, today))
                            driver.close()
                            break
                    except Exception as E:
                        print("stale element reference error")
                        print(E)
                except Exception as E:
                    print('CANT FIND tt16 element')
                    print(E)
                
            self.write_json_articles(category[1], articles_list)
            cate_article_list[category[0]] = articles_list
            
        return cate_article_list

    
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Peopo Web Crawler')
    parser.add_argument('--out_dir', type=str, help='output directory')
    parser.add_argument('--driver_path', type=str, help='chromedriver path')
    parser.add_argument('--period', type=int, help='crawler time range')
    args = parser.parse_args()
    bcc = BCC(args.driver_path)
    if args.period is not None:
        bcc = BCC(args.driver_path, args.period)
    article_list = bcc.crawl_articles_list()
