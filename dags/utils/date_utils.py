import re
from dateutil import parser
from dateutil.parser import ParserError

ACTIVITY_DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"

CONVENTION_DATE_PATTERN = r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}$"
CONVENTION_DATE_FORMAT = "%d/%m/%Y %H:%M"


def to_iso_date(raw_date: str) -> str | None:
    """
    Ensure that the field has format YYYY-MM-DD.
    If not, try to parse it and convert to ISO date.
    """
    if raw_date is None or re.fullmatch(ACTIVITY_DATE_PATTERN, raw_date):
        return raw_date
    try:
        return parser.parse(raw_date).date().isoformat()
    except ParserError as e:
        raise ValueError(f"Invalid date format: {raw_date}") from e


def to_convention_date_format(raw_date: str) -> str | None:
    """
    Ensure that the field has format DD/MM/YYYY hh:mm.
    If not, try to parse it and convert to this format.
    """
    if raw_date is None or re.fullmatch(CONVENTION_DATE_PATTERN, raw_date):
        return raw_date
    try:
        return parser.parse(raw_date).strftime(CONVENTION_DATE_FORMAT)
    except ParserError as e:
        raise ValueError(f"Invalid date format: {raw_date}") from e


def ensure_start_before_end(
    start: str | None, end: str | None, start_name="start", end_name="end"
):
    """
    Parses start and end date strings of various formats and checks that start <= end.
    Raises ValueError if the date format is invalid or if the check fails.
    """
    if start and end:
        try:
            start_dt = parser.parse(start)
            end_dt = parser.parse(end)
        except ParserError as e:
            raise ValueError(f"Invalid date format: {start} & {end}") from e

        if end_dt < start_dt:
            raise ValueError(
                f"{end_name} ({end}) cannot be before {start_name} ({start})"
            )
    return start, end
