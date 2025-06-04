from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from app import db

def role_required(allowed_roles):
    """
    A decorator to protect routes based on user roles.
    
    Args:
        allowed_roles (list): List of role names that are allowed to access the route.
        
    Usage:
        @role_required(['student'])
        def student_route():
            pass
            
        @role_required(['admin', 'faculty'])
        def admin_route():
            pass
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verify JWT is present and valid
            verify_jwt_in_request()
            
            # Get the identity from JWT
            identity = get_jwt_identity()
            
            # Determine the user's role
            user_role = None
            
            # Check if user is in students collection
            student = db.students.find_one({'registration_no': identity})
            if student:
                user_role = 'student'
            
            # Check if user is in faculty collection
            if not user_role:
                faculty = db.faculty.find_one({'faculty_id': identity})
                if faculty:
                    user_role = 'faculty'
            
            # Check if user is in admin collection
            if not user_role:
                admin = db.admin.find_one({'admin_id': identity})
                if admin:
                    user_role = 'admin'
            
            # Check if user role is in allowed roles
            if not user_role or user_role not in allowed_roles:
                return jsonify({
                    'error': 'Unauthorized access. You do not have the required role to access this resource.'
                }), 403
            
            # User has required role, proceed with the route
            return fn(*args, **kwargs)
        
        return wrapper
    
    return decorator 