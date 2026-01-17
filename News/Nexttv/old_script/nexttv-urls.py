#!/usr/bin/env python3

import requests
import json
from datetime import date

def get_urls(number, category):
    page = 1
    with open(f'urls/nexttv-{category}-urls-{today}.txt', 'w') as f:
        while True:
            try:
                print(f'Parsing page {page} of category {number}...', end='\r')
                r = requests.post(
                    'http://www.nexttv.com.tw/m2o/loadmore.php',
                    data = {'offset' : 3 + (page - 1) * 6,
                            'count' : 6,
                            'column_id' : number})
                response = json.loads(r.text)
                links = [item['content_url'] for item in response
                        if date.fromisoformat(item['file_name'].split('/')[0]) \
                         >= one_month_before(today)]

                if not links:
                    print(f'\nStopped parsing on page {page}.')
                    break

                for link in links:
                    f.write(link + '\n')

                page += 1

            except:
                pass

    return ()

today = date.today()

def one_month_before(d):
    if d.month == 1:
        return d.replace(year = d.year - 1, month = 12)
    else:
        return d.replace(month = d.month - 1)

categories = [
    ('politics', 144),
    ('society', 145),
    ('finance', 147),
    ('world', 148),
    ('life', 149),
]

for category, number in categories:
    urls = get_urls(number, category)
