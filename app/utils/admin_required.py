from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
import sys
import os

# Add the parent directory to sys.path to make imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app import db

def admin_required(fn):
    """
    Decorator to check if the current user is an admin.
    Must be used with jwt_required() decorator.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()
        
        # Check if user exists and is an admin
        user = db.users.find_one({'username': current_user})
        if not user or not user.get('is_admin', False):
            return jsonify({'error': 'Admin access required'}), 403
        
        return fn(*args, **kwargs)
    
    return wrapper
