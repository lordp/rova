from flaskr import db
from sqlalchemy.orm import relationship


class Played(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    song_slug = db.Column(db.String(250), nullable=False, index=True)
    artist = db.Column(db.String(250), nullable=False)
    artist_slug = db.Column(db.String(250), nullable=False, index=True)
    station = db.Column(db.String(250), nullable=False, index=True)
    played_time = db.Column(db.DateTime)
    length = db.Column(db.Integer)


# class Artist(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(250), nullable=False)
#     slug = db.Column(db.String(250), nullable=False)
#     songs = relationship("Song")


# class Song(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
#     name = db.Column(db.String(250), nullable=False)
#     slug = db.Column(db.String(250), nullable=False)

