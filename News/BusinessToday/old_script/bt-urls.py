#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from datetime import date
import datetime
def get_urls(category):
    urls = set()
    page = 1
    while True:
        print(f'Parsing page {page} of category {category}...', end='\r')
        r = requests.get(f'http://www.businesstoday.com.tw/catalog/{category}/list/page/{page}/ajax')
        soup = BeautifulSoup(r.text)
        articles = [a for a in soup.find_all(class_='article__item')]
        #dates = [date.fromisoformat(p.text) for p in soup.find_all(class_='article__item-date')
        dates = soup.find_all('p','article__item-date')[-1].text.strip()
        links = [a['href'] for a in articles]
        urls = urls.union(links)
        page += 1
        if page == 5:
            break
        if dates < end_date:
            break

    print('\n')
    return urls

today = date.today()

#start date end date
start_date = datetime.datetime.today() #today
months = datetime.timedelta(days=30)  #last month
end_date = (start_date - months).strftime('%Y-%m-%d') 
    


categories = [
    ('finance', '80391'),
    ('health' , '183029')
]

for category, number in categories:
    urls = sorted(list(get_urls(number)))
    with open(f'urls/bt-{category}-urls-{today}.txt', 'w') as f:
        for url in urls:
            f.write(url + '\n')
