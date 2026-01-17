#!/bin/sh

cd /home/tingyang0518/scraper_codes_tingyang/ntdtv/
mkdir -p urls
mkdir -p json
python3 ntdtv-urls.py && python3 ntdtv-articles.py
