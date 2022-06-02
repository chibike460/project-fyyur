# IMPORTS

import dateutil.parser
import babel
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
    abort
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import (
    Formatter,
    FileHandler
)
from forms import *
import sys

app = Flask(__name__)
db = SQLAlchemy(app)
from models import *
# APP CONFIG


moment = Moment(app)
app.config.from_object('config')
migrate = Migrate(app, db)

# FILTERS


def format_datetime(value, format='medium'):
    if isinstance(value, datetime):
        value = value.strftime('%Y-%m-%d %H:%M:%S')
        date = dateutil.parser.parse(value, ignoretz=True)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# CONTROLLERS


@app.route('/')
def index():
    recent_artists = Artist.query.order_by(Artist.id.desc()).limit(3).all()
    recent_venues = Venue.query.order_by(Venue.id.desc()).limit(3).all()
    return render_template(
        'pages/home.html',
        artists=recent_artists,
        venues=recent_venues)

#  VENUES


@app.route('/venues')
def venues():
    return render_template('pages/venues.html', venues=Venue.query.all())


@app.route('/venues/search', methods=['POST'])
def search_venues():
    venues = Venue.query.filter(
        Venue.name.ilike(
            "%" +
            request.form.get('search_term') +
            '%')).all()
    count_venues = len(venues)
    response = {
        "count": count_venues,
        "data": venues
    }
    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    date_today = datetime.now()
    venue = Venue.query.get(venue_id)
    upcoming_shows = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id).filter(
        Show.start_time > date_today).all()
    past_shows = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id).filter(
        Show.start_time < date_today).all()
    return render_template(
        'pages/show_venue.html',
        venue=venue,
        upcoming_shows=upcoming_shows,
        past_shows=past_shows)

#  CREATE VENUES


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm(csrf_enabled=False)
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(csrf_enabled=False)
    error = False
    if form.validate_on_submit():
        try:
            name = form.name.data
            city = form.city.data
            state = form.state.data
            address = form.address.data
            phone = form.phone.data
            image_link = form.image_link.data
            genres = form.genres.data
            facebook_link = form.facebook_link.data
            website_link = form.website_link.data
            seeking_talent = form.seeking_talent.data
            seeking_description = form.seeking_description.data
            venues = Venue(
                name=name,
                city=city,
                state=state,
                address=address,
                phone=phone,
                image_link=image_link,
                genres=genres,
                facebook_link=facebook_link,
                website_link=website_link,
                seeking_talent=seeking_talent,
                seeking_description=seeking_description)
            db.session.add(venues)
            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
        except BaseException:
            error = True
            db.session.rollback()
            flash('An error occurred. Venue ' + request.form['name']
                  + ' could not be listed.')
            print(sys.exc_info())
        finally:
            db.session.close()
    if error:
        print(sys.exc_info())
        abort(400)
    else:
        return render_template('pages/home.html')

# UPDATE VENUES


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm(obj=Venue.query.get(venue_id))
    return render_template(
        'forms/edit_venue.html',
        form=form,
        venue=Venue.query.get(venue_id))


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(csrf_enabled=False)
    venue = Venue.query.get(venue_id)
    error = False
    if form.validate_on_submit():
        try:
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.phone = form.phone.data
            venue.image_link = form.image_link.data
            venue.genres = form.genres.data
            venue.facebook_link = form.facebook_link.data
            venue.website_link = form.website_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
        except BaseException:
            error = True
            db.session.rollback()
            flash(
                'An error occurred. Venue ' +
                request.form['name'] +
                ' could not be listed.')
            print(sys.exc_info())
    if error:
        print(sys.exc_info())
        abort(400)
    else:
        return redirect(url_for('show_venue', venue_id=venue.id))

# DELETE VENUES


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error: False
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except BaseException:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        print(sys.exc_info())
        abort(500)
    else:
        return jsonify({'success': True})

#  ARTISTS


@app.route('/artists')
def artists():
    return render_template('pages/artists.html', artists=Artist.query.all())


