#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from datetime import date

def get_urls(category):
    urls = []
    page = 1
    while True:
        print(f'Parsing page {page} of category {category}...',
              end='\r')
        r = requests.get(
            f'https://www.thenewslens.com/category/{category}?page={page}')
        soup = BeautifulSoup(r.text)

        # Select only non-sponsored links
        all_containers = set(soup.select('.list-container'))
        sponsored_containers = set(soup.select('.sponsoredd-container'))
        containers = all_containers - sponsored_containers

        links = list(
            # Some pages are 'interactive' or 'feature',
            # we don't want those
            filter(lambda link: '/article/' in link,
                   [x.find(class_='title').a['href']
                    for x in containers]))
        urls = urls + links
        dates = [date.fromisoformat(
            # .time is formatted as 'YYYY/MM/DD |', so we strip and
            # reformat it to be able to read the date.
            x.find(class_='time').text.strip(' |').replace('/','-'))
                 for x in containers]
        if any(not d >= one_month_before(today) for d in dates):
            print(f'\nStopped parsing on page {page}.')
            break
        else:
            page += 1

    return urls


today = date.today()

def one_month_before(d):
    if d.month == 1:
        return d.replace(year = d.year - 1, month = 12)
    else:
        return d.replace(month = d.month - 1)

categories = [
    'world',
    'china',
    'health',
    'lifestyle',
    'politics',
    'economy',
    'society',
    'science',
    'tech',
]

for category in categories:
    urls = get_urls(category)
    with open(f'urls/tnl-{category}-urls-{today}.txt', 'w') as f:
        for url in urls:
            f.write(url + '\n')
