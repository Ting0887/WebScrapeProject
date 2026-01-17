#/bin/sh

cd /home/tingyang0518/scraper_codes_tingyang/gvm/
mkdir -p urls
mkdir -p json
python3 gvm-urls.py && python3 gvm-articles.py
