from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app import db
from app.auth.utils import hash_password, check_password, validate_registration_number, validate_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new student user."""
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('registration_no') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Registration number, email and password are required'}), 400
    
    registration_no = data.get('registration_no')
    email = data.get('email')
    password = data.get('password')
    
    # Validate registration number format (9 digits)
    if not validate_registration_number(registration_no):
        return jsonify({'error': 'Registration number must be 9 digits'}), 400
    
    # Validate email format
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
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
    
    # Create a minimal student record with only required fields
    new_student = {
        'registration_no': registration_no,
        'email_id': email,
        'password': hashed_password,
        'registered': True
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
    
    email_id = data.get('email_id')
    password = data.get('password')
    
    # Find the user by email
    user = db.students.find_one({'email_id': email_id})
    
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