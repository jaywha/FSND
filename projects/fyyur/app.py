# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import logging
import sys
from babel import dates
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app, session_options={"expire_on_commit": False})

migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

UpcomingShowToArtist_Association = db.Table('UpcomingShowToArtist',
                                            db.Column('show_id', db.Integer,
                                                      db.ForeignKey('Show.id'), primary_key=True),
                                            db.Column('artist_id', db.Integer,
                                                      db.ForeignKey('Artist.id'), primary_key=True))


UpcomingShowToVenue_Association = db.Table('UpcomingShowToVenue',
                                           db.Column('show_id', db.Integer,
                                                     db.ForeignKey('Show.id'), primary_key=True),
                                           db.Column('venue_id', db.Integer,
                                                     db.ForeignKey('Venue.id'), primary_key=True))

PastShowToArtist_Association = db.Table('PastShowToArtist',
                                        db.Column('show_id', db.Integer,
                                                  db.ForeignKey('Show.id'), primary_key=True),
                                        db.Column('artist_id', db.Integer,
                                                  db.ForeignKey('Artist.id'), primary_key=True))


PastShowToVenue_Association = db.Table('PastShowToVenue',
                                       db.Column('show_id', db.Integer,
                                                 db.ForeignKey('Show.id'), primary_key=True),
                                       db.Column('venue_id', db.Integer,
                                                 db.ForeignKey('Venue.id'), primary_key=True))


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(240))
    upcoming_shows = db.relationship('Show', secondary=UpcomingShowToVenue_Association,
                                     backref=db.backref('upcoming_venue', lazy=True))
    upcoming_shows_count = db.Column(db.Integer, server_default="0")
    past_shows = db.relationship('Show', secondary=PastShowToVenue_Association,
                                 backref=db.backref('past_venue', lazy=True))
    past_shows_count = db.Column(db.Integer, server_default="0")

    def __repr__(self):
        return f'<Venue {self.id} {self.name} {self.city} {self.state}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(240))
    upcoming_shows = db.relationship('Show', secondary=UpcomingShowToArtist_Association,
                                     backref=db.backref('upcoming_artist', lazy=True))
    upcoming_shows_count = db.Column(db.Integer, server_default="0")
    past_shows = db.relationship('Show', secondary=PastShowToArtist_Association,
                                 backref=db.backref('past_artist', lazy=True))
    past_shows_count = db.Column(db.Integer, server_default="0")

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer)
    artist_name = db.Column(db.String)
    artist_image_link = db.Column(db.String)
    venue_id = db.Column(db.Integer)
    venue_name = db.Column(db.String)
    venue_image_link = db.Column(db.String)
    start_time = db.Column(db.String)

    def __repr__(self):
        return f'<Show {self.id} {self.artist_id} {self.venue_id}>'


