#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import *
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
# from models import db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://Julianna@localhost:5432/fyyur'
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
# db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

# Used 'https://stackoverflow.com/questions/63269150/typeerror-parser-must-be-a-string-or-character-stream-not-datetime'
#  as a source to fix datetime TypeError. 
def format_datetime(value, format='medium'):
  if isinstance(value, str):
     date = dateutil.parser.parse(value)
  else: date = value
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  artists = Artist.query.all()
  return render_template('pages/home.html', artists=artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():   
  places = Venue.query.distinct(Venue.city, Venue.state).all()
  venues = Venue.query.all()
  areas = []

  for place in places:
     venue_data = []
     for venue in venues:
        if venue.city == place.city and venue.state == place.state:
           num_upcoming_shows = 0
           for show in venue.shows:
              if show.start_time > datetime.now():
                 num_upcoming_shows += 1
           venue_data.append({
              'id': venue.id,
              'name': venue.name, 
              'shows': num_upcoming_shows
           })
     areas.append({
        'city': venue.city, 
        'state': venue.state, 
        'venues': venue_data
     })
  
  return render_template('pages/venues.html', areas=areas )


@app.route('/venues/search', methods=['POST'])
def search_venues():
  query = request.form.get('search_term', '')
  data = Venue.query.filter(Venue.name.ilike(f'%{query}%')).all()
  searched_venues = []
  current_time = datetime.now()
  for venue in data:
     count = Show.query.filter_by(venue_id = venue.id).filter(Show.start_time > current_time).count()
     searched_venues.append({"id":venue.id,"name":venue.name,"num_upcoming_shows":count})
     response={
        "count": len(data), 
        "data": searched_venues
     }
  return render_template('pages/search_venues.html', results=response, 
                         search_term=request.form.get('search_term', ''))
  

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  past_shows = []
  upcoming_shows = []

  venue = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id=venue_id)
  
  for show in shows:
     show_data = {
        'id': show.id, 
        'artist_id': show.artist_id, 
        'venue_id': show.venue_id, 
        'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
     }
     if show.start_time < datetime.now():
        past_shows.append(show_data)
     else:
        upcoming_shows.append(show_data)

  data = {
    "id": venue.id, 
    "name": venue.name, 
    "city": venue.city, 
    "state": venue.state, 
    "address": venue.address, 
    "phone": venue.phone, 
    "genres": venue.genres, 
    "facebook_link": venue.facebook_link, 
    "image_link": venue.image_link, 
    "website_link": venue.website_link, 
    "seeking_talent": venue.seeking_talent, 
    "seeking_description": venue.seeking_description, 
    "past_shows": past_shows, 
    "upcoming_shows": upcoming_shows, 
    "num_past_shows": len(past_shows), 
    "num_upcoming_shows": len(upcoming_shows)
  }
  
  return render_template('pages/show_venue.html', venue=data, shows=shows)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():

  form = VenueForm()

  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
  error = False
  try: 
    name = request.form['name']
    city = request.form['city']
    state = request.form['city']
    address = request.form['city']
    phone = request.form['phone']
    genres = request.form['genres']
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    website_link = request.form['website_link']

    venue = Venue(
        name=name,
        city=city,
        state=state,
        address=address,
        phone=phone, 
        genres=genres,
        facebook_link=facebook_link,
        image_link=image_link, 
        website_link=website_link, 
     )
    active_list = Venue.query.all()
    venue.list = active_list
    db.session.add(venue)
    db.session.commit()
  except:
     error = True
     flash('An error occurred. Venue ' + name + ' could not be listed.')
     db.session.rollback()
  finally:
     db.session.close()
  if not error:     
     flash('Venue ' + request.form['name'] + ' was successfully listed!')
        
  return render_template('pages/home.html', form=form)


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
     Venue.query.filter_by(id=venue_id).delete()
     db.session.commit()
  except:
     db.session.rollback()
  finally:
     db.session.close()
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return jsonify({ 'success': True })

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  return render_template('pages/artists.html', artists=artists)
    

