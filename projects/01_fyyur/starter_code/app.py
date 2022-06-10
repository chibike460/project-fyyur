# IMPORTS

import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
)
from models import setup_db, Venue, Artist, db
from flask_moment import Moment
from flask_migrate import Migrate
from flask_cors import CORS
import logging
from logging import (
    Formatter,
    FileHandler
)
from forms import *
import sys
from venues.venues import venue_bp
from artists.artists import artist_bp
from shows.shows import show_bp


'''
Factory function to create the app
'''
def create_app(test_config=None):

    # APP CONFIG
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    moment = Moment(app)
    migrate = Migrate(app, db)

    # CORS SETUP

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

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

    #  BLUEPRINTS

    app.register_blueprint(venue_bp, url_prefix='/venues')
    app.register_blueprint(artist_bp, url_prefix='/artists')
    app.register_blueprint(show_bp, url_prefix='/shows')


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
    # if __name__ == '__main__':
    #     app.run(debug=True)

    # Or specify port manually:
    '''
    if __name__ == '__main__':
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
    '''
    return app
