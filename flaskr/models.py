from flaskr import db
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index


class Played(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey("songs.id"), index=True)
    song = relationship("Song")
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), index=True)
    artist = relationship("Artist")
    station = db.Column(db.String(250), nullable=False, index=True)
    played_time = db.Column(db.DateTime(timezone=True), index=True)


class Artist(db.Model):
    __tablename__ = "artists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    slug = db.Column(db.String(250), nullable=False, index=True)
    songs = relationship("Song", back_populates="artist")
    plays = relationship("Played", back_populates="artist")


class Song(db.Model):
    __tablename__ = "songs"

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), index=True)
    artist = relationship("Artist", back_populates="songs")
    name = db.Column(db.String(250), nullable=False)
    slug = db.Column(db.String(250), nullable=False, index=True)
    length = db.Column(db.Integer)
    plays = relationship("Played", back_populates="song")


class Chart(db.Model):
    __tablename__ = "charts"

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    week = db.Column(db.Integer)
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), index=True)
    artist = relationship("Artist")
    song_id = db.Column(db.Integer, db.ForeignKey("songs.id"), index=True)
    song = relationship("Song")
    station = db.Column(db.String(250), index=True)
    position = db.Column(db.Integer)
    play_count = db.Column(db.Integer)
    change = db.Column(db.Integer)

    __table_args__ = (Index("week_year", "year", "week"),)

    def set_change(self, prev):
        for entry in prev:
            if (
                entry
                and entry.song_id == self.song_id
                and entry.artist_id == self.artist_id
            ):
                self.change = entry.position - self.position
