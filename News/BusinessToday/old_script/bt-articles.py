#!/usr/bin/env python3

import requests
import json
from bs4 import BeautifulSoup
import subprocess # to run jq
import os # to delete temp files
from datetime import date


def parse_content(url):
    print('Parsing article content: ' + url, end='\r')

    try:
        soup = BeautifulSoup(requests.get(url).text)
        article = {}

        article['url'] = url
        article['author'] = soup.find(class_='context__info-item--author').text
        article['title'] = soup.find(class_='article__maintitle').text
        article['date'] = soup.find(class_='context__info-item--date').text
        article['label'] = soup.find(class_='context__info-item--type').text


        article['content'] = ''.join(
            p.text.strip()
            for p in
            soup.find(
                itemprop='articleBody'
            ).select('div > div > p'))
        return article

    except Exception as err:
        print('Error: could not parse.')
        print(err)


categories = [
    'finance',
    'health'
    ]

today = date.today()

for category in categories:
    print(f'Parsing articles in category {category}...')
    with open(f'urls/bt-{category}-urls-{today}.txt', 'r') as f:
        urls = [line.strip() for line in f]

    tmp_file = f'json/bt-{category}-tmp.json'
    with open(tmp_file, 'w', encoding='utf8') as f:
        for url in urls:
            json.dump(parse_content(url),
                      f,
                      ensure_ascii=False)
            f.write('\n')

    filename = f'json/bt-{category}-{today}.json'
    subprocess.run(f"jq -s '.' {tmp_file} > {filename}", shell=True)
    os.remove(tmp_file)
