import os

from config import Config

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .util import SlugConverter

app = Flask(__name__)
app.config.from_object(Config)

app.url_map.converters['slug'] = SlugConverter

db = SQLAlchemy(app)
db.init_app(app)

from flaskr import models, routes


@app.template_filter()
def station_name(name):
    stations = {
        'breeze': 'The Breeze',
        'rock': 'The Rock',
        'sound': 'The Sound',
        'mai': 'Mai FM',
        'more': 'More FM',
        'george': 'George FM',
        'magic': 'Magic Music',
        'edge': 'The Edge'
    }

    return stations.get(name)


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

