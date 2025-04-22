from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from bson.objectid import ObjectId

from app import db

announcement_bp = Blueprint('announcement', __name__)

@announcement_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_announcements():
    """Get all announcements."""
    announcements = list(db.announcements.find().sort('date', -1))
    
    # Convert ObjectId to string for JSON serialization
    for announcement in announcements:
        announcement['_id'] = str(announcement['_id'])
    
    return jsonify({
        'announcements': announcements
    }), 200

@announcement_bp.route('/<announcement_id>', methods=['GET'])
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