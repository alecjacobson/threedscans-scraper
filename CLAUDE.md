# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A scraper that downloads all `.stl.zip` 3D model files from https://threedscans.com/.

**Crawl path:** Homepage → category/item pages → `.stl.zip` download links

**Example:**
- `https://threedscans.com/` links to `https://threedscans.com/uncategorized/siren/`
- which links to `https://threedscans.com/wp-content/uploads/2025/10/Siren-1.stl.zip`

**Key requirements:**
- Download all `.stl.zip` files found by crawling the site
- Save files to a local directory
- Cache which files have been downloaded so re-running the script skips already-downloaded files (resume support)

## Running

```bash
pip3 install requests beautifulsoup4
python3 scrape.py
```

Downloaded files go to `downloads/`. Progress is cached in `cache.json` (list of downloaded URLs) — re-running skips already-downloaded files.

## Attribution constraints

The archive publishes no license (checked July 2026: homepage, /info/, item pages all
silent). Do not add code or docs that redistribute scan data or assert a license over it.
Per-object credit comes from `metadata.json`. See README "Attribution and terms".

## Implementation Notes

- `scrape.py` — single-file scraper
- `harvest_metadata.py` — collects per-object provenance into `metadata.json`
- Index pages: fetched via `/page/N/` until 404 (site uses infinite scroll, no static "next" links)
- Item URLs: `article.post a[href][rel='bookmark']` selector on each index page
- Download links: `<a>` tags with text "Download Scan" on item pages (files can be `.stl.zip`, `.OBJ.zip`, etc.)
- 1-second delay between requests to be polite to the server
