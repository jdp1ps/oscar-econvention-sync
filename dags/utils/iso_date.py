import re
from datetime import datetime
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


def ensure_start_before_end(
    start: str | None, end: str | None, start_name="start", end_name="end"
):
    """
    Convert start and end dates from ISO string to datetime and check that start <= end.
    Raises ValueError if the check fails.
    """
    if start and end:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        if end_dt < start_dt:
            raise ValueError(
                f"{end_name} ({end}) cannot be before {start_name} ({start})"
            )
    return start, end
