from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from bson.objectid import ObjectId
import time

from app import db

announcements_bp = Blueprint('student_announcements', __name__, url_prefix='/student/announcements')

@announcements_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_announcements():
    """Get all announcements with optional filtering and pagination."""
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    skip = (page - 1) * per_page
    
    # Get filter parameters
    important_only = request.args.get('important', '').lower() == 'true'
    date_after = request.args.get('date_after')
    
    # Build query
    query = {}
    if important_only:
        query['important'] = True
    if date_after:
        try:
            date_after_timestamp = float(date_after)
            query['date'] = {'$gte': date_after_timestamp}
        except ValueError:
            pass
    
    # Get total count
    total = db.announcements.count_documents(query)
    
    # Get announcements
    announcements = list(db.announcements.find(query).sort('date', -1).skip(skip).limit(per_page))
    
    # Convert ObjectId to string for JSON serialization
    for announcement in announcements:
        announcement['_id'] = str(announcement['_id'])
    
    return jsonify({
        'announcements': announcements,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }), 200

@announcements_bp.route('/<announcement_id>', methods=['GET'])
@jwt_required()
def get_announcement(announcement_id):
    """Get a specific announcement by ID."""
    try:
        # Validate the ObjectId format
        if not ObjectId.is_valid(announcement_id):
            return jsonify({'error': 'Invalid announcement ID format'}), 400
        
        # Find the announcement
        announcement = db.announcements.find_one({'_id': ObjectId(announcement_id)})
        
        if not announcement:
            return jsonify({'error': 'Announcement not found'}), 404
        
        # Convert ObjectId to string for JSON serialization
        announcement['_id'] = str(announcement['_id'])
        
        return jsonify({
            'announcement': announcement
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@announcements_bp.route('/recent', methods=['GET'])
@jwt_required()
def get_recent_announcements():
    """Get recent announcements (last 30 days by default)."""
    # Get the number of days to look back
    days = int(request.args.get('days', 30))
    limit = int(request.args.get('limit', 5))
    
    # Calculate the timestamp for the specified number of days ago
    cutoff_date = time.time() - (days * 24 * 60 * 60)
    
    # Get announcements newer than the cutoff date
    announcements = list(db.announcements.find({
        'date': {'$gte': cutoff_date}
    }).sort('date', -1).limit(limit))
    
    # Convert ObjectId to string for JSON serialization
    for announcement in announcements:
        announcement['_id'] = str(announcement['_id'])
    
    return jsonify({
        'announcements': announcements,
        'count': len(announcements)
    }), 200

@announcements_bp.route('/important', methods=['GET'])
@jwt_required()
def get_important_announcements():
    """Get important announcements."""
    limit = int(request.args.get('limit', 5))
    
    # Get important announcements
    announcements = list(db.announcements.find({
        'important': True
    }).sort('date', -1).limit(limit))
    
    # Convert ObjectId to string for JSON serialization
    for announcement in announcements:
        announcement['_id'] = str(announcement['_id'])
    
    return jsonify({
        'announcements': announcements,
        'count': len(announcements)
    }), 200 