#!/usr/bin/env python3

import requests
import json
from bs4 import BeautifulSoup
from time import sleep
import subprocess # to run jq
import os # to delete temp files
from datetime import date


def parse_content(url, label):
    soup = BeautifulSoup(requests.get(url).text)
    article = {}

    article['url'] = url
    article['title'] = soup.find('h1').text.strip()
    source = soup.find('cite').a.text
    article['source'] = source
    article['date'] = soup.find('cite')\
                          .text\
                          .strip()\
                          [len(source):]\
                          .strip()\
                          .lstrip('(')\
                          .rstrip(')')
    article['label'] = label
    article['content'] = get_article_text(
        soup.find(class_='pcont'))

    return article

def get_article_text(contents):
    ps = ''.join(p.text.strip()
                 for p in
                 contents.find_all('p'))
    if ps != '':
        return ps
    else:
        return contents.text.strip()

categories = [
    ('政治', 'politics'),
    ('社會', 'society'),
    ('兩岸', 'china'),
    ('國際', 'global'),
    ('生活', 'life'),
    ('財經', 'finance'),
    ('科技', 'tech')
    ]

today = date.today().isoformat()

for label, category in categories:
    with open(f'urls/sina-{category}-urls-{today}.txt', 'r') as f:
        urls = sorted(line.strip() for line in f)

    tmp_filename = f'json/sina-{category}-tmp.json'
    with open(tmp_filename, 'w', encoding='utf8') as f:
        for url in urls:
            print('Parsing article content: ' + url)
            try:
                json.dump(parse_content(url, label),
                          f,
                          ensure_ascii=False)
                f.write('\n')
            except Exception as err:
                print('Error: could not parse.')
                print(err)
            sleep(10)

    out_filename = f'json/sina-{category}-{today}.json'
    subprocess.run(f"jq -s '.' {tmp_filename} > {out_filename}", shell=True)
    os.remove(tmp_filename)
