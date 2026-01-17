#!/bin/sh

cd /home/tingyang0518/scraper_codes_tingyang/sina/
mkdir -p urls
mkdir -p json
python3 sina-urls.py && python3 sina-articles.py
