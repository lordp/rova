from flaskr import app, db
from flaskr.models import Played, Artist, Song, Chart
from flaskr.util import parse_time, stations, tz

from flask import render_template, request, url_for, Response, abort, redirect

from sqlalchemy.sql.expression import desc, and_

import math
import json
import re
from datetime import datetime, timedelta
import string


def find_start_date():
    start_date = db.session.query(Played.played_time).order_by(Played.played_time)[0]
    return (start_date[0], datetime.now().replace(microsecond=0).astimezone(tz()))


@app.route("/")
def index():
    last_day_span = parse_time("24hours")
    last_week_span = parse_time("7days")
    last_month_span = parse_time("30days")

    recent_songs = (
        db.session.query(Played)
        .join(Song)
        .join(Artist, Artist.id == Played.artist_id)
        .order_by(Played.played_time.desc())
        .filter(
            and_(
                Played.played_time >= last_day_span[0],
                Played.played_time <= last_day_span[1],
            )
        )
        .limit(15)
        .distinct()
    )

    total_plays = db.session.query(Played).count()
    unique_songs = db.session.query(Song.name).distinct().count()
    unique_artists = db.session.query(Artist).distinct().count()

    last_day = (
        db.session.query(Played)
        .filter(
            Played.played_time >= last_day_span[0],
            Played.played_time < last_day_span[1],
        )
        .count()
    )
    last_week = (
        db.session.query(Played)
        .filter(
            Played.played_time >= last_week_span[0],
            Played.played_time < last_week_span[1],
        )
        .count()
    )
    last_month = (
        db.session.query(Played)
        .filter(
            Played.played_time >= last_month_span[0],
            Played.played_time < last_month_span[1],
        )
        .count()
    )

    hourly_plays_query = (
        db.session.query(
            db.func.date_part("HOUR", Played.played_time).label("hour"), db.func.count()
        )
        .filter(
            and_(
                Played.played_time >= last_day_span[0],
                Played.played_time <= last_day_span[1],
            )
        )
        .group_by("hour")
        .order_by("hour")
        .all()
    )
    hourly_plays = {hour: 0 for hour in range(24)}
    for entry in hourly_plays_query:
        hourly_plays[entry[0]] = entry[1]

    hourly_plays = [(hour, play) for hour, play in hourly_plays.items()]

    daily_plays = (
        db.session.query(
            db.func.to_char(Played.played_time, "YYYY-MM-DD").label("day"),
            db.func.count(),
        )
        .filter(
            Played.played_time
            >= last_month_span[0].replace(hour=0, minute=0, second=0, microsecond=0),
            Played.played_time < last_month_span[1],
        )
        .group_by("day")
        .order_by("day")
        .all()
    )

    stats = {
        "total_plays": f"{total_plays:,d}",
        "unique_songs": f"{unique_songs:,d}",
        "unique_artists": f"{unique_artists:,d}",
        "last_day": f"{last_day:,d}",
        "last_week": f"{last_week:,d}",
        "last_month": f"{last_month:,d}",
        "hourly_plays": hourly_plays,
        "daily_plays": daily_plays,
    }

    return render_template(
        "stats/index.html",
        stats=stats,
        recent_songs=recent_songs,
        station_list=stations(),
    )


