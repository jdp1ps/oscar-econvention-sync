import csv
import re
from enum import Enum
import unicodedata

from utils.config import (
    CONVENTION_TYPE_CSV_FILE_PATH,
    CONVENTION_SOUS_TYPE_CSV_FILE_PATH,
    TYPE_PARENT_COLUMN_NAME,
    TYPE_PARENT_VALUE,
    VALUE_COLUMN_NAME,
)


def normalize_enum_name(name: str) -> str:
    """
    Converts a string to an enum name.
    """
    # Convert accents (é -> e, ç -> c, etc.)
    name = unicodedata.normalize("NFD", name)
    name = name.encode("ascii", "ignore").decode("utf-8")

    # Uppercase + replace invalid chars by "_"
    name = re.sub(r"[^A-Z0-9_]", "_", name.upper())

    # Remove duplicate underscores
    name = re.sub(r"__+", "_", name).strip("_")
    return name


def csv_column_to_list(
    csv_path: str, value_column_index: int, use_header: bool = False
) -> list[str]:
    """
    Extract a list of strings from a specific column in a CSV file.

    Args:
        csv_path (str): Path to the CSV file.
        value_column_index (int): 0-based index of the column to extract.
        use_header (bool): Skip first row if True. Defaults to False.

    Returns:
        list[str]: List of non-empty strings from the column.
    """
    values = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=",")
        if use_header:
            next(reader, None)

        for row in reader:
            if len(row) <= value_column_index:
                continue
            value = row[value_column_index].strip()
            if value:
                values.append(value)
    return values


def extract_column_by_filter(
    csv_path: str,
    filter_column: str,
    filter_value: str,
    extract_column: str,
    delimiter: str = ",",
) -> list[str]:
    """
    Extract values from a specific CSV column where another column matches a filter.
    Header row is required.

    Args:
        csv_path: Path to the CSV file.
        filter_column: Name of the column to filter on.
        filter_value: Value to match in the filter column.
        extract_column: Name of the column whose values are returned.
        delimiter: CSV separator (default ",").

    Returns:
        List of strings from extract_column matching the filter.
    """
    results = []
    with open(
        csv_path, mode="r", encoding="utf-8"
    ) as f:  # utf-8-sig supprime le BOM
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            if row.get(filter_column) == filter_value:
                results.append(row.get(extract_column))
    return results


def create_str_enum_from_list(name: str, values: list[str]) -> Enum:
    """
    Create a string-based Enum dynamically.
    Members are normalized names, values are original strings.
    """
    normalized_dict = {normalize_enum_name(v): v for v in values}
    # Méthode type() + inheritance pour str + Enum
    return Enum(name, normalized_dict, type=str)


CONVENTION_TYPE_ENUM = create_str_enum_from_list(
    "ConventionTypeEnum", csv_column_to_list(CONVENTION_TYPE_CSV_FILE_PATH, 0, True)
)


CONVENTION_SOUS_TYPE_ENUM = create_str_enum_from_list(
    "ConventionSousTypeEnum",
    extract_column_by_filter(
        CONVENTION_SOUS_TYPE_CSV_FILE_PATH,
        filter_column=TYPE_PARENT_COLUMN_NAME,
        filter_value=TYPE_PARENT_VALUE,
        extract_column=VALUE_COLUMN_NAME,
    ),
)
