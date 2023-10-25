#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import datetime
import dateutil.parser
import babel
from flask import Flask, abort, render_template, request, Response, flash, redirect, url_for
#from markupsafe import Markup
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys, time
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database == DONE
#     -- Done; on config.py. Database name is 'fire'

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
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate == DONE
    #     -- Done; added a migrate object above to enable use of Flask-Migrate

    genres = db.Column(db.String(120), nullable=False, default='Other')
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    show = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return f'<NEW VENUEE: {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.image_link} {self.facebook_link} {self.genres} {self.website_link} {self.seeking_talent} {self.seeking_description}>'


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False, default='Other')
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate == DONE
    website_link = db.Column(db.String(120), nullable=False, default='https://www.google.com')
    seeking_venue = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    show = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
       return f'<NEW ARTISTT: {self.id} {self.name} {self.city} {self.state} {self.phone} {self.image_link} {self.facebook_link} {self.genres} {self.website_link} {self.seeking_venue} {self.seeking_description}>'


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. == DONE

class Show(db.Model):
   __tablename__ = 'shows'

   id = db.Column(db.Integer, primary_key=True)
   artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
   venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
   start_time = db.Column(db.String(120), nullable=False, default=datetime.now)

   def __repr__(self):
      return f'<NEW SHOWW: {self.id} {self.start_time}, list {self.artist_id} {self.venue_id}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data. == DONE
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue. == DONE
  """ data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }] """

  cities_list = Venue.query.distinct('city')
  areas = []

  for one_city in cities_list:
    city_data = {}
    city_data['city'] = one_city.city
    city_data['state'] = one_city.state
    city_data['venues'] = Venue.query.filter_by(city = one_city.city)
    city_data['num_upcoming_shows'] = Show.query.filter_by(venue_id = one_city.id).count()
    areas.append(city_data)

  return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive. == DONE
  # seach for Hop should return "The Musical Hop". == DONE
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee" == DONE
  """ response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', '')) """

  search_term = request.form['search_term']
  search_term_case_insensitive = '%' + search_term + '%'
  
  search_response = {}
  search_response['count'] = 0
  search_response['data'] = []

  #venues_from_search = Venue.query.filter(Venue.name.contains(search_term)) # .contains() is not case-insensitive
  venues_from_search = Venue.query.filter(Venue.name.ilike(search_term_case_insensitive))
  venues_from_search_count = Venue.query.filter(Venue.name.ilike(search_term_case_insensitive)).count()

  for venue in venues_from_search:
    this_venue = {}
    this_venue['id'] = venue.id
    this_venue['name'] = venue.name
    this_venue['num_upcoming_shows'] = Show.query.filter_by(venue_id = venue.id).count()

    search_response['count'] = venues_from_search_count
    search_response['data'].append(this_venue)

  return render_template('pages/search_venues.html', results=search_response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id == DONE
  """ data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0] """

  error = False

  try:
    venue_selected_data = {}
    venue_selected = Venue.query.get(venue_id)
    shows_joinedwith_artists = Show.query.filter_by(venue_id = venue_id).join(Artist).all()

    venue_selected_data['id'] = venue_selected.id
    venue_selected_data['name'] = venue_selected.name
    venue_selected_data['genres'] = venue_selected.genres
    venue_selected_data['address'] = venue_selected.address
    venue_selected_data['city'] = venue_selected.city
    venue_selected_data['state'] = venue_selected.state
    venue_selected_data['phone'] = venue_selected.phone
    venue_selected_data['website_link'] = venue_selected.website_link
    venue_selected_data['facebook_link'] = venue_selected.facebook_link
    venue_selected_data['seeking_talent'] = venue_selected.seeking_talent
    venue_selected_data['image_link'] = venue_selected.image_link
    venue_selected_data['past_shows'] = []
    venue_selected_data['upcoming_shows'] = []
    venue_selected_data['past_shows_count'] = 0
    venue_selected_data['upcoming_shows_count'] = 0

    #traverse the Show+Artist data to retrieve the artist details from past shows and upcoming shows
    for show in shows_joinedwith_artists:
      this_show = {}
      this_show['artist_id'] = show.artist_id
      this_show['artist_name'] = show.artist.name
      this_show['artist_image_link'] = show.artist.image_link
      this_show['start_time'] = show.start_time

      #get current timestamp and convert timestamp from db, then compare to populate past shows and upcoming shows
      show_start_time = show.start_time
      show_start_time_formatted = datetime.strptime(show_start_time, '%Y-%m-%d %H:%M:%S')
      db_timestamp = datetime.timestamp(show_start_time_formatted)
      current_timestamp = time.time()

      if current_timestamp > db_timestamp:
        venue_selected_data['past_shows'].append(this_show)
        venue_selected_data['past_shows_count'] += 1
      else:
        venue_selected_data['upcoming_shows'].append(this_show)
        venue_selected_data['upcoming_shows_count'] += 1

  except:
    error = True
    print(sys.exc_info())

  if error:
    error = False
    flash('This venue does NOT exist in our records.')
    abort(404)
  
  return render_template('pages/show_venue.html', venue=venue_selected_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead == DONE
  error = False
  venueName = ''
  data = {}
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form['genres']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website_link = request.form['website_link']
    seeking_talent = request.form['seeking_talent']
    seeking_description = request.form['seeking_description']

    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, image_link=image_link, facebook_link=facebook_link, website_link=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
     
    db.session.add(venue)
    db.session.commit()

    venueName = name
    print(venue)

    data['id'] = venue.id
    data['name'] = venue.name
    data['city'] = venue.city
    data['state'] = venue.state
    data['address'] = venue.address
    data['phone'] = venue.phone
    data['genres'] = venue.genres
    data['image_link'] = venue.image_link
    data['facebook_link'] = venue.facebook_link
    data['website_link'] = venue.website_link
    data['seeking_talent'] = venue.seeking_talent
    data['seeking_description'] = venue.seeking_description

  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead. == DONE
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    flash('An error occurred. Venue ' + venueName + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  else:
    error=False
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # TODO: modify data to be the data object returned from db insertion == DONE
  return render_template('pages/home.html', venues=data)



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using == DONE
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  error = False
  
  try:
    venue_to_delete = Venue.query.get(venue_id)
    db.session.delete(venue_to_delete)
    db.session.commit()

  except:
    error = True
    db.session.rollback()

  finally:
    db.session.close()

  if error:
    error = False
    flash('An error occured. Venue could NOT be deleted.')
    abort(404)
  
  return None 

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database == DONE
  """ data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }] """

  artist_data = []
  artists_all = Artist.query.all()

  for artist in artists_all:
    artist_formatted = {}
    artist_formatted['id'] = artist.id
    artist_formatted['name'] = artist.name
    artist_data.append(artist_formatted)

  return render_template('pages/artists.html', artists=artist_data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. == DONE
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band". == DONE
  # search for "band" should return "The Wild Sax Band". == DONE
  """ response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', '')) """

  search_term = request.form['search_term']
  search_term_case_insensitive = '%' + search_term + '%'

  search_response = {}
  search_response['count'] = 0
  search_response['data'] = []

  artists_from_search = Artist.query.filter(Artist.name.ilike(search_term_case_insensitive))
  artists_from_search_count = Artist.query.filter(Artist.name.ilike(search_term_case_insensitive)).count()

  for artist in artists_from_search:
    this_artist = {}
    this_artist['id'] = artist.id
    this_artist['name'] = artist.name
    this_artist['num_upcoming_shows'] = Show.query.filter_by(artist_id = artist.id).count()

    search_response['count'] = artists_from_search_count
    search_response['data'].append(this_artist)

  return render_template('pages/search_artists.html', results=search_response, search_term=search_term)



@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id == DONE
  """ data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  } """
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]

  error = False
  try:
    artist_selected = Artist.query.get(artist_id)
    shows_joinedwith_venue = Show.query.filter_by(artist_id = artist_id).join(Venue).all()
    print(shows_joinedwith_venue)
    artist_selected_data = {}

    artist_selected_data['id'] = artist_selected.id
    artist_selected_data['name'] = artist_selected.name
    artist_selected_data['genres'] = artist_selected.genres
    artist_selected_data['city'] = artist_selected.city
    artist_selected_data['state'] = artist_selected.state
    artist_selected_data['phone'] = artist_selected.phone
    artist_selected_data['seeking_venue'] = artist_selected.seeking_venue
    artist_selected_data['image_link'] = artist_selected.image_link
    artist_selected_data['past_shows'] = []
    artist_selected_data['upcoming_shows'] = []
    artist_selected_data['past_shows_count'] = 0
    artist_selected_data['upcoming_shows_count'] = 0

    for show in shows_joinedwith_venue:
      this_show = {}
      this_show['venue_id'] = show.venue_id
      this_show['venue_name'] = show.venue.name
      this_show['venue_image_link'] = show.venue.image_link
      this_show['start_time'] = show.start_time

      showstart_time = show.start_time
      showstart_time_formatted = datetime.strptime(showstart_time, '%Y-%m-%d %H:%M:%S')
      db_timestamp = datetime.timestamp(showstart_time_formatted)
      current_timestamp = time.time()

      if (current_timestamp > db_timestamp):
        artist_selected_data['past_shows'].append(this_show)
        artist_selected_data['past_shows_count'] += 1
      else:
        artist_selected_data['upcoming_shows'].append(this_show)
        artist_selected_data['upcoming_shows_count'] += 1

  except:
    error = True
    print(sys.exc_info())

  if error:
    error = False
    flash('This artist does NOT exist in our records.')
    abort(404)

  return render_template('pages/show_artist.html', artist=artist_selected_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>

  artist_to_edit = Artist.query.get(artist_id)

  artist_data = {}
  artist_data['id'] = artist_to_edit.id
  artist_data['name'] = artist_to_edit.name
  artist_data['genres'] = artist_to_edit.genres
  artist_data['city'] = artist_to_edit.city
  artist_data['state'] = artist_to_edit.state
  artist_data['phone'] = artist_to_edit.phone
  artist_data['website_link'] = artist_to_edit.website_link
  artist_data['facebook_link'] = artist_to_edit.facebook_link
  artist_data['seeking_venue'] = artist_to_edit.seeking_venue
  artist_data['seeking_description'] = artist_to_edit.seeking_description
  artist_data['image_link'] = artist_to_edit.image_link

  form.name.data = artist_to_edit.name
  form.genres.data = artist_to_edit.genres
  form.city.data = artist_to_edit.city
  form.state.data = artist_to_edit.state
  form.phone.data = artist_to_edit.phone
  form.website_link.data = artist_to_edit.website_link
  form.facebook_link.data = artist_to_edit.facebook_link
  form.seeking_venue.data = artist_to_edit.seeking_venue
  form.seeking_description.data = artist_to_edit.seeking_description
  form.image_link.data = artist_to_edit.image_link

  return render_template('forms/edit_artist.html', form=form, artist=artist_data)



@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing artist record with ID <artist_id> using the new attributes

  error = False

  try:
    artist_edit = Artist.query.get(artist_id)

    artist_edit.name = request.form['name']
    artist_edit.genres = request.form['genres']
    artist_edit.city = request.form['city']
    artist_edit.state = request.form['state']
    artist_edit.phone = request.form['phone']
    artist_edit.website_link = request.form['website_link']
    artist_edit.facebook_link = request.form['facebook_link']
    artist_edit.seeking_venue = request.form['seeking_venue']
    artist_edit.seeking_description = request.form['seeking_description']
    artist_edit.image_link = request.form['image_link']

    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  if error:
    error = False
    flash('Error occured: edit was not successfull.')
    abort(404)
  
  else:
    flash('Artist ' + request.form['name'] + ' updated successully.')

  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead == DONE
  # TODO: modify data to be the data object returned from db insertion == DONE

  error = False
  artist_name = ''
  artist_data = {}

  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form['genres']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website_link = request.form['website_link']
    seeking_venue = request.form['seeking_venue']
    seeking_description = request.form['seeking_description']

    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, image_link=image_link, facebook_link=facebook_link, website_link=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description)

    db.session.add(artist)
    db.session.commit()

    artist_name = name
    print(artist)

    artist_data['id'] = artist.id
    artist_data['id'] = artist.id
    artist_data['name'] = artist.name
    artist_data['city'] = artist.city
    artist_data['state'] = artist.state
    artist_data['phone'] = artist.phone
    artist_data['genres'] = artist.genres
    artist_data['image_link'] = artist.image_link
    artist_data['facebook_link'] = artist.facebook_link
    artist_data['website_link'] = artist.website_link
    artist_data['seeking_venue'] = artist.seeking_venue
    artist_data['seeking_description'] = artist.seeking_description

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  if error:
    print(sys.exc_info())
    # TODO: on unsuccessful db insert, flash an error instead. == DONE
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occured. Artist ' + artist_name + ' could NOT be listed.')

  else:
    error = False
    # on successful db insert, flash success
    flash('Artist ' + artist_name + ' was successfully listed!')
  
  return render_template('pages/home.html', artists=artist_data)
  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data. == DONE
  """ data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]

  return render_template('pages/shows.html', shows=data) """

  all_shows = Show.query.all()
  
  shows_data = []

  #traverse all shows and get the required show, venue and artist data for our view
  for show in all_shows:
    this_show = {}
    this_show['venue_id'] = show.venue_id
    this_show['venue_name'] = show.venue.name
    this_show['artist_id'] = show.artist_id
    this_show['artist_name'] = show.artist.name
    this_show['artist_image_link'] = show.artist.image_link
    this_show['start_time'] = show.start_time

    shows_data.append(this_show)

  return render_template('pages/shows.html', shows=shows_data)



@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead == DONE

  error = False

  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

    db.session.add(show)
    db.session.commit()

    print(show)

  except:
    error = True
    db.session.rollback()

  finally:
    db.session.close()

  if error:
    # TODO: on unsuccessful db insert, flash an error instead. == DONE
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occured. SHOW could not be listed.')

  else:
    # on successful db insert, flash success
    flash('Show was successfully listed!')

  return render_template('pages/home.html')


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
""" if __name__ == '__main__':
    app.run()
 """
# Or specify port manually:
if __name__ == '__main__':
    #port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=5001)