@app.route("/artist/<slug:name>")
def artist(name):
    artist = db.session.query(Artist).filter(Artist.slug == name).first()
    if not artist:
        abort(404, "We're sorry, that artist cannot be found.")

    last_day_span = parse_time("24hours")
    last_week_span = parse_time("7days")
    last_month_span = parse_time("30days")

    recent_songs = (
        db.session.query(Played)
        .join(Song)
        .join(Artist, Artist.id == Played.artist_id)
        .filter(Played.artist_id == artist.id)
        .filter(
            and_(
                Played.played_time >= last_day_span[0],
                Played.played_time <= last_day_span[1],
            )
        )
        .order_by(Played.played_time.desc())
        .limit(15)
    )

    total_plays = (
        db.session.query(Played)
        .join(Artist)
        .filter(Played.artist_id == artist.id)
        .count()
    )
    unique_songs = (
        db.session.query(Song.name)
        .join(Played, Artist)
        .filter(Song.artist_id == artist.id)
        .distinct()
        .count()
    )

    last_day = (
        db.session.query(Played)
        .join(Artist)
        .filter(
            Played.artist_id == artist.id,
            Played.played_time >= last_day_span[0],
            Played.played_time < last_day_span[1],
        )
        .count()
    )
    last_week = (
        db.session.query(Played)
        .join(Artist)
        .filter(
            Played.artist_id == artist.id,
            Played.played_time >= last_week_span[0],
            Played.played_time < last_week_span[1],
        )
        .count()
    )
    last_month = (
        db.session.query(Played)
        .join(Artist)
        .filter(
            Played.artist_id == artist.id,
            Played.played_time >= last_month_span[0],
            Played.played_time < last_month_span[1],
        )
        .count()
    )

    hourly_plays_query = (
        db.session.query(
            db.func.date_part("HOUR", Played.played_time).label("hour"), db.func.count()
        )
        .join(Artist)
        .filter(Played.artist_id == artist.id)
        .group_by("hour")
        .order_by("hour")
    )
    hourly_plays = {hour: 0 for hour in range(24)}
    for entry in hourly_plays_query:
        hourly_plays[entry[0]] = entry[1]

    hourly_plays = [(hour, play) for hour, play in hourly_plays.items()]

    daily_plays = (
        db.session.query(
            db.func.to_char(Played.played_time, "YYYY-MM-DD").label("day"),
            db.func.count(),
        )
        .join(Artist)
        .filter(
            Played.artist_id == artist.id,
            Played.played_time
            >= last_month_span[0].replace(hour=0, minute=0, second=0, microsecond=0),
            Played.played_time < last_month_span[1],
        )
        .group_by("day")
        .order_by("day")
    )

    song_play_count = (
        db.session.query(Song, db.func.count(Song.slug).label("cnt"))
        .join(Played, Artist)
        .filter(Artist.id == artist.id)
        .group_by(Song.id)
        .order_by(desc("cnt"))
    )

    station_play_count = (
        db.session.query(Played.station, db.func.count(Song.slug).label("cnt"))
        .join(Song)
        .join(Artist, Artist.id == Played.artist_id)
        .filter(Artist.id == artist.id)
        .group_by(Played.station)
        .order_by(desc("cnt"))
    )

    stats = {
        "total_plays": f"{total_plays:,d}",
        "unique_songs": f"{unique_songs:,d}",
        "last_day": f"{last_day:,d}",
        "last_week": f"{last_week:,d}",
        "last_month": f"{last_month:,d}",
        "hourly_plays": hourly_plays,
        "daily_plays": daily_plays,
    }

    return render_template(
        "stats/artist.html",
        artist=artist,
        stats=stats,
        recent_songs=recent_songs,
        song_play_count=song_play_count,
        station_play_count=station_play_count,
        station_list=stations(),
    )


@app.route("/artists")
def artists():
    artists = (
        db.session.query(Artist, db.func.count(Song.id))
        .join(Song)
        .group_by(Artist.id)
        .order_by(Artist.slug.asc())
    )

    startswith = "ALL"
    if "startswith" in request.args:
        startswith = request.args.get("startswith", type=str)
        artists = artists.filter(Artist.slug.ilike(f"{startswith}%"))

    page = request.args.get("page", 1, type=int)
    artists = artists.paginate(page, per_page=15)

    if "startswith" in request.args:
        next_url = (
            url_for("artists", page=artists.next_num, startswith=startswith)
            if artists.has_next
            else None
        )
        prev_url = (
            url_for("artists", page=artists.prev_num, startswith=startswith)
            if artists.has_prev
            else None
        )
    else:
        next_url = (
            url_for("artists", page=artists.next_num) if artists.has_next else None
        )
        prev_url = (
            url_for("artists", page=artists.prev_num) if artists.has_prev else None
        )

    return render_template(
        "stats/artists.html",
        artists=artists.items,
        next_url=next_url,
        prev_url=prev_url,
        page=page,
        next_page=page + 1,
        prev_page=page - 1,
        alphabet=list(string.ascii_uppercase),
        startswith=startswith,
        station_list=stations(),
    )


@app.route("/songs")
def songs():
    songs = db.session.query(Song).distinct().order_by(Song.slug.asc())

    startswith = "ALL"
    if "startswith" in request.args:
        startswith = request.args.get("startswith", type=str)
        songs = songs.filter(Song.slug.ilike(f"{startswith}%"))

    page = request.args.get("page", 1, type=int)
    songs = songs.paginate(page, per_page=15)

    if "startswith" in request.args:
        next_url = (
            url_for("songs", page=songs.next_num, startswith=startswith)
            if songs.has_next
            else None
        )
        prev_url = (
            url_for("songs", page=songs.prev_num, startswith=startswith)
            if songs.has_prev
            else None
        )
    else:
        next_url = url_for("songs", page=songs.next_num) if songs.has_next else None
        prev_url = url_for("songs", page=songs.prev_num) if songs.has_prev else None

    return render_template(
        "stats/songs.html",
        songs=songs.items,
        next_url=next_url,
        prev_url=prev_url,
        page=page,
        next_page=page + 1,
        prev_page=page - 1,
        alphabet=list(string.ascii_uppercase),
        startswith=startswith,
        station_list=stations(),
    )


