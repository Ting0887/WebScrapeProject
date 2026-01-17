import json
import requests
from datetime import date, timedelta
from bs4 import BeautifulSoup

def get_urls(date):
    # The 'realtime' news of TVBS are searchable by date.
    # The page first loads 90 articles, and the rest can
    # be seen by scrolling down the page. Alternatively,
    # we can use their API to scrape these articles without
    # using selenium.
    #
    # We begin by parsing the first 90 article links as normal.
    date_url = f'https://news.tvbs.com.tw/realtime/{date}'
    soup = BeautifulSoup(requests.get(date_url).text)
    all_urls = [a['href'] for a in soup.select('#realtime_data > li > a')]
    # We then filter out unneeded urls and use that list
    # as the base list, to which we add new links from API calls.
    # Site-internal urls on TVBS have the form
    # '/live/news4live/2888' or '/life/1363792',
    # so we extract the word between the first two slashes
    # and check if it's a category that we want to scrape.
    urls = [url for url in all_urls if url.split('/')[1] in categories]
    # `offset` is a counter that is incremented with each API call,
    # see the while loop below.
    offset = 0
    # `liveoffset` is the number of /live/ news links in the first 90
    # links (given when the page first loads). For a more detailed
    # explanation, see the while loop below.
    liveoffset = len([url for url in all_urls if url.startswith('/live/')])
    # Then we use the API to keep loading new articles until there
    # are none.
    while True:
        # TVBS treats /live/ links as special in their API, and counts
        # them separately. The API contains three numbers: newsoffset,
        # ttalkoffset, and liveoffset.
        # From what I can tell, ttalkoffset is always 0.
        # liveoffset is the number of /live/ links seen so far,
        # and newsoffset is the number of non-/live/ links seen.
        # The API loads new links in groups of 6. Thus each time we
        # need to check if there are any /live/ links in the last API
        # call, and if yes, add their amount to the liveoffset number.
        # We can calculate the newsoffset number with the following formula:
        #     90 + (6 * offset) - liveoffset
        # That is, 90 (the initial number of loaded articles) plus the
        # amount of articles loaded so far (6 times the number of API calls)
        # minus the number of /live/ links.
        r = requests.get('https://news.tvbs.com.tw/news/'
                         + f'LoadMoreOverview_realtime?showdate={date}'
                         + f'&newsoffset={90 + (6 * offset) - liveoffset}'
                         + f'&ttalkoffset=0&liveoffset={liveoffset}')
        soup = BeautifulSoup(r.text)
        # Links received through the API are quoted and escaped,
        # so we need to remove all " and \ first.
        # `hrefs` contains all the urls from the API call.
        hrefs = [a['href'].replace('\\', '').replace('"', '') for a in soup.select('a')]
        # `links` contains only those urls we want to parse.
        links =  [link for link in hrefs if link.split('/')[1] in categories]
        # If our `liveoffset` calculations were correct, once we have
        # received all the news articles for the day, all subsequent
        # API requests will return an empty list, so we check for that
        # to break the loop.
        if not hrefs:
            break
        else:
            urls += links
            offset += 1
            liveoffset += len([href for href in hrefs if href.startswith('/live/')])

    return urls


def sort_urls(urls):
    for url in urls:
        cat = url.split('/')[1]
        today = date.today()
        with open(f'urls/tvbs-{cat}-urls-{today}.txt', 'a') as f:
            f.write(f'https://news.tvbs.com.tw{url}' + '\n')

categories = [
    'local',
    'politics',
    'world',
    'health',
    'money',
    'tech',
    'life',
]


def one_month_before(d):
    if d.month == 1:
        return d.replace(year = d.year - 1, month = 12)
    else:
        return d.replace(month = d.month - 1)

# Instead of scraping by category, like we do in other sites,
# we scrape by date, and then sort the links into categories.
date = date.today()
one_month_ago = one_month_before(date.today())
while date >= one_month_ago:
    print(f'Parsing urls from {date}...', end='\r')
    date -= timedelta(days=1)
    urls = get_urls(date)
    sort_urls(urls)
