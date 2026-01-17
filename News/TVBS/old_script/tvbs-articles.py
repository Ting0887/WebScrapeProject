#!/usr/bin/env python3

import requests
import json
from datetime import date
from bs4 import BeautifulSoup
import subprocess # to run jq
import os # to delete temp files
import re


def parse_content(url, label):
    print('Parsing article content: ' + url, end='\r')

    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text)
        article = {}

        article['url'] = url
        article['title'] = soup.find(class_='title').text
        # Right now (2021-01-04) the time is in the .author class, written as:
        # 發佈時間：2021/01/04 09:16 | 最後更新時間：2021/01/04 09:16
        # We take the time of the latest change.
        article['date'] = extract_date(soup.find(class_='author').text)
        article['label'] = label
        # Junk content that we don't need to save.
        # This changes and needs to be kept updated.
        stopstrings = ['&nbsp',
                       '最HOT話題在這！想跟上時事，快點我加入TVBS新聞LINE好友！',
                       '～開啟小鈴鐺',
                       'TVBS YouTube頻道',
                       '新聞搶先看',
                       '快點我按讚訂閱',
                       '～',
                       '55直播線上看',
                       '現正直播']
        article['content'] = ''.join(
            s for s in soup.find(class_='article_content').stripped_strings
        if s not in stopstrings)

        try:
            # In the new website, the keywords are hashtags,
            # so we delete the leading # char.
            article['keywords'] = [a.text.lstrip('#') for a in soup.select_one('.article_keyword')]
        except:
            pass

        return article

    except Exception as err:
        print('Error: could not parse.')
        print(err)


def extract_date(datestr):
    if '最後更新時間' in datestr:
        return datestr.split('最後更新時間：')[1].strip()
    else:
        return datestr.split('發佈時間：')[1].strip()



categories = [
    ('要聞', 'politics'),
    ('社會', 'local'),
    ('全球', 'world'),
    ('健康', 'health'),
    ('理財', 'money'),
    ('科技', 'tech'),
    ('生活', 'life'),
]

today = date.today()

for label, category in categories:
    print(f'\nParsing articles in category {category}...')
    with open(f'urls/tvbs-{category}-urls-{today}.txt', 'r') as f:
        urls = [line.strip() for line in f]

    tmp_file = f'json/tvbs-{category}-tmp.json'
    with open(tmp_file, 'w', encoding='utf8') as f:
        for url in urls:
            json.dump(parse_content(url, label),
                      f,
                      ensure_ascii=False)
            f.write('\n')

    filename = f'json/tvbs-{category}-{today}.json'
    subprocess.run(f"jq -s '.' {tmp_file} > {filename}", shell=True)
    os.remove(tmp_file)
