from flaskr import app, db
from flaskr.models import Played
from flaskr.util import parse_time

from flask import render_template, request, url_for, Response

import math
import json
import re
from datetime import datetime


def find_start_date():
    start_date = db.session.query(Played.played_time).order_by(Played.played_time)[0]
    return (start_date[0], datetime.now().replace(microsecond=0))


@app.route("/")
def index():
    stats = db.session.query(Played.artist, Played.artist_slug, db.func.count(Played.artist)).\
        group_by(Played.artist).\
        order_by(db.func.count(Played.artist).desc())

    recent_songs = db.session.query(Played.artist, Played.artist_slug, Played.name, Played.song_slug, Played.station, Played.played_time).\
        order_by(Played.played_time.desc())[:15]

    t = request.args.get('t')
    start_date, end_date, span = parse_time(t)
    if not start_date:
        start_date, end_date = find_start_date()

    stats = stats.filter(Played.played_time >= start_date, Played.played_time < end_date)

    page = request.args.get('page', 1, type=int)
    stats = stats.paginate(page, 15, False)

    next_url = url_for('index', page=stats.next_num, t=t) if stats.has_next else None
    prev_url = url_for('index', page=stats.prev_num, t=t) if stats.has_prev else None

    return render_template(
        'stats/index.html',
        stats=stats.items,
        recent_songs=recent_songs,
        span=span,
        next_url=next_url,
        prev_url=prev_url
    )


@app.route("/artist/<slug:name>")
def artist(name):
    artist = db.session.query(Played.artist).filter(Played.artist_slug == name).first()

    song_stats = db.session.query(Played.name, db.func.count(Played.name)).\
        filter(Played.artist_slug == name).\
        group_by(Played.name).\
        order_by(db.func.count(Played.name).desc())

    station_stats = db.session.query(Played.station, db.func.count(Played.station)).\
        filter(Played.artist_slug == name).\
        group_by(Played.station).\
        order_by(db.func.count(Played.station).desc())

    hourly_plays = db.session.query(db.func.strftime("%H", Played.played_time).label("hour"), db.func.count()).\
        filter(Played.artist_slug == name).\
        group_by("hour")

    daily_plays = db.session.query(db.func.strftime("%w", Played.played_time).label("day"), db.func.count()).\
        filter(Played.artist_slug == name).\
        group_by("day")

    start_date, end_date, span = parse_time(request.args.get('t'))
    if not start_date:
        start_date, end_date = find_start_date()

    song_stats = song_stats.filter(Played.played_time >= start_date, Played.played_time < end_date)
    station_stats = station_stats.filter(Played.played_time >= start_date, Played.played_time < end_date)
    hourly_plays = hourly_plays.filter(Played.played_time >= start_date, Played.played_time < end_date)

    page = request.args.get('page', 1, type=int)
    song_stats = song_stats.paginate(page, 15, False)

    next_url = url_for('artist', name=name, page=song_stats.next_num) if song_stats.has_next else None
    prev_url = url_for('artist', name=name, page=song_stats.prev_num) if song_stats.has_prev else None

    return render_template(
        'stats/artist.html',
        song_stats=song_stats.items,
        station_stats=station_stats,
        artist=artist[0],
        span=span,
        hourly_plays=hourly_plays,
        daily_plays=daily_plays,
        next_url=next_url,
        prev_url=prev_url
    )


