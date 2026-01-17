#!/usr/bin/env python3

import requests
import json
from bs4 import BeautifulSoup
from datetime import date
import subprocess # to run jq
import os # to delete temp files
import time
from selenium import webdriver


#chromedriver setting
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")
# if you don't want to open browser, add 18th line
#chrome_options.add_argument("--headless")
chrome_options.add_argument('--dns-prefetch-disable')
chrome_options.add_argument('disable-infobars')
chrome_options.add_argument('blink-settings=imagesEnabled=false')
chrome_options.add_argument("--disable-javascript")
chrome_options.add_argument("--disable-images")
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument("--disable-plugins")
chrome_options.add_argument("--in-process-plugins")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

ua = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"
chrome_options.add_argument("user-agent={}".format(ua))
driverPath = "/home/tingyang0518/chromedriver"
browser = webdriver.Chrome(driverPath,chrome_options=chrome_options)

def parse_content(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
               'Host': 'new.ctv.com.tw',
               'Connection': 'keep-alive'}
    print('Parsing article content: ' + url, end='\r')

    try:
        browser.get(url)
        soup = BeautifulSoup(browser.page_source,'lxml')
        article = {}
        time.sleep(2.5)
        article['url'] = url
        # CTV use pipes inside strings as separators, the philistines.
        article['title'] = soup.find(class_='title').text.split('│')[0].strip()
        # Note the pipe character is different here.
        article['date'] = soup.find(class_='author').text.split('|')[1].strip()
        article['label'] = soup.find(class_='tag').text
        article['content'] = soup.find(class_='editor').text.strip()

        return article

    except Exception as err:
        print('Error: could not parse.')
        print(err)


categories = [
    ('popular', '十大發燒新聞'),
    ('life', '生活'),
    ('society', '社會'),
    ('world', '國際'),
    ('politics','政治')
]

today = date.today()

for label, _ in categories:
    print(f'\nParsing articles in category {label}...')
    with open(f'urls/ctv-{label}-urls-{today}.txt', 'r') as f:
        urls = [line.strip() for line in f]

    tmp_file = f'json/ctv-{label}-tmp.json'
    with open(tmp_file, 'w', encoding='utf8') as f:
        for url in urls:
            json.dump(parse_content(url),
                      f,
                      ensure_ascii=False)
            f.write('\n')

    filename = f'json/ctv-{label}-{today}.json'
    subprocess.run(f"jq -s '.' {tmp_file} > {filename}", shell=True)
    os.remove(tmp_file)
