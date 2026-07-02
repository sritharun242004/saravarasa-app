"""Maps a 7-day challenge's day_number (1-7) to real calendar dates,
anchored to the day the client logged their first-ever meal."""
from datetime import timedelta


def day_dates(start_at, days: int = 7) -> dict[int, str]:
    """Day N's calendar date = start date + (N-1) days — 1 through 7, back to back."""
    start = start_at.date()
    return {n: (start + timedelta(days=n - 1)).isoformat() for n in range(1, days + 1)}
