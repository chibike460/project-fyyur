from flask import Blueprint, jsonify, render_template, request, flash, url_for, redirect
from models import Venue, Show, Artist
from datetime import datetime
from app import db
from forms import ArtistForm
import sys


'''
Define the blueprint: 'artists'
'''
artist_bp = Blueprint('artist', __name__, template_folder='templates')


'''
Lists Artists
'''
@artist_bp.route('/')
def artists():
    return render_template('pages/artists.html', artists=Artist.query.all())


'''
Functionality to search for artists
'''
@artist_bp.route('/search', methods=['POST'])
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


'''
Artist page
'''
@artist_bp.route('/<int:artist_id>')
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

'''
Form to add new artists
'''

@artist_bp.route('/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm(csrf_enabled=False)
    return render_template('forms/new_artist.html', form=form)


'''
Sumit form to add new artists
'''
@artist_bp.route('/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(csrf_enabled=False)
    if form.validate_on_submit():
        artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            genres=form.genres.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            website_link=form.website_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data)
        db.session.add(artist)
        db.session.commit()
        db.session.close()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return redirect(url_for('artist.artists'))
    else:
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
        print(form.errors)
        return render_template('forms/new_artist.html', form=form)