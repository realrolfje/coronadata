import datetime
import os


def reference_datetime(daily=None):
    """Return a reproducible build time based on data, with an explicit override for releases."""
    override = os.environ.get("CORONADATA_BUILD_DATE")
    if override:
        return datetime.datetime.fromisoformat(override)
    if daily:
        return datetime.datetime.combine(
            datetime.date.fromisoformat(max(daily)), datetime.time(12, 0)
        )
    return datetime.datetime(1970, 1, 1, 12, 0)


def reference_date(daily=None):
    return reference_datetime(daily).date()
