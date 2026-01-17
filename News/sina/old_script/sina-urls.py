#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta

def get_urls(category):
    urls = set()
    # Scrape the latest 31 days (~1 month)
    for i in range(31, -1, -1):
        d = date.today() - timedelta(days=i)
        datestring = f'{d.year}{d.month:02}{d.day:02}'
        print(f'Parsing urls of day {datestring} of category {category}...', end='\r')
        page = 1
        while True:
            r = requests.get(
                'https://news.sina.com.tw/realtime/'
                + category
                + '/tw/'
                + datestring
                + '/list-'
                + str(page)
                + '.html')
            soup = BeautifulSoup(r.text)
            titles = soup.find('ul', class_='realtime')\
                         .find_all('a')
            if titles == []:
                break
            else:
                links = ['https://news.sina.com.tw' + a['href']
                        for a in titles]
                urls = urls.union(links)
                page += 1

    return urls


categories = [
    ('politics', '政治'),
    ('society' , '社會'),
    ('china'   , '兩岸'),
    ('global'  , '國際'),
    ('life'    , '生活'),
    ('finance' , '財經'),
    ('tech'    , '科技')
]

today = date.today().isoformat()

for category, label in categories:
    urls = sorted(list(get_urls(category)))
    with open(f'urls/sina-{category}-urls-{today}.txt', 'w') as f:
        for url in urls:
            f.write(url + '\n')
