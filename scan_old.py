import requests
import json
import re
from datetime import datetime
from slugify import slugify

from flaskr import db
from flaskr.models import Artist, Song, Played
from sqlalchemy.sql import text

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

counter = 0

played_old = db.session.execute("select * from played_old")
for record in played_old:
    artist_name = record[3]
    artist_slug = slugify(artist_name)
    artist = db.session.query(Artist).filter(Artist.name == artist_name).first()
    if not artist:
        # print(f"Creating new artist record - {artist_name}")
        artist = Artist(name=artist_name, slug=artist_slug)
        db.session.add(artist)

    song_name = record[2]
    song_slug = slugify(song_name)
    length = record[5]
    song = db.session.query(Song).filter(Song.name == song_name, Song.artist_id == artist.id).first()
    if not song:
        # print(f"Creating new song record - {song_name}")
        song = Song(name=song_name, slug=song_slug, artist_id=artist.id, length=length)
        db.session.add(song)

    db.session.commit()

    played_time = record[4]
    tag = record[1]
    play = db.session.query(Played).filter(Played.artist_id == artist.id, Played.song_id == song.id, Played.played_time == played_time, Played.station == tag).first()
    if not play:
        # print("Creating new play record")
        play = Played(artist_id=artist.id, song_id=song.id, played_time=played_time, station=tag)
        db.session.add(play)

    db.session.commit()

    if counter % 100 == 0:
        print(".", end="", flush=True)
    if counter % 1000 == 0:
        print(counter, flush=True)

    counter += 1