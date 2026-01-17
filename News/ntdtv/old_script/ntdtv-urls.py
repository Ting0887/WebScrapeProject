#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from datetime import date


def get_urls(category):
    urls = set()
    page = 1
    while True:
        print(f'Parsing page {page} of category {category}...')
        r = requests.get(f'https://www.ntdtv.com/b5/{category}/{page}')
        if r.status_code == 404:
            print(f'Stopped parsing at page {page}')
            break
        soup = BeautifulSoup(r.text)
        headlines = soup.select('.post_list .text')
        links = [h.find(class_='title').a['href']
                 for h in headlines
                 if is_valid_date(h.find(class_='date').text)]
        urls = urls.union(links)
        if not links:
            print(f'Stopped parsing at page {page}')
            break
        page += 1
    return urls

def is_valid_date(datestr):
    if '前' in datestr:
        return True
    if date.fromisoformat(datestr) >= one_month_before(today):
        return True
    return False


def one_month_before(d):
    if d.month == 1:
        return d.replace(year = d.year - 1, month = 12)
    else:
        return d.replace(month = d.month - 1)


today = date.today()

categories = [
    ('prog202', '國際', 'world'),
    ('prog204', '大陸', 'china'),
    ('prog203', '美國', 'usa'),
    ('prog206', '台灣', 'taiwan'),
    ('prog205', '港澳', 'hk'),
    ('prog208', '財經', 'finance'),
    ('prog1255', '健康', 'health')
]

for category, _, label_en in categories:
    urls = sorted(list(get_urls(category)))
    with open(f'urls/ntdtv-{label_en}-urls-{today}.txt', 'w') as f:
        for url in urls:
            f.write(url + '\n')
