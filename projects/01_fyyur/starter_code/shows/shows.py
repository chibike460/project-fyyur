from flask import Blueprint, jsonify, render_template, request, flash, url_for, redirect
from models import Venue, Show, Artist
from datetime import datetime
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