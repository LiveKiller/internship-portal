import re
import bcrypt
from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from app import db

def hash_password(password):
    """Hash a password for storing."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def check_password(stored_password, provided_password):
    """Check hashed password against a provided password."""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

def validate_registration_number(reg_no):
    """Validate that a registration number matches the format 2X13XXXXX where X are integers."""
    return bool(re.match(r'^2\d13\d{5}$', reg_no))

def validate_email(email):
    """Validate that an email has a valid format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def get_current_user():
    """Get the current user from JWT identity."""
    identity = get_jwt_identity()
    
    # First check if user is a student
    user = db.students.find_one({'registration_no': identity})
    if user:
        return user, 'student'
    
    # Check if user is faculty
    user = db.faculty.find_one({'faculty_id': identity})
    if user:
        return user, 'faculty'
    
    # Check if user is admin
    user = db.admin.find_one({'admin_id': identity})
    if user:
        return user, 'admin'
    
    return None, None

def get_user_role(identity=None):
    """
    Get the role of a user based on their identity.
    
    Args:
        identity: The user's identity (registration_no, faculty_id, admin_id)
                 If None, uses the JWT identity.
    
    Returns:
        str: 'student', 'faculty', 'admin', or None if not found
    """
    if identity is None:
        identity = get_jwt_identity()
    
    # Check if user is a student
    student = db.students.find_one({'registration_no': identity})
    if student:
        return 'student'
    
    # Check if user is faculty
    faculty = db.faculty.find_one({'faculty_id': identity})
    if faculty:
        return 'faculty'
    
    # Check if user is admin
    admin = db.admin.find_one({'admin_id': identity})
    if admin:
        return 'admin'
    
    return None

def user_to_json(user):
    """Convert a user document to JSON-serializable format."""
    if user:
        # Create a copy of the user dictionary to avoid modifying the original
        user_copy = dict(user)
        
        # Convert MongoDB ObjectId to string
        if '_id' in user_copy:
            user_copy['_id'] = str(user_copy['_id'])
        
        # Handle binary password - we should not expose this in the API anyway
        if 'password' in user_copy:
            del user_copy['password']  # Remove password from the response
        
        # Check for other binary data or non-serializable types
        for key, value in list(user_copy.items()):
            if isinstance(value, bytes):
                user_copy[key] = f"<binary data of length {len(value)}>"
            elif hasattr(value, 'isoformat'):  # Handle datetime objects
                user_copy[key] = value.isoformat()
                
        return user_copy
    return None