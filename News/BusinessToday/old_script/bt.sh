#!/bin/sh

cd /home/tingyang0518/scraper_codes_tingyang/businesstoday/
mkdir -p urls
mkdir -p json
python3 bt-urls.py && python3 bt-articles.py
