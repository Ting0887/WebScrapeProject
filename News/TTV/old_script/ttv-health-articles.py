#!/usr/bin/env python3

import requests
import json
from bs4 import BeautifulSoup
from datetime import date, timedelta
import subprocess # to run jq
import os # to delete temp files


def parse_content(url):
    print('Parsing article content: ' + url)

    try:
        r = requests.get(url)
        r.encoding = 'utf8'
        soup = BeautifulSoup(r.text)
        article = {}

        article['url'] = url
        article['title'] = soup.find('h1').text.strip()
        info = [a.text for a in soup.select('.ReportDate > a')]
        article['date'] = soup.find(class_='date time').text.strip()
        article['label'] = soup.find('div', {'id': 'crumbs'}).find_all('li')[1].text
        article['content'] = soup.find('div', {'id': 'newscontent'}).text.strip()

        try:
            article['keywords'] = [a.text for a in soup.select('.news-status > .tag > li')]
        except:
            pass

        return article

    except Exception as err:
        print('Error: could not parse.')
        print(err)


categories = [
    #'politics',
    #'finance',
    #'society',
    #'world',
    #'life',
    'health',
]

category='health'

today = date.today() - timedelta(days=1)


with open(f'ttv-{category}-urls-{today}.txt', 'r') as f:
    urls = [line.strip() for line in f]

tmp_file = f'ttv-{category}-tmp.json'
with open(tmp_file, 'w', encoding='utf8') as f:
    for url in urls:
        json.dump(parse_content(url),
                  f,
                  ensure_ascii=False)
        f.write('\n')

filename = f'ttv-{category}-{today}.json'
subprocess.run(f"jq -s '.' {tmp_file} > {filename}", shell=True)
os.remove(tmp_file)
