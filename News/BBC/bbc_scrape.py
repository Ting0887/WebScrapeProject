import datetime
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from News.common.scraper_utils import build_end_date, create_session, get_soup, join_text, write_json_records


OUTPUT_BASE_DIR = os.environ.get("NEWS_OUTPUT_DIR", "/home/ftp_246/data_1/news_data")


def parse_bbc_list_date(date_text):
    try:
        return datetime.datetime.strptime(date_text, "%H:%M %B %d, %Y").strftime("%Y-%m-%d")
    except Exception:
        return ""


def scrape_link(session, cate_id, label, category, end_date):
    urls = []
    page = 1
    domain_url = "https://www.bbc.com/zhongwen/trad/topics/"
    while True:
        url = f"{domain_url}{cate_id}/page/{page}"
        print(url)
        try:
            soup = get_soup(session, url, sleep_seconds=0.3)
        except Exception as error:
            print(f"skip page by request error: {error}")
            break

        posts = soup.find_all("article")
        if not posts:
            break

        stop_by_date = False
        for item in posts:
            title_node = item.find("span", "lx-stream-post__header-text gs-u-align-middle")
            title = title_node.get_text(strip=True) if title_node else ""

            link_node = item.find("a", "qa-heading-link lx-stream-post__header-link")
            href = link_node.get("href") if link_node else ""
            link = f"https://www.bbc.com{href}" if href else ""

            date_node = item.find("span", "qa-post-auto-meta")
            date_time = parse_bbc_list_date(date_node.get_text(strip=True)) if date_node else ""
            if not date_time:
                continue
            if date_time < end_date:
                stop_by_date = True
                break
            if link:
                urls.append((title, link, date_time))

        if stop_by_date:
            break

        no_content = soup.find("span", "gs-u-display-block gs-u-mb qa-no-content-message")
        if no_content and "Oops! It looks like there is no content" in no_content.get_text(strip=True):
            break
        page += 1

    if urls:
        scrape_content(session, label, category, urls)


def scrape_content(session, label, category, urls):
    data_collect = []
    for title, link, date_time in urls:
        try:
            soup = get_soup(session, link, sleep_seconds=0.2)
        except Exception as error:
            print(f"skip article by request error: {error}")
            continue

        content_nodes = soup.find_all("p", "bbc-mj7obe e1cc2ql70")
        if not content_nodes:
            content_nodes = soup.select("main p")
        content = join_text(content_nodes)
        article = {
            "title": title,
            "author": "",
            "date_time": date_time,
            "label": label,
            "link": link,
            "content": content,
            "keyword": "",
        }
        data_collect.append(article)

    if data_collect:
        file_path = write_json_records(
            records=data_collect,
            source_name="BBC",
            category=category,
            base_output_dir=OUTPUT_BASE_DIR,
            file_prefix="bbc",
        )
        print(f"saved: {file_path}")

if __name__ == '__main__':
    end_date = build_end_date(days_back=1)
    print(end_date)
    session = create_session()

    categories = [('c83plve5vmjt','國際','global'),
                  ('c9wpm0e5zv9t','兩岸','china'),
                  ('c32p4kj2yzqt','科技','tech'),
                  ('cq8nqywy37yt','財經','finance')]
    for cate_id,label,category in categories:
        scrape_link(session, cate_id, label, category, end_date)

