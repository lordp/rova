from flaskr import db
from sqlalchemy.orm import relationship


class Played(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), index=True)
    song = relationship("Song")
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), index=True)
    artist = relationship("Artist")
    station = db.Column(db.String(250), nullable=False, index=True)
    played_time = db.Column(db.DateTime, index=True)


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    slug = db.Column(db.String(250), nullable=False, index=True)
    songs = relationship("Song")
    plays = relationship("Played")


class Song(db.Model):
    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), index=True)
    artist = relationship("Artist")
    name = db.Column(db.String(250), nullable=False)
    slug = db.Column(db.String(250), nullable=False, index=True)
    length = db.Column(db.Integer)
    plays = relationship("Played")
