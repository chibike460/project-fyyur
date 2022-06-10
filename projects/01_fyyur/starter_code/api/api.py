from flask import Blueprint, jsonify, render_template, request, flash, url_for, redirect
from models import Venue

'''
Define the blueprint: 'api'
'''
api_bp = Blueprint('api', __name__)


'''
Lists Venues
'''
@api_bp.route('/venues')
def get_venues():
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * 10
    end = start + 10
    venues = Venue.query.order_by(Venue.id.desc()).all()
    formated_venues = [venue.format() for venue in venues]
    return jsonify(
        {
            'success': True,
            'data': formated_venues[start:end],
            'total_venues': len(formated_venues)
        }
    )