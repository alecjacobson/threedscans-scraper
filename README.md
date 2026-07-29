# threedscans-scraper

Scrapes and downloads the 3D scan archive at [threedscans.com](https://threedscans.com/) —
Oliver Laric's project, initiated in 2012, of museum-object scans released for free
circulation.

This repository contains **only the scraping code**. It does not redistribute any scan
data. See [Attribution and terms](#attribution-and-terms) below.

## What it does

Crawls the site index, follows each item page, and downloads the linked archive:

```
https://threedscans.com/
  → https://threedscans.com/uncategorized/siren/
    → https://threedscans.com/wp-content/uploads/2025/10/Siren-1.stl.zip
```

The site uses infinite scroll with no static "next" links, so `scrape.py` probes
`/page/N/` until it 404s. Download links are `<a>` tags whose text is "Download Scan";
the linked files are a mix of `.stl.zip`, `.OBJ.zip`, and a few bare `.stl`.

Downloaded URLs are recorded in `cache.json`, so re-running skips what's already fetched.
Downloads are written to a `.part` file and renamed on completion, so an interrupted run
does not leave a truncated file that a later run would treat as done.

## Usage

```bash
pip3 install requests beautifulsoup4

python3 scrape.py            # download all scans to downloads/
python3 harvest_metadata.py  # write metadata.json (per-object provenance)
```

`scrape.py` sleeps 1 second between requests. Please leave that in — the archive is run
by one person and is not a CDN.

## Files

| File | Purpose |
| --- | --- |
| `scrape.py` | Crawls the site and downloads every scan archive |
| `harvest_metadata.py` | Collects per-object title, institution, date, material, scan method |
| `test_stats.m` | MATLAB/[gptoolbox](https://github.com/alecjacobson/gptoolbox) pass reporting non-manifold and boundary-edge counts per mesh |

## Attribution and terms

Read this before redistributing anything you download.

**The archive publishes no license.** As of July 2026 there is no licensing, copyright,
or terms-of-use statement on the homepage, the [Info page](https://threedscans.com/info/),
or any item page. Press coverage reports that Laric claims no copyright over the scans and
intends them to circulate freely, but that is secondary reporting, not a license grant
from the source.

What this means in practice:

- **Crawling is permitted.** `robots.txt` disallows only `/wp-admin/`.
- **Downloading for your own use** is squarely within what the archive is for.
- **Republishing the scan files** is a separate act. The underlying objects are mostly
  public-domain antiquities and 19th-century sculpture, but several jurisdictions
  (notably in the EU) may recognise rights in a 3D scan of a public-domain work, and the
  holding institutions have their own terms. Absent an explicit grant, get written
  permission before mirroring the data.

If you use the scans, credit both the project and the holding institution for each
object. `metadata.json` carries the per-object institution so this can be done properly:

> Scan by Oliver Laric, [threedscans.com](https://threedscans.com/). Object: *Siren*,
> 4th century CE, marble, National Archaeological Museum Athens.

Objects in the archive come from the Albertina, Kunsthistorisches Museum and Theater
Museum (Vienna); Musée Guimet, Musée des Monuments français, the Louvre, Dépôt des
sculptures de la Ville de Paris and Musée Carnavalet (Paris); Museum Romanité (Nîmes);
Parco Archeologico di Pompei; The Collection and Usher Gallery (Lincoln); Museo
Archeologico Nazionale di Firenze; and KODE Artmuseums (Bergen), among others.

## License

The code in this repository is MIT licensed. **This does not extend to the scan data**,
which is not covered by any license the project has published.
