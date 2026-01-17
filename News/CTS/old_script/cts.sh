#!/bin/sh

cd /home/tingyang0518/scraper_codes_tingyang/cts/
mkdir -p urls
mkdir -p json
racket cts-urls.rkt && racket cts-articles.rkt
