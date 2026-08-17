from typing import Any


def month_index(value: dict[str, Any]) -> int:
    """Return the absolute month number for a {year, month} value."""
    return int(value["year"]) * 12 + int(value["month"]) - 1


def month_date(value: dict[str, Any]) -> str:
    """Return the first day of a {year, month} value as YYYY-MM-DD."""
    return f"{int(value['year']):04d}-{int(value['month']):02d}-01"
