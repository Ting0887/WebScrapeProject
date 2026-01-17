#!/bin/sh

cd /home/tingyang0518/scraper_codes_tingyang/cnews/
mkdir -p urls
mkdir -p json
python3 cnews-urls.py && python3 cnews-articles.py
