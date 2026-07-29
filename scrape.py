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


def load_cache() -> dict:
    """Cache maps download URL -> local filename.

    Older runs wrote a bare list of URLs; migrate those by recomputing the
    filename, which is what the list form implied anyway.
    """
    if not CACHE_FILE.exists():
        return {}
    data = json.loads(CACHE_FILE.read_text())
    if isinstance(data, list):
        return {url: urlparse(url).path.split("/")[-1] for url in data}
    return data


def save_cache(cache: dict):
    CACHE_FILE.write_text(json.dumps(dict(sorted(cache.items())), indent=2))


def local_name(url: str, cache: dict) -> str:
    """Local filename for a URL, disambiguated when two URLs share a basename.

    Distinct objects can share a filename — the Vatican Museums and Campi
    Flegrei Hermanubis scans are both served as Hermanubis.stl.zip. Falling back
    to the basename alone silently drops one, so a colliding URL is prefixed
    with its /YYYY/MM/ upload segment.
    """
    parts = urlparse(url).path.strip("/").split("/")
    name = parts[-1]

    claimant = next((u for u, n in cache.items() if n == name), None)
    if claimant is None or claimant == url:
        return name

    # wp-content/uploads/YYYY/MM/file — use the date segment as the qualifier.
    if len(parts) >= 3 and parts[-3].isdigit() and parts[-2].isdigit():
        return f"{parts[-3]}-{parts[-2]}_{name}"
    return f"{abs(hash(url)) % 10**6}_{name}"


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


def download_file(url: str, cache: dict):
    if url in cache:
        print(f"    [skip] {cache[url]}")
        return

    filename = local_name(url, cache)
    dest = DOWNLOAD_DIR / filename

    if dest.exists():
        print(f"    [skip] {filename} (file exists)")
        cache[url] = filename
        save_cache(cache)
        return

    print(f"    [download] {filename}")
    resp = requests.get(url, headers=HEADERS, timeout=60, stream=True)
    resp.raise_for_status()

    # Download to a .part file and rename only on success, so an interrupted
    # run leaves no truncated file that a later run would mistake for complete.
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    partial = dest.with_suffix(dest.suffix + ".part")
    try:
        with open(partial, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        # Guard against a connection that drops mid-body: requests raises for a
        # broken read, but a short body can also arrive without an exception.
        expected = resp.headers.get("Content-Length")
        if expected is not None and partial.stat().st_size != int(expected):
            raise OSError(
                f"{filename}: got {partial.stat().st_size} bytes, expected {expected}"
            )
        partial.rename(dest)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise

    cache[url] = filename
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
        except (requests.RequestException, OSError) as e:
            print(f"    [error] {e}")

    print(f"\nDone. {len(cache)} files in cache.")


if __name__ == "__main__":
    main()
