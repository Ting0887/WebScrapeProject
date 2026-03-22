import datetime
import json
import os
import time
from typing import Dict, Iterable, Optional

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
}


def build_end_date(days_back: int = 1) -> str:
    target_date = datetime.datetime.today() - datetime.timedelta(days=days_back)
    return target_date.strftime("%Y-%m-%d")


def create_session(
    retries: int = 3,
    backoff_factor: float = 0.5,
    headers: Optional[Dict[str, str]] = None,
) -> requests.Session:
    session = requests.Session()

    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("HEAD", "GET", "OPTIONS"),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(DEFAULT_HEADERS)
    if headers:
        session.headers.update(headers)
    return session


def get_soup(
    session: requests.Session,
    url: str,
    parser: str = "lxml",
    timeout: int = 20,
    sleep_seconds: float = 0.0,
) -> BeautifulSoup:
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    if sleep_seconds > 0:
        time.sleep(sleep_seconds)
    return BeautifulSoup(response.text, parser)


def join_text(elements: Iterable, sep: str = "") -> str:
    return sep.join(element.get_text(strip=False) for element in elements)


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_json_records(
    records,
    source_name: str,
    category: str,
    base_output_dir: str,
    file_prefix: str,
) -> str:
    folder_path = os.path.join(base_output_dir, source_name, category, time.strftime("%Y-%m"))
    ensure_dir(folder_path)
    file_name = f"{file_prefix}_{category}{time.strftime('%Y%m%d')}.json"
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, "w", encoding="utf-8") as output_file:
        json.dump(records, output_file, ensure_ascii=False, indent=2)
    return file_path
