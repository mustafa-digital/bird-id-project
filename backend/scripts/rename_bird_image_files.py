# backend/utils/rename_bird_images_files.py

import json
import re
from pathlib import Path

from backend.core.config import SPECIES_MAP_PATHS

# Adjust these paths
IMAGE_DIR = Path("frontend/src/assets/birds")
SPECIES_MAP_PATH = Path(
    SPECIES_MAP_PATHS["species_ebird_map"]
)  # {"species_name": "ebird_code"}

# Load mapping
with SPECIES_MAP_PATH.open("r", encoding="utf-8") as f:
    name_to_code = json.load(f)


# Build a normalized lookup: normalized_name -> ebird_code
def normalize_name(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = s.strip("_")
    return s


norm_map = {normalize_name(name): code for name, code in name_to_code.items()}


def main():
    if not IMAGE_DIR.exists():
        print(f"Image directory not found: {IMAGE_DIR}")
        return

    renamed = 0
    skipped = 0
    not_found = 0

    for path in sorted(IMAGE_DIR.iterdir()):
        if not path.is_file():
            continue

        stem = path.stem  # e.g. "eurasian teal"
        suffix = path.suffix  # e.g. ".jpg"

        norm_stem = normalize_name(stem)

        if norm_stem not in norm_map:
            print(f"Skip (no mapping): {path.name}")
            not_found += 1
            continue

        code = norm_map[norm_stem]
        new_name = f"{code}{suffix}"
        new_path = path.with_name(new_name)

        if new_path.exists() and new_path != path:
            print(f"Skip (target exists): {path.name} -> {new_name}")
            skipped += 1
            continue

        print(f"Rename: {path.name} -> {new_name}")
        path.rename(new_path)
        renamed += 1

    print(
        f"\nDone. Renamed: {renamed}, Skipped (exists): {skipped}, No mapping: {not_found}"
    )


if __name__ == "__main__":
    main()
