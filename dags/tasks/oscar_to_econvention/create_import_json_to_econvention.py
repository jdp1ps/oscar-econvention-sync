import os
import re
import pathlib
from airflow.decorators import task
from utils.config import OSCAR_TO_ECONVENTION_OUTPUT_DIR
from utils.file_utils import create_in_fallback_dir


@task
def create_import_json_to_econvention(data: str, **context) -> str | None:
    """
    Create a JSON file in OSCAR_TO_ECONVENTION_OUTPUT_DIR/YYYY-MM-DD/
    with a unique name based on logical date
    It contains serialized data given by transform process
    then this created file will be used to import in ECONVENTION

    If OSCAR_TO_ECONVENTION_OUTPUT_DIR doesn't exist or can't be written,
    It tries to write in FALLBACK_OUTPUT_DIR to create json file

    Args:
        data: serialized data.

    Returns:
        Path to the generated JSON file.
    """
    if data != "[]":
        logical_date = context["logical_date"]
        safe_logical_date = re.sub(r"[: ]", "_", str(logical_date))

        output_filename = f"output_for_econvention_{safe_logical_date}.json"
        try:
            import_json_date_dir = str(
                os.path.join(
                    OSCAR_TO_ECONVENTION_OUTPUT_DIR, logical_date.date().isoformat()
                )
            )
            import_json_path = os.path.join(import_json_date_dir, output_filename)
            pathlib.Path(import_json_date_dir).mkdir(exist_ok=True)
            with open(import_json_path, "w", encoding="utf-8") as f:
                f.write(data)
            return str(import_json_path)

        except (PermissionError, FileNotFoundError):
            return create_in_fallback_dir(data, output_filename)

        except Exception as e:
            raise RuntimeError("Unhandled exception while writing file") from e

    return None
