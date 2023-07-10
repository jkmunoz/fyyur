from flask_sqlalchemy import SQLAlchemy
from app import db

# db = SQLAlchemy()

class Venue(db.Model):
    __tablename__ = 'venues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(1000))
    shows = db.relationship('Show', backref='venue',lazy=True)

    def __repr__(self):
      return f'<venues {self.id} {self.name}>'
    

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    genres = db.Column(db.String, nullable=False)
    facebook_link = db.Column(db.String)
    image_link = db.Column(db.String)
    website_link = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(200))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return f'<artists {self.id} {self.name}>'

class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
      return f'<shows {self.artist_id} {self.venue_id}>'

