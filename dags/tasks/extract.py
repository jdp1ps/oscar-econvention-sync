import os
import json
from airflow.decorators import task


@task
def extract_from_econvention(input_path: str) -> list[dict]:
    """
    Loads data from a JSON file located at the given path.

    Args:
        input_path: The absolute path to the input JSON file.

    Returns:
        A list of dictionaries loaded from the JSON file.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"The file {input_path} was not found.")

    with open(input_path, "r", encoding="utf-8") as f:
        return json.load(f)
