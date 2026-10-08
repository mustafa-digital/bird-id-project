# backend/utils/json.py
import json
from pathlib import Path


def load_json(filepath: Path) -> dict:
    """Load a JSON file and return its contents as a Python object.
    Args:
        filepath (str): The path to the JSON file.
        Returns:
            dict: The contents of the JSON file as a Python dictionary.
    """
    if not filepath.is_file():
        raise FileNotFoundError(f"File not found: {filepath}")

    if not filepath.suffix.lower() == ".json":
        raise ValueError("File is not a json file.")

    try:
        with open(filepath, "r") as f:
            return json.load(f)

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in file {filepath}") from e