@app.route('/artists/search', methods=['POST'])
def search_artists():
  query = request.form.get('search_term', '')
  data = Artist.query.filter(Artist.name.ilike(f'%{query}%')).all()
  searched_artists = []
  current_time = datetime.now()
  for artist in data:
    count = Show.query.filter_by(artist_id = artist.id).filter(Show.start_time > current_time).count()
    searched_artists.append({"id":artist.id,"name":artist.name,"num_upcoming_shows":count})
    response={
      "count": len(data),
      "data": searched_artists
    }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  past_shows = []
  upcoming_shows = []
  
  artist = Artist.query.get(artist_id)
  shows = Show.query.filter_by(artist_id=artist_id)

  for show in shows:
    show_data = {
      'id': show.id, 
      'artist_id': show.artist_id, 
      'venue_id': show.venue_id, 
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time < datetime.now():
      past_shows.append(show_data)
    else:
      upcoming_shows.append(show_data)
  

  data = ({
    "id": artist.id, 
    "name": artist.name, 
    "city": artist.city, 
    "state": artist.state,  
    "phone": artist.phone, 
    "genres": artist.genres, 
    "facebook_link": artist.facebook_link, 
    "image_link": artist.image_link, 
    "website_link": artist.website_link, 
    "seeking_venue": artist.seeking_venue, 
    "seeking_description": artist.seeking_description, 
    "past_shows": past_shows, 
    "upcoming_shows": upcoming_shows, 
    "num_past_shows": len(past_shows), 
    "num_upcoming_shows": len(upcoming_shows)
  })
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  data = ({
    "id": artist.id, 
    "name": artist.name, 
    "city": artist.city, 
    "state": artist.state,  
    "phone": artist.phone, 
    "genres": artist.genres, 
    "facebook_link": artist.facebook_link, 
    "image_link": artist.image_link, 
    "website_link": artist.website_link, 
    "seeking_venue": artist.seeking_venue, 
    "seeking_description": artist.seeking_description,
  })
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  old_artist_data = Artist.query.get(artist_id)
  new_artist_data = ArtistForm(request.form)

  error = False
  try:
     old_artist_data.name = new_artist_data.name.data, 
     old_artist_data.city = new_artist_data.city.data, 
     old_artist_data.state = new_artist_data.state.data, 
     old_artist_data.phone = new_artist_data.phone.data, 
     old_artist_data.genres = new_artist_data.genres.data, 
     old_artist_data.facebook_link = new_artist_data.facebook_link.data, 
     old_artist_data.image_link = new_artist_data.image_link.data, 
     old_artist_data.website_link = new_artist_data.website_link.data, 
     old_artist_data.seeking_venue = new_artist_data.seeking_venue.data, 
     old_artist_data.seeking_description = new_artist_data.seeking_description.data, 
     db.session.commit()
  except:
     error = True
     flash('An error occured. Artist could not be edited.')
     db.session.rollback()
  finally:
    if not error:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')        
        db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  form = VenueForm()
  venue = Venue.query.get(venue_id)

  data = ({
    "id": venue.id, 
    "name": venue.name, 
    "city": venue.city, 
    "state": venue.state, 
    "address": venue.address, 
    "phone": venue.phone, 
    "genres": venue.genres, 
    "facebook_link": venue.facebook_link, 
    "image_link": venue.image_link, 
    "website_link": venue.website_link, 
    "seeking_talent": venue.seeking_talent, 
    "seeking_description": venue.seeking_description
  })

  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  new_venue_data = VenueForm(request.form)

  try:
     old_venue_data = Venue.query.get_or_404(venue_id)
     new_venue_data.populate_obj(old_venue_data)
     db.session.commit()
     flash(f'Venue ' + request.form['name'] + ' was successfully edited!')
  except ValueError as e:
     db.session.rollback()
     flash('An error occured. Venue could not be edited.' + e)
  finally:  
     db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form = form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  error = False
  try: 
    name = request.form['name'],
    city = request.form['city'],
    state = request.form['state'],
    phone = request.form['phone'],
    image_link = request.form['image_link'],
    genres = request.form['genres'],
    facebook_link = request.form['facebook_link'],
    website_link = request.form['website_link'],
    seeking_description = request.form['seeking_description']
    artist = Artist(
        name=name, 
        city=city, 
        state=state, 
        phone=phone, 
        image_link=image_link, 
        genres=genres, 
        facebook_link=facebook_link, 
        website_link=website_link, 
        seeking_description=seeking_description
     )
    active_list = Artist.query.all()
    artist.list = active_list
    db.session.add(artist)
    db.session.commit()
  except:
     error = True
     flash('An error occured. Artist could not be added.')
     db.session.rollback()
  finally:
        db.session.close()
  if not error:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html', form = form)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  return render_template('pages/shows.html', shows = Show.query.all())

@app.route('/shows/create')
def create_shows():
# ****IMPORTANT: renders form. do not touch. IMPORTANT****
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)
# **** DO NOT TOUCH ABOVE ! ****


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time'] 
    show = Show(
      artist_id=artist_id, 
      venue_id=venue_id, 
      start_time=start_time
      )
    active_list = Show.query.all()
    show.list = active_list
    db.session.add(show)
    db.session.commit()
  except:
     error = True
     flash('An error occurred. Show could not be listed.')
     db.session.rollback()
  finally:
     db.session.close()
  if not error:
     flash('Your show has been listed!')
       
  return render_template('pages/home.html')

@app.route('/shows/search', methods=['POST'])
def search_shows():
   query = request.form.get('search_term', '')
   searched_shows = db.session.query(Venue.id.label('venue_id'),Venue.name.label('venue_name'),
                                     Artist.id.label('artist_id'),Artist.name.label('artist_name'),
                                     Artist.image_link.label('artist_image_link'),
                                     Show.show_time.label('start_time')).outerjoin(Venue).outerjoin(Artist).filter(or_(Artist.name.ilike(f'%{query}%'),
                                                                                                                       Venue.name.ilike(f'%{query}%'))).all()
   response={
      "count": len(searched_shows), 
      "data": searched_shows
   }
   return render_template('pages/search_shows.html', results=response, search_term=request.form.get('search_term', ''))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