@app.route("/station/<slug:name>")
def station(name):
    station_list = stations()
    if name not in station_list["rova"] and name not in station_list["iheart"]:
        abort(404, "We're sorry, that station cannot be found.")

    last_day_span = parse_time("24hours")
    last_week_span = parse_time("7days")
    last_month_span = parse_time("30days")

    recent_songs = (
        db.session.query(Played)
        .join(Song)
        .join(Artist, Artist.id == Played.artist_id)
        .filter(Played.station == name)
        .filter(
            and_(
                Played.played_time >= last_day_span[0],
                Played.played_time <= last_day_span[1],
            )
        )
        .order_by(Played.played_time.desc())[:15]
    )

    total_plays = db.session.query(Played).filter(Played.station == name).count()
    unique_songs = (
        db.session.query(Song)
        .join(Played)
        .filter(Played.station == name)
        .distinct()
        .count()
    )
    unique_artists = (
        db.session.query(Artist)
        .join(Played)
        .filter(Played.station == name)
        .distinct()
        .count()
    )

    last_day = (
        db.session.query(Played)
        .filter(
            Played.played_time >= last_day_span[0],
            Played.played_time < last_day_span[1],
            Played.station == name,
        )
        .count()
    )
    last_week = (
        db.session.query(Played)
        .filter(
            Played.played_time >= last_week_span[0],
            Played.played_time < last_week_span[1],
            Played.station == name,
        )
        .count()
    )
    last_month = (
        db.session.query(Played)
        .filter(
            Played.played_time >= last_month_span[0],
            Played.played_time < last_month_span[1],
            Played.station == name,
        )
        .count()
    )

    hourly_plays_query = (
        db.session.query(
            db.func.date_part("HOUR", Played.played_time).label("hour"), db.func.count()
        )
        .filter(Played.station == name)
        .group_by("hour")
    )
    hourly_plays = {hour: 0 for hour in range(24)}
    for entry in hourly_plays_query:
        hourly_plays[entry[0]] = entry[1]

    hourly_plays = [(hour, play) for hour, play in hourly_plays.items()]

    daily_plays = (
        db.session.query(
            db.func.to_char(Played.played_time, "YYYY-MM-DD").label("day"),
            db.func.count(),
        )
        .filter(
            Played.played_time
            >= last_month_span[0].replace(hour=0, minute=0, second=0, microsecond=0),
            Played.played_time < last_month_span[1],
            Played.station == name,
        )
        .group_by("day")
        .order_by("day")
    )

    start_date, end_date = find_start_date()
    total_song_length = (
        db.session.query(db.func.sum(Song.length).label("total_length"))
        .join(Played)
        .filter(Played.station == name)
        .first()[0]
    )
    total_seconds = end_date.timestamp() - start_date.timestamp()
    song_percent = round(((total_song_length / total_seconds) * 100), 1)

    stats = {
        "total_plays": f"{total_plays:,d}",
        "unique_songs": f"{unique_songs:,d}",
        "unique_artists": f"{unique_artists:,d}",
        "last_day": f"{last_day:,d}",
        "last_week": f"{last_week:,d}",
        "last_month": f"{last_month:,d}",
        "hourly_plays": hourly_plays,
        "daily_plays": daily_plays,
        "music_ratio": {"music": song_percent, "other": 100 - song_percent},
    }

    return render_template(
        "stats/station.html",
        station=name,
        stats=stats,
        recent_songs=recent_songs,
        station_list=station_list,
    )


