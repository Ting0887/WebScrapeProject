#!/usr/bin/env python3

import requests
import json
from bs4 import BeautifulSoup
import subprocess # to run jq
import os # to delete temp files
import datetime


def parse_content(url):
    print('Parsing article content: ' + url, end='\r')

    try:
        soup = BeautifulSoup(requests.get(url).text)
        article = {}

        # blog
        article['url'] = url
        article['label'] = ':'.join(x.text for x in soup.select('.breadcrumb-item')[1:])
        article['title'] = soup.find('h1', class_='Single-title-main').text
        article['author'] = soup.find(class_='Single-author-row-name').text.strip()
        article['date'] = soup.select('.Single-author-row > .Padding-left > span')[1].text
        article['summary'] = ''.join(
            p.text for p in
            soup.select('.Single-summary-content > p'))
        article['content'] = ''.join(
            p.text for p in
            soup.select('.Single-article > p'))
        # Not all articles have tags/keywords
        try:
            article['keywords'] = [a.text for a in
                                   soup.select('.Single-tag-list > a')]
        except:
            pass

        return article

    except Exception as err:
        print('Error: could not parse.')
        print(err)


categories = [
    'business',
    'style'
    ]

today = datetime.date.today().isoformat()

for category in categories:
    print(f'\nParsing articles in category {category}...')
    with open(f'urls/bw-{category}-urls-{today}.txt', 'r') as f:
        urls = [line.strip()
                for line in f
                # only take 'blog' articles,
                # ignore sponsored and magazine content
                if '/blog/' in line]

    tmp_file = f'json/bw-{category}-tmp.json'
    with open(tmp_file, 'w', encoding='utf8') as f:
        for url in urls:
            json.dump(parse_content(url),
                      f,
                      indent=4,
                      ensure_ascii=False)
            f.write('\n')

    filename = f'json/bw-{category}-{today}.json'
    subprocess.run(f"jq -s '.' {tmp_file} > {filename}", shell=True)
    os.remove(tmp_file)