@app.route("/station/<slug:name>")
def station(name):
    stats = db.session.query(Played.artist, Played.artist_slug, Played.name, db.func.count(Played.artist)).\
        filter(Played.station == name).\
        group_by(Played.artist, Played.name).\
        order_by(db.func.count(Played.artist).desc())

    total_plays = db.session.query(db.func.count()).filter(Played.station == name)

    hourly_plays = db.session.query(db.func.strftime("%H", Played.played_time).label("hour"), db.func.count()).\
        filter(Played.station == name).\
        group_by("hour")

    daily_plays = db.session.query(db.func.strftime("%w", Played.played_time).label("day"), db.func.count()).\
        filter(Played.station == name).\
        group_by("day")

    average_songs_per_day = db.session.query(db.func.strftime("%Y-%m-%d", Played.played_time).label("day"), db.func.count()).\
        filter(Played.station == name).\
        group_by("day")

    total_song_length = db.session.query(db.func.sum(Played.length).label("total_length")).\
        filter(Played.station == name)

    t = request.args.get('t')
    start_date, end_date, span = parse_time(t)
    if not start_date:
        start_date, end_date = find_start_date()

    stats = stats.filter(Played.played_time >= start_date, Played.played_time < end_date)
    total_plays = total_plays.filter(Played.played_time >= start_date, Played.played_time < end_date)
    hourly_plays = hourly_plays.filter(Played.played_time >= start_date, Played.played_time < end_date)
    daily_plays = daily_plays.filter(Played.played_time >= start_date, Played.played_time < end_date)
    average_songs_per_day = average_songs_per_day.filter(Played.played_time >= start_date, Played.played_time < end_date)

    total_song_length = total_song_length.filter(Played.played_time >= start_date, Played.played_time < end_date)
    songs_length = total_song_length.first()[0]
    total_seconds = end_date.timestamp() - start_date.timestamp()
    song_percent = round(((songs_length / total_seconds) * 100), 2)

    songs_played = 0

    songs_max = 0
    songs_max_day = None

    songs_min = 99999
    songs_min_day = None

    day_count = 0
    for day in average_songs_per_day:
        day_count += 1
        songs_played += day[1]

        if day[1] > songs_max:
            songs_max = day[1]
            songs_max_day = day[0]

        if day[1] < songs_min:
            songs_min = day[1]
            songs_min_day = day[0]

    songs_average = math.floor(songs_played / day_count)

    page = request.args.get('page', 1, type=int)
    stats = stats.paginate(page, 15, False)

    next_url = url_for('station', name=name, page=stats.next_num, t=t) if stats.has_next else None
    prev_url = url_for('station', name=name, page=stats.prev_num, t=t) if stats.has_prev else None

    return render_template(
        'stats/station.html',
        stats=stats.items,
        station=name,
        span=span,
        next_url=next_url,
        prev_url=prev_url,
        hourly_plays=hourly_plays,
        daily_plays=daily_plays,
        song_stats={
            "average": songs_average,
            "max": songs_max,
            "max_day": songs_max_day,
            "min": songs_min,
            "min_day": songs_min_day,
            "song_percent": song_percent,
            "total": total_plays.first()[0]
        }
    )


@app.route('/search', methods=['GET'])
def autocomplete():
    search_term = request.args.get('term')
    search_type = request.args.get('type')

    songs = {
        "results": [],
        "pagination": {
            "more": False
        }
    }

    search_term = re.sub('[^0-9A-Za-z ]+', '', search_term)
    if search_type == 'artist':
        result = db.session.query(Played.artist).filter(Played.artist.like(f"%{search_term}%")).distinct().limit(10)
    else:
        result = db.session.query(Played.name, Played.artist).filter(Played.name.like(f"%{search_term}%")).distinct().limit(10)

    for idx, entry in enumerate(result):
        if search_type == 'artist':
            text = f"{entry[0]}"
        else:
            text = f"{entry[0]} ({entry[1]})"

        songs["results"].append({ "id": idx, "text": text })

    return Response(json.dumps(songs), mimetype='application/json')


@app.route("/song/<slug:name>")
def song(name):
    song = db.session.query(Played.name).filter(Played.song_slug == name).first()
    artists = db.session.query(Played.artist, Played.artist_slug).filter(Played.song_slug == name).distinct()

    station_stats = db.session.query(Played.station, db.func.count(Played.station)).\
        filter(Played.song_slug == name).\
        group_by(Played.station).\
        order_by(db.func.count(Played.station).desc())

    hourly_plays = db.session.query(db.func.strftime("%H", Played.played_time).label("hour"), db.func.count()).\
        filter(Played.song_slug == name).\
        group_by("hour")

    daily_plays = db.session.query(db.func.strftime("%w", Played.played_time).label("day"), db.func.count()).\
        filter(Played.song_slug == name).\
        group_by("day")

    start_date, end_date, span = parse_time(request.args.get('t'))
    if not start_date:
        start_date, end_date = find_start_date()

    station_stats = station_stats.filter(Played.played_time >= start_date, Played.played_time < end_date)
    hourly_plays = hourly_plays.filter(Played.played_time >= start_date, Played.played_time < end_date)
    daily_plays = daily_plays.filter(Played.played_time >= start_date, Played.played_time < end_date)

    return render_template(
        'stats/song.html',
        song=song[0],
        artists=artists,
        station_stats=station_stats,
        span=span,
        hourly_plays=hourly_plays,
        daily_plays=daily_plays
    )
