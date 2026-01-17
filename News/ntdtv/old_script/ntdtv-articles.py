#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import date
import subprocess # to run jq
import os # to delete temp files


def parse_content(url, label):
    soup = BeautifulSoup(requests.get(url).text)
    article = {}
    try:
        article['url'] = url
        article['title'] = soup.find(class_='article_title').h1.text
        article['date'] = soup.find(class_='time').span.text
        article['label'] = label

        content = soup.find(class_='post_content').find_all('p')
        content_strings = [x.text.strip() for x in content]
        article['content'] = ''.join(content_strings)

        return article

    except Exception as err:
        print('Error: could not parse.')
        print(err)


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

for category, label, label_en in categories:
    print(f'\nParsing articles in category {label_en}...')
    with open(f'urls/ntdtv-{label_en}-urls-{today}.txt', 'r') as f:
        urls = [line.strip() for line in f]

    tmp_file = f'json/ntdtv-{label_en}-tmp.json'
    with open(tmp_file, 'w') as f:
        for url in urls:
            print(f'Parsing article content: {url}')
            json.dump(parse_content(url, label),
                      f,
                      ensure_ascii=False)
            f.write('\n')

    filename = f'json/ntdtv-{label_en}-{today}.json'
    subprocess.run(f"jq -s '.' {tmp_file} > {filename}", shell=True)
    os.remove(tmp_file)
