import os
import pathlib
from utils.config import FALLBACK_OUTPUT_DIR


def create_in_fallback_dir(data: str, output_filename: str) -> str:
    """Write data to fallback output dir if the initial directory doesn't work."""
    fallback_path = os.path.join(FALLBACK_OUTPUT_DIR, output_filename)
    pathlib.Path(FALLBACK_OUTPUT_DIR).mkdir(mode=0o750,parents=True, exist_ok=True)
    with open(fallback_path, "w", encoding="utf-8") as f:
        f.write(data)
    return str(fallback_path)
