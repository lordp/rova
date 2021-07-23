from flaskr import db
from flaskr.models import Artist, Song, Played, Chart

from sqlalchemy.sql.expression import desc

from datetime import datetime, timedelta
import sys


def generate(year, week):
    if week > 1:
        prev_week = db.session.query(Chart).filter(Chart.week == week - 1, Chart.year == year, Chart.station == None).order_by(Chart.position).all()
        prev_week_stations = {}
        for station in urls:
            prev_week_stations[station] = db.session.query(Chart).filter(Chart.week == week - 1, Chart.year == year, Chart.station == station).order_by(Chart.position).all()
    else:
        prev_week = []
        prev_week_stations = {}
        for station in urls:
            prev_week_stations[station] = []

    print("-" * 20)
    print(f"Generating for week #{week} of year {year} -> ", end="")
    rows = db.session.query(Chart).filter(Chart.week==week, Chart.year==year).delete(synchronize_session=False)
    db.session.commit()

    top_10 = db.session.query(Artist.id, Song.id, db.func.count(Played.id).label("cnt")).\
        select_from(Played).\
        join(Song, Artist).\
        filter(db.func.date_part('week', Played.played_time) == week, db.func.date_part('year', Played.played_time) == year).\
        group_by(Artist.id, Song.id).\
        order_by(desc("cnt")).\
        limit(10)

    for idx, entry in enumerate(top_10):
        chart = Chart(artist_id=entry[0], song_id=entry[1], position=idx + 1, play_count=entry[2], year=year, week=week)
        chart.set_change(prev_week)
        db.session.add(chart)
        print(".", end="")

    print()
    for station in urls:
        print(f"{station} -> ", end="")
        station_top_10 = db.session.query(Artist.id, Song.id, Played.station, db.func.count(Played.id).label("cnt")).\
            select_from(Played).\
            join(Song, Artist).\
            filter(db.func.date_part('week', Played.played_time) == week, db.func.date_part('year', Played.played_time) == year, Played.station == station).\
            group_by(Artist.id, Song.id, Played.station).\
            order_by(desc("cnt")).\
            limit(10)

        for idx, entry in enumerate(station_top_10):
            chart = Chart(artist_id=entry[0], song_id=entry[1], position=idx + 1, play_count=entry[3], year=year, week=week, station=station)
            chart.set_change(prev_week_stations[station])
            db.session.add(chart)
            print(".", end="")

        print()

    db.session.commit()



urls = {
    'breeze': 'The Breeze',
    'rock': 'The Rock',
    'sound': 'The Sound',
    'mai': 'Mai FM',
    'more': 'More FM',
    'george': 'George FM',
    'magic': 'Magic Music',
    'edge': 'The Edge',
    'zm': 'ZM',
    'hauraki': 'Radio Hauraki',
    'nztop40': 'NZ Top 40',
    'flava': 'Flava',
    'coast': 'Coast',
    'thehits': 'The Hits',
    'lifefm': 'Life FM',
    'southernstar': 'Southern Star',
    'rhema': 'Radio Rhema',
    'kick': 'Kick'
}

if len(sys.argv) > 1:
    if sys.argv[1] == 'full':
        year, week, _ = datetime.now().isocalendar()
        for week_num in range(week):
            generate(year, week_num + 1)
else:
    date = datetime.now()
    if date.isoweekday() > 1:
        date = date - timedelta(days=date.isoweekday() - 1)

    week = date.isocalendar()[1]
    year = date.isocalendar()[0]

    generate(year, week)

