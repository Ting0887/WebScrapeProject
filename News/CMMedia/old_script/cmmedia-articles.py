import requests
import re
import json
from datetime import date
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import subprocess # to run jq
import os # to delete tmp files

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')

def parse_content(article_number, label):
    print(f'Parsing article number {article_number}...',
          end='\r')
    url = f'https://www.cmmedia.com.tw/home/articles/{article_number}'
    soup = BeautifulSoup(requests.get(url).text)
    article = {}
    article['url'] = url
    article['title'] = soup.find(class_='article_title').text
    article['author'] = soup.find(class_="article_author-bar").span.text
    article['date'] = soup.find(class_="article_author-bar").span.next_sibling.text
    article['label'] = label
    article['content'] = ''.join(p.text for p in soup.select(".article_content > p"))

    browser = webdriver.Chrome('/home/tingyang0518/chromedriver', options=chrome_options)
    browser.get(url)
    sleep(2)
    add_cont = browser.find_element_by_id('articleAddon-container')
    keysoup = BeautifulSoup(add_cont.get_attribute('innerHTML'))
    tags = keysoup.find_all(class_=re.compile(r'article__tag.*'))
    article['keywords'] = [t.string for t in tags]
    browser.quit()
    return article

categories = [
    ('politics', '政治'),
    ('life'    , '生活'),
    ('finance' , '財經'),
]

today = date.today()

for category, label in categories:
    with open(f'urls/cmmedia-{category}-urls-{today}.txt', 'r') as f:
        article_numbers = [line.strip() for line in f]
    
    tmp_file = f'json/cmmedia-{category}-tmp.json'
    with open(tmp_file, 'w', encoding='utf8') as f:
        for article_number in article_numbers:
            print(f'Parsing article content: {article_number}', end='\r')
            try:
                json.dump(parse_content(article_number, label), f, ensure_ascii=False)
                f.write('\n')
            except Exception as e:
                print(e)
                print('\nError: could not parse.')
    
    filename = f'json/cmmedia-{category}-{today}.json'
    subprocess.run(f"jq -s '.' {tmp_file} > {filename}", shell=True)
    os.remove(tmp_file)
