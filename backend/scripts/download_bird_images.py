# backend/utils/download_bird_images.py

import hashlib
import mimetypes
import time
from pathlib import Path

import requests

IMAGE_URLS_PATH = Path("backend\\utils\\bird_image_urls.json")
OUTPUT_DIR = Path("frontend/src/assets/birds")
USER_AGENT = "Bird-Id-Project/0.1 (mustafa.atoof@gmail.com)"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": USER_AGENT}
TIMEOUT = 15
MAX_RETRIES = 3
BASE_BACKOFF = 2.0  # seconds


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return __import__("json").load(f)


def save_snapshot(data: dict, path: Path):
    tmp = path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        __import__("json").dump(data, f, indent=4, ensure_ascii=False)
    tmp.replace(path)


def sanitize_filename(name: str) -> str:
    # Simple sanitization: keep alnum, spaces, dashes, underscores
    safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in name)
    # Collapse multiple spaces/underscores
    while "  " in safe:
        safe = safe.replace("  ", " ")
    while "__" in safe:
        safe = safe.replace("__", "_")
    return safe.strip(" _-")


def guess_extension(url: str, content_type: str | None) -> str:
    # Prefer content-type, then URL extension, then default .jpg
    if content_type:
        ext = mimetypes.guess_extension(content_type.split(";")[0].strip())
        if ext:
            return ext.lstrip(".")

    # Fallback to URL extension
    parsed = url.split("?")[0]  # strip query params
    if "." in parsed:
        ext = parsed.rsplit(".", 1)[-1].lower()
        if ext in ("jpg", "jpeg", "png", "webp", "gif"):
            return ext

    return "jpg"


def download_image(url: str, dest_path: Path) -> bool:
    tmp_path = dest_path.with_suffix(dest_path.suffix + ".tmp")

    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(
                url,
                headers=HEADERS,
                timeout=TIMEOUT,
                stream=True,
            )
            resp.raise_for_status()

            content_type = resp.headers.get("Content-Type")
            ext = guess_extension(url, content_type)

            # If we guessed .jpg but response suggests something else, adjust filename
            if dest_path.suffix.lstrip(".") != ext:
                new_name = dest_path.with_suffix(f".{ext}")
                # Ensure we don't accidentally overwrite a different bird's file
                if new_name.exists() and new_name != dest_path:
                    # Add a short hash to make unique
                    h = hashlib.sha256(url.encode()).hexdigest()[:6]
                    new_name = dest_path.parent / f"{dest_path.stem}_{h}.{ext}"

                dest_path = new_name
                tmp_path = dest_path.with_suffix(dest_path.suffix + ".tmp")

            with tmp_path.open("wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)

            tmp_path.replace(dest_path)  # atomic
            return True

        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                print(f"Failed to download {url} after {MAX_RETRIES} attempts: {e}")
                return False
            backoff = BASE_BACKOFF * (2**attempt)
            print(f"Error downloading {url}, retrying in {backoff}s: {e}")
            time.sleep(backoff)

    return False


def main():
    image_urls = load_json(IMAGE_URLS_PATH)

    # Optional: track download status in a separate JSON for resume
    status_path = IMAGE_URLS_PATH.with_name("bird_images_download_status.json")
    status = load_json(status_path)  # {bird: {"url": ..., "file": ..., "ok": bool}}

    downloaded_count = 0
    skipped_count = 0
    failed_count = 0

    for bird, url in image_urls.items():
        if not url:
            print(f"No URL for {bird}, skipping.")
            status[bird] = {"url": None, "file": None, "ok": False}
            save_snapshot(status, status_path)
            continue

        # If already successfully downloaded, skip
        if status.get(bird, {}).get("ok") is True:
            existing_file = status[bird].get("file")
            if existing_file and Path(existing_file).exists():
                print(f"Already downloaded: {bird} -> {existing_file}")
                skipped_count += 1
                continue

        safe_name = sanitize_filename(bird)
        dest_path = OUTPUT_DIR / f"{safe_name}"

        print(f"Downloading: {bird} -> {dest_path}")
        ok = download_image(url, dest_path)

        status[bird] = {
            "url": url,
            "file": str(dest_path) if ok else None,
            "ok": ok,
        }
        save_snapshot(status, status_path)

        if ok:
            downloaded_count += 1
        else:
            failed_count += 1

        # Be nice to the server
        time.sleep(0.3)

    print(
        f"\nDone. Downloaded: {downloaded_count}, Skipped: {skipped_count}, Failed: {failed_count}"
    )


if __name__ == "__main__":
    main()
