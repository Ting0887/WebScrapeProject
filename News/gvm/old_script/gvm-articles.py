import requests
import json
from bs4 import BeautifulSoup
from datetime import date
import subprocess # to run jq
import os # to delete temp files


def parse_content(url, label):
    soup = BeautifulSoup(requests.get(url).text)
    article = {}
    text = soup.find(id='main_content').article
    article['url'] = url
    article['title'] = text.section.h1.text
    article['author'] = text.find('div', class_="pc-bigArticle").a.text
    article['date'] = text.find(class_='article-time').text
    article['label'] = label
    article['content'] = text.find(
        class_='article-content').text.strip()
    try:
        article['keywords'] = [k.text for k in
                               text.find(class_='article-keyword').find_all('a')]
    except:
        pass

    return article

categories = [
    ('news'    , '時事熱點'),
    ('world'   , '國際'),
    ('money'   , '金融'),
    ('tech'    , '科技'),
    ('business', '產經'),
    ('life'    , '生活'),
]

today = date.today()

for category, label in categories:
    with open(f'urls/gvm-{category}-urls-{today}.txt', 'r') as f:
        urls = [line.strip() for line in f]

    tmp_filename = f'json/gvm-{category}-tmp.json'
    with open(tmp_filename, 'w') as f:
        print(f'Parsing category {category}...')
        for url in urls:
            print(f'Parsing article content: {url}', end='\r')
            try:
                json.dump(parse_content(url, label),
                          f,
                          ensure_ascii=False)
                f.write('\n')
            except:
                print('Error: could not parse.')
        print('\n')

    out_filename = f'json/gvm-{category}-{today}.json'
    subprocess.run(f"jq -s '.' {tmp_filename} > {out_filename}", shell=True)
    os.remove(tmp_filename)
