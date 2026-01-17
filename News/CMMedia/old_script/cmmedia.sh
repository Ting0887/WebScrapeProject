#!/bin/sh

cd /home/tingyang0518/scraper_codes_tingyang/cmmedia/
mkdir -p urls
mkdir -p json
python3 cmmedia-urls.py && python3 cmmedia-articles.py