db.create_all()

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, date_format='medium'):
    date = dateutil.parser.parse(value)
    if date_format == 'full':
        date_format = "EEEE MMMM, d, y 'at' h:mma"
    elif date_format == 'medium':
        date_format = "EE MM, dd, y h:mma"
    elif date_format == 'showtime':
        date_format = "yyyy-MM-ddThh:mm"
    return babel.dates.format_datetime(date, date_format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    sql_data = Venue.query.all()

    location_had_shows_already = False
    for row in sql_data:
        for location in data:
            if location["city"] == row.city and location["state"] == row.state:
                location["venues"].append({
                    "id": row.id,
                    "name": row.name,
                    "num_upcoming_shows": row.upcoming_shows_count
                })
                location_had_shows_already = True
                break
            pass
        pass

        if not location_had_shows_already:
            data.append({
                "city": row.city,
                "state": row.state,
                "venues": [{
                    "id": row.id,
                    "name": row.name,
                    "num_upcoming_shows": row.upcoming_shows_count
                }]
            })
    pass

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    sql_data = Venue.query.filter(Venue.name.contains(request.form['search_term'])).all()

    response = {
        "count": len(sql_data),
        "data": []
    }

    for result in sql_data:
        response["data"].append({
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": result.upcoming_shows_count,
        })
    pass

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/None')
def ignore_null_venue_route():
    """
    Needed since calls to this route were producing errors.
    """
    return {}


@app.route('/venues/<venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    sql_data = Venue.query.get(venue_id)

    venue = {
        "id": sql_data.id,
        "name": sql_data.name,
        "genres": [],
        "city": sql_data.city,
        "state": sql_data.state,
        "phone": sql_data.phone,
        "website": sql_data.website,
        "facebook_link": sql_data.facebook_link,
        "seeking_talent": sql_data.seeking_talent,
        "seeking_description": sql_data.seeking_description,
        "image_link": sql_data.image_link,
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": sql_data.past_shows_count,
        "upcoming_shows_count": sql_data.upcoming_shows_count
    }

    parse_genres(venue["genres"])

    return render_template('pages/show_venue.html', venue=venue)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    data = request.form

    try:
        venue = Venue(name=data['name'], city=data['city'], state=data['state'],
                      address=data['address'], phone=data['phone'], genres=data.getlist('genres'),
                      facebook_link=data['facebook_link'])
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + data['name'] + ' could not be listed.')
    else:
        # on successful db insert, flash success
        flash('Venue ' + data['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('venues'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = []
    sql_data = Artist.query.all()

    for row in sql_data:
        data.append({
            "id": row.id,
            "name": row.name
        })
    pass

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    sql_data = Artist.query.filter(Artist.name.contains(request.form.get('search_term', ''))).all()

    response = {
        "count": 1,
        "data": []
    }

    for result in sql_data:
        response["data"].append({
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": result.upcoming_shows_count,
        })
    pass

    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/None')
def ignore_null_artist_route():
    """
    Needed since calls to this route were producing errors.
    """
    return {}


@app.route('/artists/<artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    sql_data = Artist.query.get(artist_id)

    artist = {
        "id": sql_data.id,
        "name": sql_data.name,
        "genres": [],
        "city": sql_data.city,
        "state": sql_data.state,
        "phone": sql_data.phone,
        "website": sql_data.website,
        "facebook_link": sql_data.facebook_link,
        "seeking_venue": sql_data.seeking_venue,
        "seeking_description": sql_data.seeking_description,
        "image_link": sql_data.image_link,
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": sql_data.past_shows_count,
        "upcoming_shows_count": sql_data.upcoming_shows_count
    }

    parse_genres(artist["genres"])

    return render_template('pages/show_artist.html', artist=artist)


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    try:
        artist = Artist.query.get(artist_id)
        db.session.delete(artist)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('artists'))


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    sql_data = Artist.query.get(artist_id)

    artist = {
        "id": sql_data.id,
        "name": sql_data.name,
        "genres": sql_data.genres,
        "city": sql_data.city,
        "state": sql_data.state,
        "phone": sql_data.phone,
        "website": sql_data.website,
        "facebook_link": sql_data.facebook_link,
        "seeking_venue": sql_data.seeking_venue,
        "seeking_description": sql_data.seeking_description,
        "image_link": sql_data.image_link
    }

    form = ArtistForm(genres=artist["genres"])

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    data = request.form

    try:
        artist = Artist.query.get(artist_id)
        artist.name = data["name"]
        artist.city = data["city"]
        artist.state = data["state"]
        artist.address = data["address"]
        artist.phone = data["phone"]
        artist.genres = data.getlist("genres")
        artist.facebook_link = data["facebook_link"]
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        # on unsuccessful db update, flash an error instead.
        flash('An error occurred. Artist ' + data['name'] + ' could not be updated.')
    else:
        # on successful db update, flash success
        flash('Artist ' + data['name'] + ' was successfully updated!')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    sql_data = Venue.query.get(venue_id)

    venue = {
        "id": sql_data.id,
        "name": sql_data.name,
        "genres": sql_data.genres,
        "address": sql_data.address,
        "city": sql_data.city,
        "state": sql_data.state,
        "phone": sql_data.phone,
        "website": sql_data.website,
        "facebook_link": sql_data.facebook_link,
        "seeking_talent": sql_data.seeking_talent,
        "seeking_description": sql_data.seeking_description,
        "image_link": sql_data.image_link
    }

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    data = request.form

    try:
        venue = Venue.query.get(venue_id)
        venue.name = data["name"]
        venue.city = data["city"]
        venue.state = data["state"]
        venue.address = data["address"]
        venue.phone = data["phone"]
        venue.genres = data.getlist("genres")
        venue.facebook_link = data["facebook_link"]
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        # on unsuccessful db update, flash an error instead.
        flash('An error occurred. Venue ' + data['name'] + ' could not be updated.')
    else:
        # on successful db update, flash success
        flash('Venue ' + data['name'] + ' was successfully updated!')

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
    error = False
    data = request.form

    try:
        artist = Artist(name=data['name'], city=data['city'],
                        state=data['state'], phone=data['phone'], genres=data.getlist('genres'),
                        facebook_link=data['facebook_link'])
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Artist ' + data['name'] + ' could not be listed.')
    else:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    data = []

    for show_data in Show.query.all():
        show = {
            "id": show_data.id,
            "venue_id": show_data.venue_id,
            "venue_name": show_data.venue_name,
            "artist_id": show_data.artist_id,
            "artist_name": show_data.artist_name,
            "artist_image_link": show_data.artist_image_link,
            "start_time": show_data.start_time
        }

        data.append(show)
    pass

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    error = False
    data = request.form

    try:
        show = Show(artist_id=data['artist_id'], venue_id=data['venue_id'], start_time=data['start_time'])
        artist = Artist.query.get(show.artist_id)
        venue = Venue.query.get(show.venue_id)

        show.artist_name = artist.name
        show.artist_image_link = artist.image_link
        show.venue_name = venue.name

        if datetime.strptime(show.start_time, "%Y-%m-%dT%H:%M") >= datetime.now():
            artist.upcoming_shows.append(show)
            if artist.upcoming_shows_count is None:
                artist.upcoming_shows_count = 1
            else:
                artist.upcoming_shows_count += 1

            venue.upcoming_shows.append(show)
            if venue.upcoming_shows_count is None:
                venue.upcoming_shows_count = 1
            else:
                venue.upcoming_shows_count += 1
        else:
            artist.past_shows.append(show)
            if artist.past_shows_count is None:
                artist.past_shows_count = 1
            else:
                artist.past_shows_count += 1

            venue.past_shows.append(show)
            if venue.past_shows_count is None:
                venue.past_shows_count = 1
            else:
                venue.past_shows_count += 1

        db.session.add(show)
        db.session.add(artist)
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show could not be listed.')
    else:
        # on successful db insert, flash success
        flash('Show was successfully listed!')

    return render_template('pages/home.html')


@app.route('/shows/<int:show_id>', methods=['DELETE'])
def delete_show(show_id):
    try:
        show = Show.query.get(show_id)
        artist = Artist.query.get(show.artist_id)
        venue = Venue.query.get(show.venue_id)

        if artist.upcoming_shows.__contains__(show):
            artist.upcoming_shows.remove(show)
            artist.upcoming_shows_count -= 1
        elif artist.past_shows.__contains__(show):
            artist.past_shows.remove(show)
            artist.past_shows_count -= 1

        if venue.upcoming_shows.__contains__(show):
            venue.upcoming_shows.remove(show)
            venue.upcoming_shows_count -= 1
        elif venue.past_shows.__contains__(show):
            venue.past_shows.remove(show)
            venue.past_shows_count -= 1

        db.session.delete(show)
        db.session.add(artist)
        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('shows'))


# Utilities
# ===========================================================

def parse_genres(genre_list):
    """
    Will parse the genre SQL Array into a list of Python strings
    :param genre_list: the list of genres given
    :return: true if no error, false if there was an error
    """
    error = False

    try:
        token_builder = ""
        for genre_char in genre_list:
            if genre_char == "{":
                continue
            elif genre_char == "}" and token_builder != "":
                genre_list.append(token_builder)
            elif genre_char == ",":
                genre_list.append(token_builder)
                token_builder = ""
            else:
                token_builder = token_builder + genre_char
            pass
        pass
    except:
        error = True

    return not error


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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#


def run(port=""):
    if not port:
        # Default port:
        app.run()
    else:
        # Or specify port manually:
        app.run(host='0.0.0.0', port=port)


if __name__ == "__main__":
    run()
