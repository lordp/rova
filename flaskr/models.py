from flaskr import db


class Played(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    artist = db.Column(db.String(250), nullable=False)
    artist_slug = db.Column(db.String(250), nullable=False)
    station = db.Column(db.String(250), nullable=False)
    played_time = db.Column(db.DateTime)
    length = db.Column(db.Integer)
