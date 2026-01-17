#!/bin/sh

cd /home/tingyang0518/scraper_codes_tingyang/ttv/
mkdir -p urls
mkdir -p json
python3 ttv-urls.py && python3 ttv-articles.py
