#!/bin/sh

cd /home/tingyang0518/scraper_codes_tingyang/ctv/
mkdir -p urls
mkdir -p json
python3 ctv-urls.py && python3 ctv-articles.py
