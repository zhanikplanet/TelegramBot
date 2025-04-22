from datetime import datetime

def format_ts(ts: datetime, fmt: str = "%Y-%m-%d %H:%M") -> str:
    return ts.strftime(fmt)