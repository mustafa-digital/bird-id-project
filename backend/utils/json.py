# backend/utils/json.py
import json
import os

def load_json(filepath :str) -> dict:
  """Load a JSON file and return its contents as a Python object.
  Args:
      filepath (str): The path to the JSON file.
      Returns:
          dict: The contents of the JSON file as a Python dictionary.
    """
  if not os.path.isfile(filepath):
    raise FileNotFoundError(f"File not found: {filepath}")

  if not filepath.lower().endswith(".json"):
    raise ValueError("File is not a json file.")

  try:
    with open(filepath, "r") as f:
      return json.load(f)

  except json.JSONDecodeError as e:
    raise ValueError(f"Invalid JSON in file {filepath}") from e