import argparse
import subprocess
import sys
from pathlib import Path


SCRIPT_MAP = {
    "bbc": Path("News/BBC/bbc_scrape.py"),
    "4wayvoice": Path("News/4wayvoice/4wayvoice_scrape.py"),
    "appledaily": Path("News/Appledaily/applenews.py"),
    "bcc": Path("News/BCC/BCC_crawler.py"),
    "businesstoday": Path("News/BusinessToday/bt-article.py"),
    "businessweekly": Path("News/BusinessWeekly/bw-article.py"),
    "chinatimes": Path("News/ChinaTimes/Chinatimes_news.py"),
    "civilmedia": Path("News/CivilMedia/civilmedia_scrape.py"),
    "cmmedia": Path("News/CMMedia/cmmedia-article.py"),
    "ebc": Path("News/EBC/ebc_news.py"),
    "cna": Path("News/CNA/cna_news.py"),
    "cnews": Path("News/CNews/cnews-article.py"),
    "coolloud": Path("News/Coolloud/Coolloud_scrape.py"),
    "ctee": Path("News/Ctee/ctee_news.py"),
    "ctitv": Path("News/Ctitv/Ctitv_news.py"),
    "cts": Path("News/CTS/cts-article.py"),
    "ctv": Path("News/CTV/ctv-article.py"),
    "ctwant": Path("News/CTWant/ctwant_news.py"),
    "daai": Path("News/Daai/Daai_realtimenews.py"),
    "epochtimes": Path("News/EpochTimes/epochtime_news.py"),
    "eranews": Path("News/EraNews/eranews.py"),
    "ettoday": Path("News/Ettoday/ettoday_news.py"),
    "ftvnews": Path("News/FTVNews/ftv-article.py"),
    "gvm": Path("News/gvm/gvm-article.py"),
    "libertytimes": Path("News/LibertyTimes/Libertytimes_scrape.py"),
    "limedia": Path("News/LiMedia/limedia_scrape.py"),
    "linetoday": Path("News/linetoday/Linetoday_scrape.py"),
    "mirrormedia": Path("News/MirrorMedia/mirror_news.py"),
    "newsmarket": Path("News/NewsMarket/Newsmarket.py"),
    "newtalk": Path("News/NewTalk/newtalk_news.py"),
    "nexttv": Path("News/Nexttv/nexttv-article.py"),
    "nownews": Path("News/Nownews/Nownews_all.py"),
    "ntdtv": Path("News/ntdtv/ntdtv-article.py"),
    "pchomenews": Path("News/PCHomeNews/PCHome.py"),
    "peoplenews": Path("News/PeopleNews/people_news.py"),
    "pts": Path("News/PTS/pts_realtime.py"),
    "tvbs": Path("News/TVBS/tvbs-article.py"),
    "setn": Path("News/Setn/setn_news.py"),
    "sina": Path("News/sina/sina-article.py"),
    "storm": Path("News/Storm/storm_news.py"),
    "taipeitimes": Path("News/TaipeiTimes/tt_crawler.py"),
    "taronews": Path("News/TaroNews/taro_crawler_news.py"),
    "thenewslen": Path("News/Thenewslen/Thenewslens-article.py"),
    "ttv": Path("News/TTV/ttv-article.py"),
    "udn": Path("News/udn/udn_news.py"),
    "upmedia": Path("News/UpMedia/upmedia_news.py"),
    "wealth": Path("News/Wealth/wealth.py"),
    "yahoo": Path("News/YahooNews/yahoo_news.py"),
}


def run_script(script_key):
    script_path = SCRIPT_MAP[script_key]
    command = [sys.executable, str(script_path)]
    print(f"[run] {script_key}: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"[ok] {script_key}")
        if result.stdout.strip():
            print(result.stdout.strip())
        return True

    print(f"[failed] {script_key} (exit={result.returncode})")
    if result.stdout.strip():
        print("[stdout]")
        print(result.stdout.strip())
    if result.stderr.strip():
        print("[stderr]")
        print(result.stderr.strip())
    return False


def parse_args():
    parser = argparse.ArgumentParser(description="Run selected News scrapers in batch.")
    parser.add_argument(
        "--targets",
        nargs="+",
        default=list(SCRIPT_MAP.keys()),
        choices=list(SCRIPT_MAP.keys()),
        help="Scrapers to run. Defaults to all supported refactored scripts.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    failed = []
    for target in args.targets:
        ok = run_script(target)
        if not ok:
            failed.append(target)

    if failed:
        print(f"Batch finished with failures: {', '.join(failed)}")
        raise SystemExit(1)

    print("Batch finished successfully")


if __name__ == "__main__":
    main()
