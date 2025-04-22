from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.auth.utils import user_to_json

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    """Get all user data for the dashboard."""
    current_user = get_jwt_identity()
    
    # Get user data
    user = db.students.find_one({'registration_no': current_user})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get announcements (most recent 5)
    announcements = list(db.announcements.find().sort('date', -1).limit(5))
    for announcement in announcements:
        announcement['_id'] = str(announcement['_id'])
    
    # Get unread messages count
    unread_messages = db.messages.count_documents({
        'recipient_id': current_user,
        'read': False
    })
    
    # Get upcoming interview count
    upcoming_interviews = db.interviews.count_documents({
        'student_id': current_user,
        'status': 'scheduled'
    })
    
    # Convert user to JSON-serializable format
    user_data = user_to_json(user)
    
    return jsonify({
        'user': user_data,
        'recent_announcements': announcements,
        'stats': {
            'unread_messages': unread_messages,
            'upcoming_interviews': upcoming_interviews,
            'applied_companies': len(user.get('companies', {}).get('applied', [])),
            'rejected_companies': len(user.get('companies', {}).get('rejected', [])),
            'interviews_attended': len(user.get('companies', {}).get('interviews_attended', [])),
            'interviews_not_attended': len(user.get('companies', {}).get('interviews_not_attended', []))
        }
    }), 200