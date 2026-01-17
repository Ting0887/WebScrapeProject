#!/bin/sh

cd /home/tingyang0518/scraper_codes_tingyang/tvbs/
mkdir -p urls
mkdir -p json
python3 tvbs-urls.py && python3 tvbs-articles.py
