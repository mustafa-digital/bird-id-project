# backend/utils/extract_bird_images.py

import json
import time
from pathlib import Path

import requests
from wikipediaapi import Wikipedia

from backend.core.config import SPECIES_MAP_PATHS
from backend.utils.json_utils import load_json

IMAGE_PATH = "frontend/src/assets/birds"
USER_AGENT = "Bird-Id-Project/0.1 (mustafa.atoof@gmail.com)"

DATA_PATH = Path("bird_image_urls.json")


def load_existing(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_snapshot(data: dict, path: Path):
    tmp = path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    tmp.replace(path)  # atomic on most filesystems


def get_wikipedia_main_image(page):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": page.title,
        "prop": "pageimages",
        "piprop": "original|thumbnail",
        "pithumbsize": 640,
        "format": "json",
    }
    headers = {"User-Agent": USER_AGENT}

    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    pages = data["query"]["pages"]
    page_data = next(iter(pages.values()))

    return {
        "filename": page_data.get("pageimage"),
        "thumbnail_url": page_data.get("thumbnail", {}).get("source"),
        "original_url": page_data.get("original", {}).get("source"),
    }


wiki = Wikipedia(
    user_agent=USER_AGENT,
    language="en",
)

species_dict = load_json(SPECIES_MAP_PATHS["species_ebird_map"])
image_urls = load_existing(DATA_PATH)

max_retries = 3
base_backoff = 2.0  # seconds

for bird in species_dict:
    # Skip if we already have a URL for this bird
    if image_urls.get(bird):
        print(f"Already have image for {bird}, skipping.")
        continue

    page = wiki.page(bird)
    if not page.exists():
        print(f"Could not directly find page of {bird}, using search instead...")
        search_result = next(iter(wiki.search(bird, limit=1).pages.values()), None)
        if search_result is None:
            print(f"Skipping: {bird} Wikipedia page not found (search failed).")
            image_urls[bird] = None
            save_snapshot(image_urls, DATA_PATH)
            continue
        page = search_result
        print(f"Found page {page.title} using search with url: {page.fullurl}")

    if not page.exists():
        print(f"Skipping: {bird} Wikipedia page not found.")
        image_urls[bird] = None
        save_snapshot(image_urls, DATA_PATH)
        continue

    url = None
    for attempt in range(max_retries):
        try:
            main_img = get_wikipedia_main_image(page)
            url = main_img.get("original_url")
            if url:
                break
        except Exception as e:
            # Could be rate limit, network error, etc.
            if attempt == max_retries - 1:
                print(
                    f"Failed to fetch image for {bird} after {max_retries} attempts: {e}"
                )
                break
            backoff = base_backoff * (2**attempt)
            print(f"Error fetching {bird}, retrying in {backoff}s: {e}")
            time.sleep(backoff)

    image_urls[bird] = url
    save_snapshot(image_urls, DATA_PATH)

    # Small delay to be nice to the API
    time.sleep(0.5)

print(len([v for v in image_urls.values() if v]), "images found.")
