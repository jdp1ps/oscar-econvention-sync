import os
import json
import pathlib
from airflow.decorators import task
from utils.config import OSCAR_TO_ECONVENTION_OUTPUT_DIR
from utils.type_utils import ensure_list_of_dict


@task
def update_json_for_econvention(data: str, **context) -> str | None:
    """
    Create or update a daily JSON file for eConvention import.
    The file is stored under OSCAR_TO_ECONVENTION_OUTPUT_DIR/YYYY-MM-DD.json
    and always contains a list of dictionaries.
    - If the file exists, new data is appended.
    - If not, a new file is created with the data.

    Args:
        data (str): JSON string representing a list of dicts.
        **context: Airflow context, must contain "logical_date".

    Returns:
        str | None: Path to the created/updated JSON file, or None if data is empty.
    """
    if data != "[]":
        data_to_add = ensure_list_of_dict(json.loads(data))
        logical_date = context["logical_date"]
        date_str = logical_date.date().isoformat()

        output_filename = f"{date_str}.json"
        import_json_dir = str(os.path.join(OSCAR_TO_ECONVENTION_OUTPUT_DIR, date_str))
        import_json_path = os.path.join(import_json_dir, output_filename)
        try:
            pathlib.Path(import_json_dir).mkdir(parents=True, exist_ok=True)
            if os.path.exists(import_json_path):
                with open(import_json_path, "r", encoding="utf-8") as f:
                    og_data = ensure_list_of_dict(json.load(f))
            else:
                og_data = []

        except Exception as e:
            raise RuntimeError("Unhandled exception while reading file") from e

        updated_data = og_data + data_to_add
        try:
            with open(import_json_path, "w", encoding="utf-8") as f:
                f.write(json.dumps(updated_data))
            return str(import_json_path)

        except Exception as e:
            raise RuntimeError("Unhandled exception while writing file") from e

    return None