@app.route("/search", methods=["GET"])
def autocomplete():
    search_term = request.args.get("term")

    results = {
        "results": [
            {"text": "Artists", "children": []},
            {"text": "Songs", "children": []},
        ],
        "pagination": {"more": False},
    }

    search_term = re.sub("[^0-9A-Za-z ]+", "", search_term)
    artists = (
        db.session.query(Artist)
        .filter(Artist.name.ilike(f"%{search_term}%"))
        .distinct()
        .limit(10)
    )
    songs = (
        db.session.query(Song)
        .filter(Song.name.ilike(f"%{search_term}%"))
        .distinct()
        .limit(10)
    )

    for idx, entry in enumerate(artists):
        results["results"][0]["children"].append(
            {"id": idx, "text": entry.name, "slug": entry.slug, "type": "artist"}
        )

    for idx, entry in enumerate(songs):
        results["results"][1]["children"].append(
            {
                "id": idx,
                "text": f"{entry.name} ({entry.artist.name})",
                "slug": entry.slug,
                "type": "song",
            }
        )

    return Response(json.dumps(results), mimetype="application/json")


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.route("/song/<slug:name>")
@app.route("/song/<slug:name>/artist/<slug:artist>")
def song(name, artist=None):
    song = db.session.query(Song).filter(Song.slug == name).first()
    if not song:
        abort(404, "We're sorry, that song cannot be found.")

    if artist:
        artists = [db.session.query(Artist).filter(Artist.slug == artist).first()]
        artist = artists[0]
    else:
        artists = (
            db.session.query(Artist)
            .join(Song)
            .filter(Song.slug == name)
            .distinct()
            .all()
        )

    last_day_span = parse_time("24hours")
    last_week_span = parse_time("7days")
    last_month_span = parse_time("30days")
    last_year_span = parse_time("1year")

    recent_plays = (
        db.session.query(Played)
        .join(Song)
        .filter(Song.slug == name)
        .filter(
            and_(
                Played.played_time >= last_year_span[0],
                Played.played_time <= last_year_span[1],
            )
        )
        .order_by(Played.played_time.desc())
    )

    station_stats = (
        db.session.query(Played.station, db.func.count(Played.station).label("cnt"))
        .join(Song)
        .filter(Song.slug == name)
        .group_by(Played.station)
        .order_by(desc("cnt"))
    )

    total_plays = db.session.query(Played).join(Song).filter(Song.slug == name)

    last_day = (
        db.session.query(Played)
        .join(Song)
        .filter(
            Played.played_time >= last_day_span[0],
            Played.played_time < last_day_span[1],
            Song.slug == name,
        )
    )
    last_week = (
        db.session.query(Played)
        .join(Song)
        .filter(
            Played.played_time >= last_week_span[0],
            Played.played_time < last_week_span[1],
            Song.slug == name,
        )
    )
    last_month = (
        db.session.query(Played)
        .join(Song)
        .filter(
            Played.played_time >= last_month_span[0],
            Played.played_time < last_month_span[1],
            Song.slug == name,
        )
    )

    hourly_plays_query = (
        db.session.query(
            db.func.date_part("HOUR", Played.played_time).label("hour"), db.func.count()
        )
        .join(Song)
        .filter(Song.slug == name)
        .group_by("hour")
    )

    daily_plays = (
        db.session.query(
            db.func.to_char(Played.played_time, "YYYY-MM-DD").label("day"),
            db.func.count(),
        )
        .join(Song)
        .filter(
            Played.played_time >= last_month_span[0],
            Played.played_time < last_month_span[1],
            Song.slug == name,
        )
        .group_by("day")
        .order_by("day")
    )

    if artist:
        recent_plays = recent_plays.filter(Played.artist_id == artist.id)
        station_stats = station_stats.filter(Played.artist_id == artist.id)
        total_plays = total_plays.filter(Played.artist_id == artist.id)
        last_day = last_day.filter(Played.artist_id == artist.id)
        last_week = last_week.filter(Played.artist_id == artist.id)
        last_month = last_month.filter(Played.artist_id == artist.id)
        hourly_plays_query = hourly_plays_query.filter(Played.artist_id == artist.id)
        daily_plays = daily_plays.filter(Played.artist_id == artist.id)

    recent_plays = recent_plays.limit(15)
    total_plays = total_plays.count()
    last_day = last_day.count()
    last_week = last_week.count()
    last_month = last_month.count()

    hourly_plays = {hour: 0 for hour in range(24)}
    for entry in hourly_plays_query:
        hourly_plays[entry[0]] = entry[1]

    hourly_plays = [(hour, play) for hour, play in hourly_plays.items()]

    stats = {
        "total_plays": f"{total_plays:,d}",
        "last_day": f"{last_day:,d}",
        "last_week": f"{last_week:,d}",
        "last_month": f"{last_month:,d}",
        "hourly_plays": hourly_plays,
        "daily_plays": daily_plays,
    }

    return render_template(
        "stats/song.html",
        song=song,
        artists=artists,
        artists_length=len(artists),
        station_stats=station_stats,
        stats=stats,
        recent_plays=recent_plays,
        station_list=stations(),
    )


@app.route("/chart/")
@app.route("/chart/<int:year>/<int:month>/<int:day>")
@app.route("/chart/<int:year>/<int:month>/<int:day>/<slug:station>")
def chart(year=None, month=None, day=None, station=None):
    if not year:
        today = datetime.today()
        year = today.year
        month = today.month
        day = today.day

    date = datetime(year, month, day)
    if date.isoweekday() > 1:
        date = date - timedelta(days=date.isoweekday() - 1)
        return redirect(f"/chart/{date.year}/{date.month:02d}/{date.day:02d}", code=302)

    year, week, _ = date.isocalendar()
    chart = (
        db.session.query(Chart)
        .join(Song)
        .join(Artist, Artist.id == Chart.artist_id)
        .filter(Chart.year == year, Chart.week == week)
        .order_by(Chart.position)
    )
    if station:
        chart = chart.filter(Chart.station == station)
    else:
        chart = chart.filter(Chart.station == None)

    return render_template(
        "stats/chart.html",
        chart=chart,
        year=year,
        week=week,
        full_date=date.strftime("%a, %b %d, %Y"),
        station=station,
        station_list=stations(),
    )
