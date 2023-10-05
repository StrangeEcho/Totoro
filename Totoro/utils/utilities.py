from datetime import timedelta

import humanize


def humanize_timedelta(td: timedelta, *, precise: bool = False):
    """Humanize a timedelta into human readable text"""
    if precise:
        return humanize.precisedelta(td)
    return humanize.naturaldelta(td)
