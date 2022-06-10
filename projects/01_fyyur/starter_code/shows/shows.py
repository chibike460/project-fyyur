from flask import Blueprint, jsonify, render_template, request, flash, abort
from models import Show
from app import db
from forms import ShowForm
import sys


'''
Define the blueprint: 'shows'
'''
show_bp = Blueprint('show', __name__, template_folder='templates')


'''
Lists Shows
'''
@show_bp.route('/')
def shows():
    return render_template('pages/shows.html', shows=Show.query.all())


'''
Form to create a new show
'''
@show_bp.route('/create')
def create_shows():
    form = ShowForm(csrf_enabled=False)
    return render_template('forms/new_show.html', form=form)


'''
Submit form to create a new show
'''
@show_bp.route('/create', methods=['POST'])
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