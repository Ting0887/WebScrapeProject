#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from datetime import date


def get_urls(category):
    urls = []
    page = 1
    while True:
        print(f'Parsing urls on page {page} of category {category}...', end='\r')
        r = requests.get(f'https://www.ftvnews.com.tw/tag/{category}/{page}')
        soup = BeautifulSoup(r.text)
        
        links = ['https://www.ftvnews.com.tw' + item.a['href'] for item in soup.find_all('li',class_='col-lg-4')
                if is_valid_date(item.find(class_='time').text.replace('/' , '-').split(' ')[0])]

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
    ('政治'    , 'politics'),
    ('國際'   , 'world'),
    ('生活'   , 'life'),
    ('健康'    , 'health'),
    ('財經', 'finance'),
]

for category, label in categories:
    urls = get_urls(category)
    with open(f'urls/ftv-{label}-urls-{today}.txt', 'w') as f:
        for url in urls:
            f.write(url + '\n')
