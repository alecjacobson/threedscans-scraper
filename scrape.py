#!/usr/bin/env python3
"""
Scrapes all .stl.zip files from https://threedscans.com/ and downloads them locally.
Maintains a cache so re-runs skip already-downloaded files.
"""

import json
import os
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://threedscans.com/"
DOWNLOAD_DIR = Path("downloads")
CACHE_FILE = Path("cache.json")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; threedscans-downloader/1.0)"}
DELAY = 1.0  # seconds between requests


def load_cache() -> set:
    if CACHE_FILE.exists():
        return set(json.loads(CACHE_FILE.read_text()))
    return set()


def save_cache(cache: set):
    CACHE_FILE.write_text(json.dumps(sorted(cache), indent=2))


def get_soup(url: str) -> BeautifulSoup | None:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    time.sleep(DELAY)
    return BeautifulSoup(resp.text, "html.parser")


def get_index_pages() -> list[str]:
    """Crawl paginated index pages and return all item URLs.
    The site uses infinite scroll so there are no visible 'next' links —
    we probe /page/N/ until we get a 404.
    """
    item_urls = []
    page = 1
    while True:
        url = BASE_URL if page == 1 else f"{BASE_URL}page/{page}/"
        print(f"  Index page {page}: {url}")
        soup = get_soup(url)

        if soup is None:
            break

        articles = soup.select("article.post a[href][rel='bookmark']")
        if not articles:
            break

        for a in articles:
            href = a["href"]
            if href not in item_urls:
                item_urls.append(href)

        page += 1

    return item_urls


def get_download_links(item_url: str) -> list[str]:
    """Return all download URLs from an item page (any format .zip)."""
    soup = get_soup(item_url)
    if soup is None:
        return []
    links = []
    for a in soup.find_all("a", href=True):
        if a.get_text().strip() == "Download Scan":
            links.append(a["href"])
    return links


def download_file(url: str, cache: set):
    filename = urlparse(url).path.split("/")[-1]
    dest = DOWNLOAD_DIR / filename

    if url in cache:
        print(f"    [skip] {filename}")
        return

    if dest.exists():
        print(f"    [skip] {filename} (file exists)")
        cache.add(url)
        save_cache(cache)
        return

    print(f"    [download] {filename}")
    resp = requests.get(url, headers=HEADERS, timeout=60, stream=True)
    resp.raise_for_status()

    # Download to a .part file and rename only on success, so an interrupted
    # run leaves no truncated file that a later run would mistake for complete.
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    partial = dest.with_suffix(dest.suffix + ".part")
    with open(partial, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    partial.rename(dest)

    cache.add(url)
    save_cache(cache)
    time.sleep(DELAY)


def main():
    cache = load_cache()
    print(f"Cache loaded: {len(cache)} files already downloaded")

    print("\nCrawling index pages...")
    item_urls = get_index_pages()
    print(f"Found {len(item_urls)} item pages")

    for i, item_url in enumerate(item_urls, 1):
        print(f"\n[{i}/{len(item_urls)}] {item_url}")
        try:
            links = get_download_links(item_url)
            if not links:
                print("    (no download links found)")
                continue
            for link in links:
                download_file(link, cache)
        except requests.RequestException as e:
            print(f"    [error] {e}")

    print(f"\nDone. {len(cache)} files in cache.")


if __name__ == "__main__":
    main()
