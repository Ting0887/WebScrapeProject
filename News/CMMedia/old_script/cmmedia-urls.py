import requests
# import json
from datetime import date


#進cmmedia(F12),click a category(politics),in browser developer tools click "Network" and find 'articles?num=....'
#articles' ids in "Preview"->r.json(),創links的條件:取r.json()裡的ids，如果不曾在past_ids裡出現，就加進links
#如果links空了就停
def get_urls(category):
    urls = set()
    page = 1

    while True:
        print(f'Parsing urls on page {page} of category {category}...',end='\r')
        r = requests.get(f'https://www.cmmedia.com.tw/api/articles?num=12&page={page}&category={category}')

        links = {item['id'] for item in r.json() if item['id'] not in past_ids}
        if not links:
            print(f'\nStopped parsing category {category}.')
            break
        else:
            urls |= links
            page += 1
    
    return urls

categories = [
    ('politics', '政治'),
    ('life'    , '生活'),
    ('finance' , '財經'),
]

past_ids=set()
with open('cmmedia-ids.txt') as f:
    for line in f:
        past_ids.add(int(line))

for category, label in categories:
    urls = get_urls(category)
    past_ids |= urls
    with open(f'urls/cmmedia-{category}-urls-{date.today()}.txt', 'w') as f:
        for url in urls:
            f.write(str(url) + '\n')

with open(f'cmmedia-ids.txt', 'w') as f:
    for id_ in past_ids:
        f.write(str(id_) + '\n')
