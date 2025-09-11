import os
import re
from airflow.decorators import task
from utils.config import ECONVENTION_TO_OSCAR_OUTPUT_DIR
from utils.file_utils import create_in_fallback_dir


@task
def create_import_json_to_oscar(data: str, **context) -> dict[str]:
    """
    Create a JSON file in ECONVENTION_TO_OSCAR_OUTPUT_DIR
    with a unique name based on logical date
    It contains serialized data given by transform process
    then this created file will be used to import in OSCAR

    If ECONVENTION_TO_OSCAR_OUTPUT_DIR doesn't exist or can't be written,
    It tries to write in FALLBACK_OUTPUT_DIR to create json file

    Args:
        data: serialized data.

    Returns:
        Path to the generated JSON file.
    """
    logical_date = str(context["logical_date"])
    safe_logical_date = re.sub(r"[: ]", "_", logical_date)

    output_filename = f"output_for_oscar_{safe_logical_date}.json"
    try:
        import_json_path = os.path.join(
            ECONVENTION_TO_OSCAR_OUTPUT_DIR, output_filename
        )
        with open(import_json_path, "w", encoding="utf-8") as f:
            f.write(data)
        return {"local_path": import_json_path, "filename": output_filename}

    except (PermissionError, FileNotFoundError):
        return {
            "local_path": create_in_fallback_dir(data, output_filename),
            "filename": output_filename,
        }

    except Exception as e:
        raise RuntimeError("Unhandled exception while writing file") from e
