#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from datetime import date


def get_urls(category):
    urls = []
    page = 1
    while True:
        print(f'Parsing urls on page {page} of category {category}...', end='\r')
        r = requests.get(f'https://www.gvm.com.tw/category/{category}?page={page}')
        soup = BeautifulSoup(r.text)
        
        links = [item.div.a['href'] for item in soup.select('.article-list-item')
                if is_valid_date(item.find(class_='time').text)]

        if not links:
            print(f'\nStopped parsing at page {page}.')
            break
        else:
            page += 1
            urls += links
    return urls


today = date.today()

def one_month_before(d):
    if d.month == 1:
        return d.replace(year = d.year - 1, month = 12)
    else:
        return d.replace(month = d.month - 1)

def is_valid_date(datestr):
    article_date = date.fromisoformat(datestr)
    return article_date >= one_month_before(today)

categories = [
    ('news'    , '時事熱點'),
    ('world'   , '國際'),
    ('money'   , '金融'),
    ('tech'    , '科技'),
    ('business', '產經'),
    ('life'    , '生活'),
]

for category, label in categories:
    urls = get_urls(category)
    with open(f'urls/gvm-{category}-urls-{today}.txt', 'w') as f:
        for url in urls:
            f.write(url + '\n')
