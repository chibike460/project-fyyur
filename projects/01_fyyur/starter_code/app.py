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
from models import setup_db, Venue, Artist, Show, db
from flask_moment import Moment
# from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import (
    Formatter,
    FileHandler
)
from forms import *
import sys
from venues.venues import venue_bp
from artists.artists import artist_bp

app = Flask(__name__)
setup_db(app)
# db = SQLAlchemy(app)

# APP CONFIG


moment = Moment(app)
# app.config.from_object('config')
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

app.register_blueprint(venue_bp, url_prefix='/venues')
app.register_blueprint(artist_bp, url_prefix='/artists')

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
