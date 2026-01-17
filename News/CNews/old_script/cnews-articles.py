#!/usr/bin/env python3

import requests
import json
from bs4 import BeautifulSoup
from datetime import date
import subprocess # to run jq
import os # to delete temp files


def parse_content(url, label):
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    soup = BeautifulSoup(requests.get(url,headers=headers,allow_redirects=False).text)
    article = {}

    article['url'] = url
    article['title'] = soup.find(id='articleTitle')\
                           .find(class_='_line')\
                           .strong.text.strip()
    article['date'] = soup.find(class_='date').text.strip()
    article['author'] = soup.find(class_='user').text.strip()
    article['label'] = label
    article['content'] = soup.find(
        class_='theme-article-content').article.text.strip()

    try:
        article['keywords'] = [a.text for a in
                               soup.select('.tags > a')]
    except:
        pass

    return article


categories = [
    ('新聞匯流', 'news'),
    ('政治匯流', 'politics'),
    ('國際匯流', 'global'),
    ('生活匯流', 'life'),
    ('健康匯流', 'health'),
    ('金融匯流', 'finance'),
    ('數位匯流', 'tech')
]

today = date.today()

for category, label in categories:
    with open(f'urls/cnews-{label}-urls-{today}.txt', 'r') as f:
        urls = [line.strip() for line in f]

    tmp_filename = f'json/cnews-{label}-tmp.json'
    with open(tmp_filename, 'w', encoding='utf8') as f:
        print(f'Parsing category {category}...')
        for url in urls:
            print('Parsing article content: ' + url, end='\r')
            try:
                json.dump(parse_content(url, category),
                          f,
                          ensure_ascii=False)
                f.write('\n')
            except Exception as err:
                print('\nError: could not parse.')
                print(err)
        print('\n')

    out_filename = f'json/cnews-{label}-{today}.json'
    subprocess.run(f"jq -s '.' {tmp_filename} > {out_filename}", shell=True)
    os.remove(tmp_filename)
