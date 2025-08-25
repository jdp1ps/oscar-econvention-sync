import os
import re
from airflow.decorators import task
from utils.config import ECONVENTION_TO_OSCAR_OUTPUT_DIR


@task
def create_import_json_to_oscar(data: str, **context) -> list[dict]:
    """
    Create a JSON file in ECONVENTION_TO_OSCAR_OUTPUT_DIR
    with a unique name based on logical date
    It contains serialized data given by transform process
    then this created file will be used to import in OSCAR

    Args:
        data: serialized data.

    Returns:
        Path to the generated JSON file.
    """
    logical_date = str(context["logical_date"])
    safe_logical_date = re.sub(r"[: ]", "_", logical_date)

    output_filename = f"output_for_oscar_{safe_logical_date}.json"
    load_output_path = os.path.join(ECONVENTION_TO_OSCAR_OUTPUT_DIR, output_filename)

    with open(load_output_path, "w", encoding="utf-8") as f:
        f.write(data)
    return load_output_path
