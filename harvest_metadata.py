#!/usr/bin/env python3
"""
Harvests per-object metadata (title, institution, date, material, scan method)
from each threedscans.com item page and writes metadata.json.

This is what attribution is built from: each downloaded file is tied back to its
source page and holding institution.
"""

import json
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://threedscans.com/"
METADATA_FILE = Path("metadata.json")
CACHE_FILE = Path("cache.json")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; threedscans-downloader/1.0)"}
DELAY = 1.0

# Item pages render each metadata row as a `div.singleSection` holding
# "Label: value" — these are the labels actually used.
FIELDS = ("artist", "period", "material", "location", "scanned", "scanner")


def get_soup(url):
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    time.sleep(DELAY)
    return BeautifulSoup(resp.text, "html.parser")


def get_item_urls():
    urls = []
    page = 1
    while True:
        url = BASE_URL if page == 1 else f"{BASE_URL}page/{page}/"
        soup = get_soup(url)
        if soup is None:
            break
        anchors = soup.select("article.post a[href][rel='bookmark']")
        if not anchors:
            break
        for a in anchors:
            if a["href"] not in urls:
                urls.append(a["href"])
        page += 1
    return urls


def load_local_names():
    """URL -> local filename, so `files` names what is actually on disk.

    Two URLs can share a basename (see local_name in scrape.py), so the
    basename alone is not a reliable local identifier.
    """
    if not CACHE_FILE.exists():
        return {}
    data = json.loads(CACHE_FILE.read_text())
    return data if isinstance(data, dict) else {}


def parse_item(url, local_names=None):
    """Pull title, download links, and whatever labelled metadata the page has."""
    soup = get_soup(url)
    if soup is None:
        return None

    title = soup.select_one("h2.entry-title")
    entry = {
        "url": url,
        "title": title.get_text().strip() if title else None,
        "downloads": [],
        "files": [],
        "meta": {},
    }

    local_names = local_names or {}
    for a in soup.find_all("a", href=True):
        if a.get_text().strip() == "Download Scan":
            href = a["href"]
            entry["downloads"].append(href)
            entry["files"].append(
                local_names.get(href, unquote(urlparse(href).path.split("/")[-1]))
            )

    for div in soup.select("div.singleSection"):
        text = div.get_text(" ", strip=True)
        label, sep, value = text.partition(":")
        if not sep:
            continue
        key = label.strip().lower()
        value = value.strip()
        if value and key in FIELDS:
            entry["meta"][key] = value

    return entry


def main():
    print("Crawling index pages...")
    item_urls = get_item_urls()
    print(f"Found {len(item_urls)} item pages\n")

    local_names = load_local_names()
    records = []
    for i, url in enumerate(item_urls, 1):
        print(f"[{i}/{len(item_urls)}] {url}")
        try:
            entry = parse_item(url, local_names)
            if entry:
                records.append(entry)
        except requests.RequestException as e:
            print(f"    [error] {e}")

    METADATA_FILE.write_text(json.dumps(records, indent=2, ensure_ascii=False))
    print(f"\nWrote {len(records)} records to {METADATA_FILE}")


if __name__ == "__main__":
    main()
