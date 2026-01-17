#!/bin/sh

cd /home/tingyang0518/scraper_codes_tingyang/thenewslens/
mkdir -p urls
mkdir -p json
python3 newslens-urls.py && python3 newslens-articles.py
