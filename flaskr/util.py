from slugify import slugify
from werkzeug.routing import BaseConverter
from datetime import datetime, timedelta
import math
from flask import render_template

from dateutil.utils import today
from dateutil.relativedelta import relativedelta
import pytz


class SlugConverter(BaseConverter):
    def to_python(self, value):
        return slugify(value)


def parse_time(span):
    dates = (None, None)
    dt = datetime.today()
    now = datetime.now().astimezone(tz())

    if span == "today":
        dates = (today(), today() + timedelta(days=1) - timedelta(seconds=1))

    if span == "yesterday":
        dates = (today() - timedelta(days=1), today() - timedelta(seconds=1))

    if span == "this_week":
        begin = today() - timedelta(days=dt.weekday())
        dates = (begin, begin + timedelta(days=7) - timedelta(seconds=1))

    if span == "last_week":
        begin = today() - timedelta(days=dt.weekday()) - timedelta(weeks=1)
        dates = (begin, begin + timedelta(days=7) - timedelta(seconds=1))

    if span == "this_month":
        begin = today().replace(day=1)
        dates = (begin, begin + relativedelta(months=1) - timedelta(seconds=1))

    if span == "last_month":
        begin = today().replace(day=1) - relativedelta(months=1)
        dates = (begin, begin + relativedelta(months=1) - timedelta(seconds=1))

    if span == "24hours":
        dates = (now - relativedelta(days=1), now)

    if span == "7days":
        dates = (now - relativedelta(days=7), now)

    if span == "30days":
        dates = (now - relativedelta(days=30), now)

    if span == "1year":
        dates = (now - relativedelta(years=1), now)

    if span:
        dates = dates + (span.replace("_", " ").title(),)
    else:
        dates = dates + ("All Time",)

    return dates


def stations():
    return {
        "rova": {
            "breeze": "The Breeze",
            "rock": "The Rock",
            "sound": "The Sound",
            "mai": "Mai FM",
            "more": "More FM",
            "george": "George FM",
            "magic": "Magic Music",
            "edge": "The Edge",
        },
        "iheart": {
            "zm": "ZM",
            "hauraki": "Radio Hauraki",
            "nztop40": "NZ Top 40",
            "flava": "Flava",
            "coast": "Coast",
            "thehits": "The Hits",
            "lifefm": "Life FM",
            "southernstar": "Southern Star",
            "rhema": "Radio Rhema",
            "kick": "Kick",
        },
    }


def format_time(seconds):
    minute, second = divmod(math.floor(seconds), 60)
    if minute > 60:
        hour, minute = divmod(minute, 60)
        if hour > 24:
            day, hour = divmod(hour, 24)
            return "{d:0.0f} days {h:0.0f} hours".format(d=day, h=hour)
        else:
            return "{h:0.0f} hours {m:02.0f} mins".format(h=hour, m=minute)
    elif minute > 0:
        return "{m:0.0f} mins {s} secs".format(m=minute, s=second)
    else:
        return "{s} secs".format(s=second)


def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template("404.html", error=e, station_list=stations()), 404


def tz():
    return pytz.timezone("Pacific/Auckland")
