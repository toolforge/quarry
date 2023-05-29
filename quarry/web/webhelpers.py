from datetime import datetime
from flask import Blueprint

templatehelpers = Blueprint("templatehelpers", __name__)


def get_pretty_delay(diff, suffix="", default="just now"):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.

    From http://flask.pocoo.org/snippets/33/
    """

    periods = (
        (diff.days // 365, "year", "years"),
        (diff.days // 30, "month", "months"),
        (diff.days // 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds // 3600, "hour", "hours"),
        (diff.seconds // 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:
        if period:
            return "%d %s %s" % (
                period,
                singular if period == 1 else plural,
                suffix,
            )

    return default


@templatehelpers.add_app_template_filter
def timesince(dt, default="just now"):
    now = datetime.utcnow()
    diff = now - dt
    return get_pretty_delay(diff, suffix="ago", default=default)
