#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from datetime import date

def get_urls(category):
    urls = []
    page = 1
    while True:
        print(f'Parsing page {page} of category {category}...', end='\r')
        r = requests.get(f'https://news.ttv.com.tw/category/{category}/{page}')
        soup = BeautifulSoup(r.text)

        links = [li.a['href']
                 for li in
                 soup.select('.news-list li')
                 if find_date(li) >= one_month_before(today)]

        if not links:
            print(f'\nStopped parsing on page {page}.')
            break
        else:
            page += 1
            urls = urls + links

    return urls


def one_month_before(d):
    if d.month == 1:
        return d.replace(year = d.year - 1, month = 12)
    else:
        return d.replace(month = d.month - 1)

def find_date(li):
    date_time=li.find(class_='time').text.replace('.','-')
    year=int(date_time[:4])
    month=date_time[5:7]
    day=date_time[8:10]
    return date.fromisoformat(f'{year}-{month}-{day}')


categories = [
    ('政治', 'politics'),
    ('財經', 'finance'),
    ('社會', 'society'),
    ('國際', 'world'),
    ('生活', 'life'),
    ('健康', 'health'),
]

today = date.today()

for code, category in categories:
    urls = get_urls(code)
    with open(f'urls/ttv-{category}-urls-{today}.txt', 'w') as f:
        for url in urls:
            f.write(url + '\n')
