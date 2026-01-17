#!/bin/sh

cd /home/tingyang0518/scraper_codes_tingyang/businessweekly/
mkdir -p urls
mkdir -p json
python3 bw-urls.py && python3 bw-articles.py
