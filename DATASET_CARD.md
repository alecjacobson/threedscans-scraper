---
pretty_name: Three D Scans
license: other
license_name: no-restrictions-stated-by-author
license_link: LICENSE
task_categories:
  - image-to-3d
tags:
  - 3d
  - mesh
  - geometry-processing
  - cultural-heritage
  - sculpture
  - photogrammetry
size_categories:
  - n<1K
---

# Three D Scans

A mirror of [threedscans.com](https://threedscans.com/), the archive of high-resolution
3D scans of museum objects initiated in 2012 by artist **Oliver Laric**.

133 archives (5.4 GB) covering antiquities, classical and 19th-century sculpture,
anatomical casts, and natural-history specimens, scanned in collaboration with museums
across Europe.

This mirror exists so the collection can be fetched programmatically and cited stably.
**All credit for the scans belongs to Oliver Laric and the holding institutions.**

## Contents

| | |
| --- | --- |
| Archives | 133 files, 5.4 GB |
| Formats | `.stl.zip`, `.OBJ.zip`, and 9 uncompressed `.stl` |
| Metadata | `metadata.json` — per-object title, period, material, holding institution, scan year, scan method, source URL |

Files are mirrored exactly as served by threedscans.com — no re-meshing, re-encoding, or
format conversion. Meshes are raw scan output: many are non-manifold or have boundary
edges, which is often the point if you are testing geometry-processing code.

## Usage

```python
from huggingface_hub import snapshot_download

path = snapshot_download(repo_id="alecjacobson/threedscans", repo_type="dataset")
```

Or a single object:

```python
from huggingface_hub import hf_hub_download

f = hf_hub_download("alecjacobson/threedscans", "Siren-1.stl.zip", repo_type="dataset")
```

`metadata.json` maps each source page to the files it provides:

```json
{
  "url": "https://threedscans.com/uncategorized/siren/",
  "title": "Siren",
  "files": ["Siren-1.stl.zip"],
  "meta": {
    "artist": "Unknown",
    "period": "4th century CE",
    "material": "Marble",
    "location": "National Archaeological Museum Athens",
    "scanned": "2025",
    "scanner": "Photogrammetry and digital sculpting"
  }
}
```

## Licensing and provenance

Read this before reusing the scans.

**threedscans.com itself publishes no license text.** As of July 2026 there is no
licensing or terms statement on the homepage, the [Info page](https://threedscans.com/info/),
or any item page.

The permission relied on here is Laric's own statement on his companion project
[Lincoln 3D Scans](https://www.lincoln3dscans.co.uk/info), run with The Collection in
Lincoln, which states that all models can be downloaded and used without copyright
restrictions. Press coverage of threedscans.com reports the same intent for the wider
archive: Laric asserts no copyright over the scans and intends them to circulate freely.

Two limits worth being precise about:

1. That explicit statement is published for the **Lincoln** project. It is strong evidence
   of intent for the whole archive, but threedscans.com carries no equivalent text of
   its own.
2. It is a **statement of no restrictions, not a formal license instrument.** This mirror
   therefore does not tag the data CC0 or PDDL — those are dedications only the rights
   holder can make, and Laric has not made one in those terms. Nothing here grants you
   rights beyond what Laric has stated.

The underlying objects are overwhelmingly public-domain works. Note that some
jurisdictions may recognise rights in a 3D scan of a public-domain work, and holding
institutions may impose their own conditions on commercial reuse.

**If you reuse a scan, credit the project and the holding institution:**

> Scan by Oliver Laric, threedscans.com. Object: *Siren*, 4th century CE, marble,
> National Archaeological Museum Athens.

`metadata.json` carries the institution for every object so this can be done per-file.

### Holding institutions

Albertina, Kunsthistorisches Museum and Theater Museum (Vienna); Musée Guimet, Musée des
Monuments français, the Louvre, Dépôt des sculptures de la Ville de Paris, Musée
Carnavalet (Paris); Museum Romanité (Nîmes); Parco Archeologico di Pompei; The Collection
and Usher Gallery (Lincoln); Museo Archeologico Nazionale di Firenze; KODE Artmuseums
(Bergen); National Archaeological Museum Athens; among others.

The project has been supported by Lafayette Anticipation, Secession Vienna, The
Contemporary Art Society London, and Entrée Bergen.

## Takedown

This is an unofficial mirror. If you are Oliver Laric or a holding institution and want
material removed or the terms restated, open a discussion on this dataset and it will be
taken down promptly.

## Source code

Scraper and metadata harvester:
[github.com/alecjacobson/threedscans-scraper](https://github.com/alecjacobson/threedscans-scraper)
