#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from datetime import date
from selenium import webdriver


driverPath = '/home/tingyang0518/chromedriver'
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")
ua = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"
chrome_options.add_argument("user-agent={}".format(ua))
browser = webdriver.Chrome(driverPath,options=chrome_options)

def get_urls(category):
    urls = []
    page = 1
    while True:
        print(f'Parsing page {page} of category {category}...',end='\r')
        browser.get(f'https://cnews.com.tw/category/{category}/page/{page}')
        soup = BeautifulSoup(browser.page_source,'lxml')
        figures = soup.find_all('figure','special-format')
        for f in figures:
            links = f.find('a')['href']
            if '/category/' in links:
                continue
            date = f.find('li','date').text.strip()
            print(date)
            urls.append(links)
            page += 1
        if date < '2021-07-01':
            break


    return urls


today = date.today()

"""
def one_month_before(d):
    if d.month == 1:
        return d.replace(year = d.year - 1, month = 12)
    else:
        return d.replace(month = d.month - 1)
"""
categories = [
    ('新聞匯流', 'news'),
    ('政治匯流', 'politics'),
    ('國際匯流', 'global'),
    ('生活匯流', 'life'),
    ('健康匯流', 'health'),
    ('金融匯流', 'finance'),
    ('數位匯流', 'tech')
]


for category, label in categories:
    urls = get_urls(category)
    with open(f'urls/cnews-{label}-urls-{today}.txt', 'w') as f:
        for url in urls:
            f.write(url + '\n')
