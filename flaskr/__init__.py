import os

from config import Config

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .util import SlugConverter, stations, format_time, page_not_found, tz

from jinja2 import Markup

app = Flask(__name__)
app.config.from_object(Config)

app.url_map.converters['slug'] = SlugConverter
app.register_error_handler(404, page_not_found)

db = SQLAlchemy(app)
db.init_app(app)

migrate = Migrate(app, db)

from flaskr import models, routes
from datetime import timedelta, datetime
import pytz


@app.template_filter()
def station_name(name):
    return stations().get(name, name)


@app.template_filter()
def weekday(dow):
    days = {
        '0': 'Sunday',
        '1': 'Monday',
        '2': 'Tuesday',
        '3': 'Wednesday',
        '4': 'Thursday',
        '5': 'Friday',
        '6': 'Saturday',
    }

    return days.get(dow)


@app.template_filter()
def delta(value):
    diff = datetime.now().astimezone(tz()) - tz().localize(value)
    return f"{format_time(diff.total_seconds())} ago"


@app.template_filter()
def extract_labels(array):
    tmp = []
    for label, _ in array:
        try:
            tmp.append(str(int(label)))
        except ValueError:
            tmp.append(label)

    return ",".join(tmp)


@app.template_filter()
def extract_values(array):
    return ",".join([str(int(value)) for _, value in array])


@app.template_filter()
def change_colour(change):
    if change is None:
        change = "new"
        change_class = "chart-new-entry"
    elif change == 0:
        change = "="
        change_class = "chart-no-change"
    elif change < 0:
        change_class = "chart-neg-change"
    elif change > 0:
        change = f"+{change}"
        change_class = "chart-pos-change"

    return Markup(f"<span class=\"{change_class}\">{change}</span>")