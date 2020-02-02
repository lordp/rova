from slugify import slugify
from werkzeug.routing import BaseConverter
from datetime import datetime, timedelta

from dateutil.utils import today
from dateutil.relativedelta import relativedelta


class SlugConverter(BaseConverter):
    def to_python(self, value):
        return slugify(value)


def parse_time(span):
    dates = (None, None)
    dt = datetime.today()

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

    if span:
        dates = dates + (span.replace("_", " ").title(), )
    else:
        dates = dates + ("All Time", )

    return dates
