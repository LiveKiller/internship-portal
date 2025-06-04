from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.auth.utils import user_to_json, get_user_role
from app.auth.role_required import role_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    """
    Get role-specific dashboard data for the current user.
    Route automatically serves appropriate data based on user role.
    """
    identity = get_jwt_identity()
    role = get_user_role(identity)
    
    if role == 'student':
        return get_student_dashboard(identity)
    elif role == 'faculty':
        return get_faculty_dashboard(identity)
    elif role == 'admin':
        return get_admin_dashboard(identity)
    else:
        return jsonify({
            'error': 'User role not found or unauthorized'
        }), 403

def get_student_dashboard(student_id):
    """Get dashboard data for student users."""
    # Get user data
    user = db.students.find_one({'registration_no': student_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get announcements (most recent 5)
    announcements = list(db.announcements.find().sort('date', -1).limit(5))
    for announcement in announcements:
        announcement['_id'] = str(announcement['_id'])
    
    # Get unread messages count
    unread_messages = db.messages.count_documents({
        'recipient_id': student_id,
        'read': False
    })
    
    # Get upcoming interview count
    upcoming_interviews = db.interviews.count_documents({
        'student_id': student_id,
        'status': 'scheduled'
    })
    
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

def get_faculty_dashboard(faculty_id):
    """Get dashboard data for faculty users."""
    # Get faculty data
    faculty = db.faculty.find_one({'faculty_id': faculty_id})
    if not faculty:
        return jsonify({'error': 'Faculty not found'}), 404
    
    # Convert to JSON-serializable format
    faculty_data = user_to_json(faculty)
    
    # Get recent announcements (most recent 5)
    announcements = list(db.announcements.find().sort('date', -1).limit(5))
    for announcement in announcements:
        announcement['_id'] = str(announcement['_id'])
    
    # Get student statistics
    total_students = db.students.count_documents({})
    placed_students = db.students.count_documents({'placed': True})
    
    # Get company statistics
    active_companies = db.companies.count_documents({'active': True})
    
    return jsonify({
        'user': faculty_data,
        'recent_announcements': announcements,
        'stats': {
            'total_students': total_students,
            'placed_students': placed_students,
            'placement_percentage': round(placed_students / total_students * 100, 2) if total_students > 0 else 0,
            'active_companies': active_companies
        }
    }), 200

def get_admin_dashboard(admin_id):
    """Get dashboard data for admin users."""
    # Get admin data
    admin = db.admin.find_one({'admin_id': admin_id})
    if not admin:
        return jsonify({'error': 'Admin not found'}), 404
    
    # Convert to JSON-serializable format
    admin_data = user_to_json(admin)
    
    # Get system statistics
    total_students = db.students.count_documents({})
    placed_students = db.students.count_documents({'placed': True})
    total_companies = db.companies.count_documents({})
    active_companies = db.companies.count_documents({'active': True})
    total_faculty = db.faculty.count_documents({})
    
    return jsonify({
        'user': admin_data,
        'stats': {
            'total_students': total_students,
            'placed_students': placed_students,
            'placement_percentage': round(placed_students / total_students * 100, 2) if total_students > 0 else 0,
            'total_companies': total_companies,
            'active_companies': active_companies,
            'total_faculty': total_faculty
        }
    }), 200

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get only the dashboard statistics based on user role."""
    identity = get_jwt_identity()
    role = get_user_role(identity)
    
    if role == 'student':
        return get_student_stats(identity)
    elif role == 'faculty':
        return get_faculty_stats(identity)
    elif role == 'admin':
        return get_admin_stats(identity)
    else:
        return jsonify({
            'error': 'User role not found or unauthorized'
        }), 403

def get_student_stats(student_id):
    """Get dashboard statistics for student users."""
    # Get user data
    user = db.students.find_one({'registration_no': student_id})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get unread messages count
    unread_messages = db.messages.count_documents({
        'recipient_id': student_id,
        'read': False
    })
    
    # Get upcoming interview count
    upcoming_interviews = db.interviews.count_documents({
        'student_id': student_id,
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

def get_faculty_stats(faculty_id):
    """Get dashboard statistics for faculty users."""
    # Get student statistics
    total_students = db.students.count_documents({})
    placed_students = db.students.count_documents({'placed': True})
    
    # Get company statistics
    active_companies = db.companies.count_documents({'active': True})
    
    return jsonify({
        'stats': {
            'total_students': total_students,
            'placed_students': placed_students,
            'placement_percentage': round(placed_students / total_students * 100, 2) if total_students > 0 else 0,
            'active_companies': active_companies
        }
    }), 200

def get_admin_stats(admin_id):
    """Get dashboard statistics for admin users."""
    # Get system statistics
    total_students = db.students.count_documents({})
    placed_students = db.students.count_documents({'placed': True})
    total_companies = db.companies.count_documents({})
    active_companies = db.companies.count_documents({'active': True})
    total_faculty = db.faculty.count_documents({})
    
    return jsonify({
        'stats': {
            'total_students': total_students,
            'placed_students': placed_students,
            'placement_percentage': round(placed_students / total_students * 100, 2) if total_students > 0 else 0,
            'total_companies': total_companies,
            'active_companies': active_companies,
            'total_faculty': total_faculty
        }
    }), 200 