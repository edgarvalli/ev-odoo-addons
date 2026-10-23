from datetime import datetime


def parse_iso_date(date: str):
    return datetime.fromisoformat(date.replace("Z", "+00:00"))
