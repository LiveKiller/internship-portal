from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import re
from datetime import datetime

from app import db
from app.auth.utils import hash_password, check_password, validate_registration_number, validate_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new student user."""
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('registration_no') or not (data.get('email') or data.get('email_id')) or not data.get('password'):
        return jsonify({'error': 'Registration number, email, and password are required'}), 400
    
    registration_no = data.get('registration_no')
    email = data.get('email') or data.get('email_id')
    password = data.get('password')
    
    # Validate registration number format (9 digits)
    if not re.match(r'^\d{9}$', registration_no):
        return jsonify({'error': 'Registration number must be 9 digits'}), 400
    
    # Validate email format
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Validate password (minimum 8 characters, at least one number and one letter)
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password):
        return jsonify({'error': 'Password must be at least 8 characters long and contain at least one letter and one number'}), 400
    
    # Check if user already exists
    existing_user = db.students.find_one({'registration_no': registration_no})
    if existing_user:
        return jsonify({'error': 'User with this registration number already exists'}), 409
    
    # Check if email is already used
    existing_email = db.students.find_one({'email_id': email})
    if existing_email:
        return jsonify({'error': 'User with this email already exists'}), 409
    
    # Hash password
    hashed_password = hash_password(password)
    
    # Create a new student record with required fields
    new_student = {
        'registration_no': registration_no,
        'email_id': email,
        'password': hashed_password,
        'registered': True,
        'name': data.get('name', 'New Student'),
        'roll_number': data.get('roll_number', registration_no),
        'mobile_no': data.get('mobile_no', ''),
        'gender': 'Other',
        'disability': 'No',
        'address': {
            'street': '',
            'pin': '',
            'district': '',
            'state': '',
            'country': ''
        },
        'father': {
            'name': '',
            'mobile_no': '',
            'email_id': ''
        },
        'mother': {
            'name': '',
            'mobile_no': '',
            'email_id': ''
        },
        'specialization': '',
        'pass_out_year': 0,
        'year_of_admission': 0,
        'marks': 0.0,
        'attendance': 0.0,
        'experience': [],
        'skills': {
            'technical': [],
            'non_technical': []
        },
        'projects': [],
        'education': {
            'tenth': 0.0,
            'twelfth': 0.0,
            'graduation': ''
        },
        'cv': '',
        'companies': {
            'applied': [],
            'rejected': [],
            'interviews_attended': [],
            'interviews_not_attended': []
        },
        'certifications': [],
        'messages': ''
    }
    
    # Insert the new student
    result = db.students.insert_one(new_student)
    
    if result.inserted_id:
        # Generate access token
        access_token = create_access_token(identity=registration_no)
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token
        }), 201
    else:
        return jsonify({'error': 'Failed to register user'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a student user."""
    data = request.get_json()
    
    if not data or not data.get('email_id') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    email = data.get('email_id')
    password = data.get('password')
    
    # Find the user by email
    user = db.students.find_one({'email_id': email})
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check password
    if not check_password(user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate access token
    access_token = create_access_token(identity=user['registration_no'])
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token
    }), 200

@auth_bp.route('/check-auth', methods=['GET'])
@jwt_required()
def check_auth():
    """Check if user is authenticated."""
    current_user = get_jwt_identity()
    return jsonify({
        'authenticated': True,
        'user': current_user
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout a user by adding their token to the blocklist."""
    # In a more complete implementation, you would add the token to a blocklist
    # For now, we'll just return a success message
    return jsonify({
        'message': 'Successfully logged out'
    }), 200

@auth_bp.route('/reset-password-request', methods=['POST'])
def reset_password_request():
    """Request a password reset by sending a reset link to the user's email."""
    data = request.get_json()
    
    if not data or not data.get('email_id'):
        return jsonify({'error': 'Email is required'}), 400
    
    email = data.get('email_id')
    
    # Find the user by email
    user = db.students.find_one({'email_id': email})
    
    if not user:
        # For security reasons, don't reveal that the email doesn't exist
        return jsonify({'message': 'If your email is registered, you will receive a reset link'}), 200
    
    # In a real implementation, you would generate a reset token and send an email
    # For now, we'll just return a success message
    return jsonify({
        'message': 'If your email is registered, you will receive a reset link'
    }), 200

@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    """Reset a user's password using a valid reset token."""
    data = request.get_json()
    
    if not data or not data.get('password'):
        return jsonify({'error': 'New password is required'}), 400
    
    password = data.get('password')
    
    # Validate password
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password):
        return jsonify({'error': 'Password must be at least 8 characters long and contain at least one letter and one number'}), 400
    
    # In a real implementation, you would validate the token and find the associated user
    # For now, we'll just return a success message
    return jsonify({
        'message': 'Password has been reset successfully'
    }), 200