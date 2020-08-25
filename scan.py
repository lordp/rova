import requests
import json
import re
from datetime import datetime
from slugify import slugify
import pytz

from flaskr import db
from flaskr.models import Artist, Song, Played

base_url = "https://radio-api.mediaworks.nz/radio-api/v3/station/{station}/auckland/web"

urls = {
    "edge": "theedge",
    "more": "morefm",
    "mai": "maifm",
    "george": "georgefm",
    "rock": "therock",
    "sound": "thesound",
    "breeze": "thebreeze",
    "magic": "magic"
}

pattern = r" ?(\*|\+|\^|NM)$"
tz = pytz.timezone("Pacific/Auckland")

for station, tag in urls.items():
    req = requests.get(base_url.format(station=tag))
    j = json.loads(req.content.decode("utf-8"))

    print("-" * 20)
    print(station)

    song_name = re.sub(pattern, "", j["nowPlaying"][0]["name"])
    song_slug = slugify(song_name)
    artist_name = j["nowPlaying"][0]["artist"]
    artist_slug = slugify(artist_name)
    played_time = f"{j['nowPlaying'][0]['played_date']} {j['nowPlaying'][0]['played_time']}"
    played_time = datetime.strptime(played_time, "%m/%d/%Y %H:%M:%S")
    played_time = tz.localize(played_time)
    length = j["nowPlaying"][0]["length_in_secs"]

    artist = db.session.query(Artist).filter(Artist.name == artist_name).first()
    if not artist:
        print(f"Creating new artist record - {artist_name}")
        artist = Artist(name=artist_name, slug=artist_slug)
        db.session.add(artist)

    song = db.session.query(Song).filter(Song.name == song_name, Song.artist_id == artist.id).first()
    if not song:
        print(f"Creating new song record - {song_name}")
        song = Song(name=song_name, slug=song_slug, artist_id=artist.id, length=length)
        db.session.add(song)

    db.session.commit()

    play = db.session.query(Played).filter(Played.artist_id == artist.id, Played.song_id == song.id, Played.played_time == played_time, Played.station == station).first()
    if not play:
        print("Creating new play record")
        play = Played(artist_id=artist.id, song_id=song.id, played_time=played_time, station=station)
        db.session.add(play)

    db.session.commit()