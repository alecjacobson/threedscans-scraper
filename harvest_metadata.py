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
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://threedscans.com/"
METADATA_FILE = Path("metadata.json")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; threedscans-downloader/1.0)"}
DELAY = 1.0

# Labels the item pages use for their metadata rows.
FIELDS = ("artist", "date", "material", "institution", "scan", "method")


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


def parse_item(url):
    """Pull title, download links, and whatever labelled metadata the page has."""
    soup = get_soup(url)
    if soup is None:
        return None

    title = soup.find("h1")
    entry = {
        "url": url,
        "title": title.get_text().strip() if title else None,
        "downloads": [],
        "files": [],
    }

    for a in soup.find_all("a", href=True):
        if a.get_text().strip() == "Download Scan":
            entry["downloads"].append(a["href"])
            entry["files"].append(urlparse(a["href"]).path.split("/")[-1])

    # Item pages render metadata as short "Label: value" lines rather than a
    # structured table, so scan the text block for the labels we know about.
    content = soup.select_one("article") or soup
    for line in content.get_text("\n").split("\n"):
        line = line.strip()
        if ":" not in line or len(line) > 200:
            continue
        label, _, value = line.partition(":")
        key = label.strip().lower()
        value = value.strip()
        if value and any(f in key for f in FIELDS):
            entry.setdefault("meta", {})[key] = value

    return entry


def main():
    print("Crawling index pages...")
    item_urls = get_item_urls()
    print(f"Found {len(item_urls)} item pages\n")

    records = []
    for i, url in enumerate(item_urls, 1):
        print(f"[{i}/{len(item_urls)}] {url}")
        try:
            entry = parse_item(url)
            if entry:
                records.append(entry)
        except requests.RequestException as e:
            print(f"    [error] {e}")

    METADATA_FILE.write_text(json.dumps(records, indent=2, ensure_ascii=False))
    print(f"\nWrote {len(records)} records to {METADATA_FILE}")


if __name__ == "__main__":
    main()
