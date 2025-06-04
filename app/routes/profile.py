from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId

from app import db
from app.auth.utils import user_to_json, get_user_role
from app.auth.role_required import role_required

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get profile data for the current user based on their role.
    """
    identity = get_jwt_identity()
    role = get_user_role(identity)
    
    if role == 'student':
        return get_student_profile(identity)
    elif role == 'faculty':
        return get_faculty_profile(identity)
    elif role == 'admin':
        return get_admin_profile(identity)
    else:
        return jsonify({
            'error': 'User role not found or unauthorized'
        }), 403

def get_student_profile(student_id):
    """Get profile data for student users."""
    # Get user data
    student = db.students.find_one({'registration_no': student_id})
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Convert to JSON-serializable format
    student_data = user_to_json(student)
    
    return jsonify({
        'profile': student_data
    }), 200

def get_faculty_profile(faculty_id):
    """Get profile data for faculty users."""
    # Get faculty data
    faculty = db.faculty.find_one({'faculty_id': faculty_id})
    if not faculty:
        return jsonify({'error': 'Faculty not found'}), 404
    
    # Convert to JSON-serializable format
    faculty_data = user_to_json(faculty)
    
    return jsonify({
        'profile': faculty_data
    }), 200

def get_admin_profile(admin_id):
    """Get profile data for admin users."""
    # Get admin data
    admin = db.admin.find_one({'admin_id': admin_id})
    if not admin:
        return jsonify({'error': 'Admin not found'}), 404
    
    # Convert to JSON-serializable format
    admin_data = user_to_json(admin)
    
    return jsonify({
        'profile': admin_data
    }), 200

@profile_bp.route('/', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update profile data for the current user based on their role.
    """
    identity = get_jwt_identity()
    role = get_user_role(identity)
    
    if role == 'student':
        return update_student_profile(identity)
    elif role == 'faculty':
        return update_faculty_profile(identity)
    elif role == 'admin':
        return update_admin_profile(identity)
    else:
        return jsonify({
            'error': 'User role not found or unauthorized'
        }), 403

def update_student_profile(student_id):
    """Update profile data for student users."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Get the current student data
    student = db.students.find_one({'registration_no': student_id})
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Fields that are not allowed to be updated
    protected_fields = ['_id', 'registration_no', 'email', 'password', 'role']
    
    # Remove protected fields from the update data
    update_data = {k: v for k, v in data.items() if k not in protected_fields}
    
    # Update the student profile
    result = db.students.update_one(
        {'registration_no': student_id},
        {'$set': update_data}
    )
    
    if result.modified_count:
        # Get the updated student data
        updated_student = db.students.find_one({'registration_no': student_id})
        student_data = user_to_json(updated_student)
        
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': student_data
        }), 200
    else:
        return jsonify({
            'message': 'No changes were made to the profile'
        }), 200

def update_faculty_profile(faculty_id):
    """Update profile data for faculty users."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Get the current faculty data
    faculty = db.faculty.find_one({'faculty_id': faculty_id})
    if not faculty:
        return jsonify({'error': 'Faculty not found'}), 404
    
    # Fields that are not allowed to be updated
    protected_fields = ['_id', 'faculty_id', 'email', 'password', 'role']
    
    # Remove protected fields from the update data
    update_data = {k: v for k, v in data.items() if k not in protected_fields}
    
    # Update the faculty profile
    result = db.faculty.update_one(
        {'faculty_id': faculty_id},
        {'$set': update_data}
    )
    
    if result.modified_count:
        # Get the updated faculty data
        updated_faculty = db.faculty.find_one({'faculty_id': faculty_id})
        faculty_data = user_to_json(updated_faculty)
        
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': faculty_data
        }), 200
    else:
        return jsonify({
            'message': 'No changes were made to the profile'
        }), 200

def update_admin_profile(admin_id):
    """Update profile data for admin users."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Get the current admin data
    admin = db.admin.find_one({'admin_id': admin_id})
    if not admin:
        return jsonify({'error': 'Admin not found'}), 404
    
    # Fields that are not allowed to be updated
    protected_fields = ['_id', 'admin_id', 'email', 'password', 'role']
    
    # Remove protected fields from the update data
    update_data = {k: v for k, v in data.items() if k not in protected_fields}
    
    # Update the admin profile
    result = db.admin.update_one(
        {'admin_id': admin_id},
        {'$set': update_data}
    )
    
    if result.modified_count:
        # Get the updated admin data
        updated_admin = db.admin.find_one({'admin_id': admin_id})
        admin_data = user_to_json(updated_admin)
        
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': admin_data
        }), 200
    else:
        return jsonify({
            'message': 'No changes were made to the profile'
        }), 200 