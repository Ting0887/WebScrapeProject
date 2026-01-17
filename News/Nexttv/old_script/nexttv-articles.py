#!/usr/bin/env python3

import requests
import json
from bs4 import BeautifulSoup
from datetime import date
import subprocess # to run jq
import os # to delete temp files


def parse_content(url, label):
    print('Parsing article content: ' + url, end='\r')

    r = requests.get(url)
    r.encoding = 'utf8' # 避免亂碼出現
    soup = BeautifulSoup(r.text)
    article = {}

    article['url'] = url
    article['title'] = soup.find(class_='articletitle').text
    article['date'] = soup.find(class_='time').text
    article['label'] = label
    article['content'] = soup.find(class_='article-main').text.strip()

    return article


today = date.today()

categories = [
    ('politics', '政治'),
    ('society' , '社會'),
    ('finance' , '財經'),
    ('world'   , '國際'),
    ('life'    , '生活'),
]

for category, label in categories:
    print(f'\nParsing articles in category {category}...')
    with open(f'urls/nexttv-{category}-urls-{today}.txt', 'r') as f:
        urls = [line.strip() for line in f]

    tmp_file = f'json/nexttv-{category}-tmp.json'
    with open(tmp_file, 'w', encoding='utf8') as f:
        for url in urls:
            try:
                json.dump(parse_content(url, label),
                        f,
                        ensure_ascii=False)
                f.write('\n')
            except Exception as err:
                print('\nError: could not parse.')
                print(err)

    filename = f'json/nexttv-{category}-{today}.json'
    subprocess.run(f"jq -s '.' {tmp_file} > {filename}", shell=True)
    os.remove(tmp_file)
