#!/usr/bin/env python3
"""
Uploads the scraped archives and metadata to the Hugging Face dataset repo.

Uses upload_large_folder, which chunks, resumes, and parallelises — the right tool
for ~5 GB of multi-hundred-MB archives. Safe to re-run: it skips what's already
uploaded.

    hf auth login          # once
    python3 upload_hf.py
"""

import sys
from pathlib import Path

from huggingface_hub import HfApi

REPO_ID = "alecjacobson/threedscans"
DOWNLOAD_DIR = Path("downloads")
METADATA = Path("metadata.json")
CARD = Path("DATASET_CARD.md")
TERMS = Path("DATA_TERMS.txt")


def main():
    if not DOWNLOAD_DIR.is_dir():
        sys.exit(f"{DOWNLOAD_DIR} not found — run scrape.py first")
    if not METADATA.exists():
        sys.exit(f"{METADATA} not found — run harvest_metadata.py first")

    api = HfApi()

    # Card and metadata first, so the repo is never briefly public with data
    # but no attribution or licensing note attached to it.
    print("Uploading dataset card and metadata...")
    api.upload_file(
        path_or_fileobj=str(CARD),
        path_in_repo="README.md",
        repo_id=REPO_ID,
        repo_type="dataset",
        commit_message="Add dataset card with provenance and attribution",
    )
    # HF requires the terms text in a LICENSE file when license: other is used.
    api.upload_file(
        path_or_fileobj=str(TERMS),
        path_in_repo="LICENSE",
        repo_id=REPO_ID,
        repo_type="dataset",
        commit_message="Add data terms",
    )
    api.upload_file(
        path_or_fileobj=str(METADATA),
        path_in_repo="metadata.json",
        repo_id=REPO_ID,
        repo_type="dataset",
        commit_message="Add per-object metadata",
    )

    files = sorted(p.name for p in DOWNLOAD_DIR.iterdir() if p.is_file())
    total = sum(p.stat().st_size for p in DOWNLOAD_DIR.iterdir() if p.is_file())
    print(f"\nUploading {len(files)} archives ({total / 1e9:.1f} GB)...")

    api.upload_large_folder(
        folder_path=str(DOWNLOAD_DIR),
        repo_id=REPO_ID,
        repo_type="dataset",
        allow_patterns=["*.zip", "*.stl", "*.STL", "*.obj", "*.OBJ"],
    )

    print(f"\nDone: https://huggingface.co/datasets/{REPO_ID}")


if __name__ == "__main__":
    main()
