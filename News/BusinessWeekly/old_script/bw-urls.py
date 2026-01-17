#!/usr/bin/env python3


import requests
from bs4 import BeautifulSoup
from datetime import date

def get_urls(number):
    urls = []
    page = 1
    while True:
        print(f'Parsing page {page} of category {number}...',
              end='\r')
        r = requests.post(
            'https://www.businessweekly.com.tw/ChannelAction/LoadBlock/',
            data = {'Start': 1 + (20 * (page - 1)),
                    'End': 20 * page,
                    'ID': number})
        soup = BeautifulSoup(r.text)
        articles = [a['href'] for a in
                    soup.select('.Article-content > a')]
        mainpage = 'https://www.businessweekly.com.tw'
        links = [link
                 if link.startswith(mainpage)
                 else mainpage + link
                 for link in articles]
        urls = links + urls
        dates = [x.text for x in
                 soup.select(
                     '.Article-img-caption > .Article-footer > .Article-date')]
        if any(not in_last_month(d) for d in dates):
            print(f'\nStopped parsing on page {page}.')
            break
        else:
            page += 1

    return urls


def in_last_month(datestr):
    formatted = datestr.replace('.', '-')
    article_date = date.fromisoformat(formatted)
    one_month_ago = one_month_before(date.today())
    return article_date >= one_month_ago


def one_month_before(d):
    if d.month == 1:
        return d.replace(year = d.year - 1, month = 12)
    else:
        return d.replace(month = d.month - 1)


categories = [
    ('business', '0000000319'),
    ('style' , '0000000337')
]

today = date.today().isoformat()

for category, number in categories:
    urls = get_urls(number)
    with open(f'urls/bw-{category}-urls-{today}.txt', 'w') as f:
        for url in urls:
            f.write(url + '\n')
