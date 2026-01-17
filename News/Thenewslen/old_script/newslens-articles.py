#!/usr/bin/env python3

import requests
import json
from bs4 import BeautifulSoup
from datetime import date
import subprocess # to run jq
import os # to delete temp files


def parse_content(url):
    print('Parsing article content: ' + url, end='\r')

    try:
        soup = BeautifulSoup(requests.get(url).text)
        article = {}

        article['url'] = url
        article['title'] = soup.find(class_='article-title').text.strip()
        info = soup.find(class_='article-info').text.strip().split(', ')
        article['date'] = info[0]
        article['label'] = info[1]

        article['summary'] = soup.find(class_='WhyNeedKnow').p.text.strip()
        article['content'] = ''.join(
            p.text for p in
            soup.select('.article-content > p'))
        # Not all articles have tags/keywords
        try:
            article['keywords'] = [a['title']
                                   for a in
                                   soup.find(class_='tags').select('a')]
        except:
            pass

        return article

    except Exception as err:
        print('Error: could not parse.')
        print(err)

today = date.today()

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
    print(f'\nParsing articles in category {category}...')
    with open(f'urls/tnl-{category}-urls-{today}.txt', 'r') as f:
        urls = [line.strip() for line in f]

    tmp_file = f'json/tnl-{category}-tmp.json'
    with open(tmp_file, 'w', encoding='utf8') as f:
        for url in urls:
            json.dump(parse_content(url),
                      f,
                      ensure_ascii=False)
            f.write('\n')

    filename = f'json/tnl-{category}-{today}.json'
    subprocess.run(f"jq -s '.' {tmp_file} > {filename}", shell=True)
    os.remove(tmp_file)
