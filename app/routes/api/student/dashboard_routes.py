from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import time

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
    
    # Get active companies count
    active_companies = db.companies.count_documents({
        'active': True
    })
    
    # Convert user to JSON-serializable format
    user_data = user_to_json(user)
    
    return jsonify({
        'user': user_data,
        'recent_announcements': announcements,
        'stats': {
            'unread_messages': unread_messages,
            'upcoming_interviews': upcoming_interviews,
            'active_companies': active_companies,
            'applied_companies': len(user.get('companies', {}).get('applied', [])),
            'rejected_companies': len(user.get('companies', {}).get('rejected', [])),
            'interviews_attended': len(user.get('companies', {}).get('interviews_attended', [])),
            'interviews_not_attended': len(user.get('companies', {}).get('interviews_not_attended', []))
        }
    }), 200

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get only the dashboard statistics."""
    current_user = get_jwt_identity()
    
    # Get user data
    user = db.students.find_one({'registration_no': current_user})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
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
    
    # Get active companies count
    active_companies = db.companies.count_documents({
        'active': True
    })
    
    # Get application status counts
    applied_companies = len(user.get('companies', {}).get('applied', []))
    rejected_companies = len(user.get('companies', {}).get('rejected', []))
    interviews_attended = len(user.get('companies', {}).get('interviews_attended', []))
    interviews_not_attended = len(user.get('companies', {}).get('interviews_not_attended', []))
    
    return jsonify({
        'stats': {
            'unread_messages': unread_messages,
            'upcoming_interviews': upcoming_interviews,
            'active_companies': active_companies,
            'applied_companies': applied_companies,
            'rejected_companies': rejected_companies,
            'interviews_attended': interviews_attended,
            'interviews_not_attended': interviews_not_attended
        }
    }), 200

@dashboard_bp.route('/upcoming-deadlines', methods=['GET'])
@jwt_required()
def get_upcoming_deadlines():
    """Get upcoming application deadlines."""
    # Get limit parameter
    limit = int(request.args.get('limit', 5))
    
    # Current time
    current_time = time.time()
    
    # Get companies with upcoming deadlines
    companies = list(db.companies.find({
        'active': True,
        'deadline': {'$gt': current_time}
    }).sort('deadline', 1).limit(limit))
    
    # Convert ObjectId to string for JSON serialization
    for company in companies:
        company['_id'] = str(company['_id'])
    
    return jsonify({
        'companies': companies,
        'count': len(companies)
    }), 200