@app.route('/artists/search', methods=['POST'])
def search_artists():
    artists = Artist.query.filter(
        Artist.name.ilike(
            "%" +
            request.form.get('search_term') +
            '%')).all()
    count_artists = len(artists)
    response = {
        "count": count_artists,
        "data": artists
    }
    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    date_today = datetime.now()
    artist = Artist.query.get(artist_id)
    upcoming_shows = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).filter(
        Show.start_time > date_today).all()
    upcoming_shows = [
        show for show in upcoming_shows if len(
            show.venue.name) > 0]
    past_shows = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).filter(
        Show.start_time > date_today).all()
    past_shows = [show for show in past_shows if len(show.venue.name) > 0]
    return render_template(
        'pages/show_artist.html',
        artist=artist,
        past_shows=past_shows,
        upcoming_shows=upcoming_shows)

#  CREATE ARTISTS


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm(csrf_enabled=False)
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(csrf_enabled=False)
    error = False
    if form.validate_on_submit():
        try:
            name = form.name.data
            city = form.city.data
            state = form.state.data
            phone = form.phone.data
            image_link = form.image_link.data
            genres = form.genres.data
            facebook_link = form.facebook_link.data
            website_link = form.website_link.data
            seeking_venue = form.seeking_venue.data
            seeking_description = form.seeking_description.data
            artists = Artist(
                name=name,
                city=city,
                state=state,
                phone=phone,
                image_link=image_link,
                genres=genres,
                facebook_link=facebook_link,
                website_link=website_link,
                seeking_venue=seeking_venue,
                seeking_description=seeking_description)
            db.session.add(artists)
            db.session.commit()
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')
        except BaseException:
            error = True
            db.session.rollback()
            flash('An error occurred. Artist ' + request.form['name'] +
                  ' could not be listed.')
            print(sys.exc_info())
        finally:
            db.session.close()
    if error:
        print(sys.exc_info())
        abort(400)
    else:
        return render_template('pages/home.html')


#  UPDATE ARTISTS

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm(obj=Artist.query.get(artist_id))
    return render_template(
        'forms/edit_artist.html',
        form=form,
        artist=Artist.query.get(artist_id))


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(csrf_enabled=False)
    artist = Artist.query.get(artist_id)
    if form.validate_on_submit():
        error = False
        try:
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.image_link = form.image_link.data
            artist.genres = form.genres.data
            artist.facebook_link = form.facebook_link.data
            artist.website_link = form.website_link.data
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data
            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
        except BaseException:
            error = True
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Venue ' + request.form['name'] +
                  ' could not be listed.')
        if error:
            print(sys.exc_info())
            abort(400)
        else:
            return redirect(url_for('show_artist', artist_id=artist.id))

# DELETE ARTISTS


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    error: False
    try:
        artist = Artist.query.get(artist_id)
        db.session.delete(artist)
        db.session.commit()
    except BaseException:
        error = True
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        print(sys.exc_info())
        abort(500)
    else:
        return jsonify({'success': True})

#  SHOWS


@app.route('/shows')
def shows():
    return render_template('pages/shows.html', shows=Show.query.all())


@app.route('/shows/create')
def create_shows():
    form = ShowForm(csrf_enabled=False)
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(csrf_enabled=False)
    error = False
    if form.validate_on_submit():
        try:
            venue_id = form.venue_id.data
            artist_id = form.artist_id.data
            start_time = form.start_time.data
            show = Show(
                venue_id=venue_id,
                artist_id=artist_id,
                start_time=start_time)
            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
        except BaseException:
            error = True
            db.session.rollback()
            flash('An error occurred. Show could not be listed.')
            print(sys.exc_info())
        finally:
            db.session.close()
    if error:
        print(sys.exc_info())
        abort(400)
    else:
        return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

@app.errorhandler(405)
def invalid_method(error):
    return render_template('errors/405.html'), 405

@app.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(401)
def unauthorized(error):
    return render_template('errors/401.html'), 401



if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# Launch.

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
