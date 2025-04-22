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
    """Validate that a registration number is 9 digits."""
    return bool(re.match(r'^\d{9}$', reg_no))

def validate_email(email):
    """Validate that an email has a valid format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def get_current_user():
    """Get the current user from JWT identity."""
    registration_no = get_jwt_identity()
    return db.students.find_one({'registration_no': registration_no})

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