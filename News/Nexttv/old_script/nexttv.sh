#!/bin/sh

cd /home/tingyang0518/scraper_codes_tingyang/nexttv/
mkdir -p urls
mkdir -p json
python3 nexttv-urls.py && python3 nexttv-articles.py
