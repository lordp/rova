import requests
import json
import re
from datetime import datetime
from slugify import slugify
import pytz
import logging

from flaskr import db
from flaskr.models import Artist, Song, Played

logger = logging.getLogger('rova')
logger.setLevel(logging.INFO)

formatter = logging.Formatter("[%(asctime)s] %(message)s")

ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


def add_record(artist_name, song_name, song_length, played_time, station):
    artist = db.session.query(Artist).filter(Artist.name == artist_name).first()
    if not artist:
        artist = Artist(name=artist_name, slug=slugify(artist_name))
        db.session.add(artist)

    song = db.session.query(Song).filter(Song.name == song_name, Song.artist_id == artist.id).first()
    if not song:
        song = Song(name=song_name, slug=slugify(song_name), artist_id=artist.id, length=song_length)
        db.session.add(song)

    db.session.commit()

    play = db.session.query(Played).filter(Played.artist_id == artist.id, Played.song_id == song.id, Played.played_time == played_time, Played.station == station).first()
    if not play:
        logger.info(f"[{station}] {artist.name} - {song.name}")
        play = Played(artist_id=artist.id, song_id=song.id, played_time=played_time, station=station)
        db.session.add(play)

    db.session.commit()

rova_base_url = "https://radio-api.mediaworks.nz/radio-api/v3/station/{station}/auckland/web"
rova_stations = {
    "edge": "theedge",
    "more": "morefm",
    "mai": "maifm",
    "george": "georgefm",
    "rock": "therock",
    "sound": "thesound",
    "breeze": "thebreeze",
    "magic": "magic"
}

iheart_base_url = "https://nz.api.iheart.com/api/v3/live-meta/stream/{station}/currentTrackMeta"
iheart_stations = {
    "zm": 6190,
    "hauraki": 6191,
    "flava": 6159,
    "coast": 6193,
    "thehits": 6197,
    "nztop40": 6491,
    "lifefm": 6938,
    "southernstar": 6939,
    "rhema": 6937,
}

pattern = r" ?(\*|\+|\^|NM)$"
tz = pytz.timezone("Pacific/Auckland")

songs = []

for station, tag in rova_stations.items():
    try:
        req = requests.get(rova_base_url.format(station=tag))
        j = json.loads(req.content.decode("utf-8"))

        song_name = re.sub(pattern, "", j["nowPlaying"][0]["name"])
        artist_name = j["nowPlaying"][0]["artist"]
        played_time = f"{j['nowPlaying'][0]['played_date']} {j['nowPlaying'][0]['played_time']}"
        played_time = datetime.strptime(played_time, "%m/%d/%Y %H:%M:%S")
        played_time = tz.localize(played_time)
        length = int(j["nowPlaying"][0]["length_in_secs"])

        songs.append({'artist': artist_name, 'name': song_name, 'length': length, 'time': played_time, 'station': station})
    except (json.decoder.JSONDecodeError, requests.adapters.ConnectionError):
        pass

for station, tag in iheart_stations.items():
    try:
        req = requests.get(iheart_base_url.format(station=tag))
        j = json.loads(req.content.decode("utf-8"))

        song_name = j["title"]
        artist_name = j["artist"]
        played_time = datetime.fromtimestamp(j['startTime'] / 1000)
        length = j["trackDuration"]

        songs.append({'artist': artist_name, 'name': song_name, 'length': length, 'time': played_time, 'station': station})
    except (json.decoder.JSONDecodeError, requests.adapters.ConnectionError):
        pass

for song in songs:
    add_record(song['artist'], song['name'], song['length'], song['time'], song['station'])