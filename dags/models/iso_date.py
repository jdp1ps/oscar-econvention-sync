import re
from dateutil import parser

DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"


def to_iso_date(raw_date: str) -> str | None:
    """
    Ensure that the field has format YYYY-MM-DD.
    If not, try to parse it and convert to ISO date.
    """
    if raw_date is None or re.fullmatch(DATE_PATTERN, raw_date):
        return raw_date
    try:
        return parser.parse(raw_date).date().isoformat()
    except ValueError as e:
        raise ValueError(f"Invalid date format: {raw_date}") from e
