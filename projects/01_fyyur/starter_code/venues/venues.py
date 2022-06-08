from flask import Blueprint, jsonify, render_template, request, flash, url_for, redirect
from models import Venue, Show, Artist
from datetime import datetime
from app import db
from forms import VenueForm
import sys


'''
Define the blueprint: 'venues'
'''
venue_bp = Blueprint('venue', __name__, template_folder='templates')


'''
Lists Venues.
'''
@venue_bp.route('/')
def venues():
    return render_template('pages/venues.html', venues=Venue.query.all())


'''
Functionality to search for venues
'''
@venue_bp.route('/search', methods=['POST'])
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


'''
Venue page
'''
@venue_bp.route('/<int:venue_id>')
def show_venue(venue_id):
    date_today = datetime.now()
    venue = Venue.query.get(venue_id)
    upcoming_shows = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id).filter(
        Show.start_time > date_today).all()
    upcoming_shows = [show for show in upcoming_shows if len(show.venue.name) > 0]
    past_shows = db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id).filter(
        Show.start_time < date_today).all()
    past_shows = [show for show in past_shows if len(show.venue.name) > 0]
    return render_template(
        'pages/show_venue.html',
        venue=venue,
        upcoming_shows=upcoming_shows,
        past_shows=past_shows)


'''
Form to add new venues
'''
@venue_bp.route('/create', methods=['GET'])
def create_venue_form():
    form = VenueForm(csrf_enabled=False)
    return render_template('forms/new_venue.html', form=form)


'''
Submit form to add new venues
'''
@venue_bp.route('/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(csrf_enabled=False)
    if form.validate_on_submit():
        vanue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data)
        db.session.add(vanue)
        db.session.commit()
        db.session.close()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return redirect(url_for('venue.venues'))
    else:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        print(form.errors)
        return render_template('forms/new_venue.html', form=form)


# '''
# Form to edit venues
# '''
# @venue_bp.route('/venues/<int:venue_id>/edit', methods=['GET'])
# def edit_venue(venue_id):
#     form = VenueForm(csrf_enabled=False)
#     venue = Venue.query.get(venue_id)
#     form.name.data = venue.name
#     form.city.data = venue.city
#     form.state.data = venue.state
#     form.address.data = venue.address
#     form.phone.data = venue.phone
#     form.genres.data = venue.genres
#     form.image_link.data = venue.image_link
#     form.facebook_link.data = venue.facebook_link
#     form.website_link.data = venue.website_link
#     form.seeking_talent.data = venue.seeking_talent
#     form.seeking_description.data = venue.seeking_description
#     return render_template(
#         'forms/edit_venue.html',
#         form=form,
#         venue=venue)


# '''
# Update venue
# '''
# @venue_bp.route('/venues/<int:venue_id>/edit', methods=['POST'])
# def edit_venue_submission(venue_id):
#     form = VenueForm(csrf_enabled=False)
#     if form.validate_on_submit():
#         venue = Venue.query.get(venue_id)
#         venue.name = form.name.data
#         venue.city = form.city.data
#         venue.state = form.state.data
#         venue.address = form.address.data
#         venue.phone = form.phone.data
#         venue.genres = form.genres.data
#         venue.image_link = form.image_link.data
#         venue.facebook_link = form.facebook_link.data
#         venue.website_link = form.website_link.data
#         venue.seeking_talent = form.seeking_talent.data
#         venue.seeking_description = form.seeking_description.data
#         db.session.commit()
#         flash('Venue ' + request.form['name'] +
#               ' was successfully updated!')
#         db.session.close()
#         return redirect(url_for('show_venue', venue_id=venue_id))
#     else:
#         print(sys.exc_info())
#         db.session.rollback()
#         flash('An error occurred. Venue ' + request.form['name']
#               + ' could not be updated.')
#         db.session.close()
#         return render_template('forms/edit_venue.html', form=form)


# '''
# Delete venue
# '''
# @venue_bp.route('/venues/<int:venue_id>/delete', methods=['DELETE'])
# def delete_venue(venue_id):
#     error = False
#     try:
#         venue = Venue.query.get(venue_id)
#         db.session.delete(venue)
#         db.session.commit()
#         flash('Venue ' + venue.name + ' was successfully deleted!')
#         db.session.close()
#     except BaseException:
#         error = True
#         db.session.rollback()
#         print(sys.exc_info())
#         flash('An error occurred. Venue ' + venue.name +
#               ' could not be deleted.')
#     finally:
#         db.session.close()
#         return jsonify({'success': True})