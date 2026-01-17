#!/bin/sh

cd /home/tingyang0518/scraper_codes_tingyang/ftv/
mkdir -p urls
mkdir -p json
python3 ftv-urls.py && racket ftv-articles.rkt
