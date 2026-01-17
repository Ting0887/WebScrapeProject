#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from datetime import date

def get_urls(category):
    urls = []
    page = 1
    while True:
        print(f'Parsing page {page} of category {category}...', end='\r')
        r = requests.get(f'http://new.ctv.com.tw/Category/{category}?PageIndex={page}',headers=headers)
        soup = BeautifulSoup(r.text)
        
        links = ['http://new.ctv.com.tw' + a['href']
                 for a in soup.select('.list > a')
                 if a['href'].startswith('/Article/')
                 and is_valid_date(a.find(class_='time').text)
                 ]
        
        if not links:
            print(f'\nStopped parsing on page {page}.')
            break
        
        urls = urls + links
        page += 1
    return urls

today = date.today()

def is_valid_date(timestr):
    d = date.fromisoformat(timestr.split()[0].replace('/', '-'))
    return d >= one_month_before(today)

def one_month_before(d):
    if d.month == 1:
        return d.replace(year = d.year - 1, month = 12)
    else:
        return d.replace(month = d.month - 1)


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36','Connection': 'keep-alive','Host': 'new.ctv.com.tw'}

categories = [
    ('popular', '十大發燒新聞'),
    ('life', '生活'),
    ('society', '社會'),
    ('world', '國際'),
    ('politics','政治')
]

for label, category in categories:
    urls = get_urls(category)
    with open(f'urls/ctv-{label}-urls-{today}.txt', 'w') as f:
        for url in urls:
            f.write(url + '\n')
