from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from functools import wraps
import hmac
import hashlib
import time
from bson.objectid import ObjectId
from datetime import datetime  # Added for application status updates

from app import db
from app.models.admin import Admin
from app.auth.utils import hash_password, check_password

admin_bp = Blueprint('admin', __name__)

def require_admin_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('X-Admin-Key')
        timestamp = request.headers.get('X-Timestamp')
        signature = request.headers.get('X-Signature')
        
        if not all([auth_header, timestamp, signature]):
            return jsonify({'error': 'Missing authentication headers'}), 401
        
        # Verify timestamp is within 5 minutes
        current_time = int(time.time())
        request_time = int(timestamp)
        if abs(current_time - request_time) > 300:  # 5 minutes
            return jsonify({'error': 'Request expired'}), 401
        
        # Verify signature
        expected_signature = hmac.new(
            bytes(auth_header, 'utf-8'),
            bytes(f"{timestamp}", 'utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return jsonify({'error': 'Invalid signature'}), 401
            
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """Login for admin users with simplified authentication."""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    # Hard code admin credentials for testing
    if username == 'savi@admin' and password == 'admin@savi':
        access_token = create_access_token(
            identity='admin',
            additional_claims={'is_admin': True}
        )
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token
        }), 200
    
    # Try to find admin in database if hard-coded credentials fail
    admin = Admin.get_admin_by_username(username)
    if not admin:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not check_password(admin['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(
        identity=str(admin['_id']),
        additional_claims={'is_admin': True}
    )
    
    if admin.get('_id'):
        Admin.update_last_login(admin['_id'])
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token
    }), 200

def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user = get_jwt_identity()
        claims = get_jwt()
        
        if not claims.get('is_admin', False):
            return jsonify({'error': 'Admin access required'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@admin_required
def admin_dashboard():
    """Protected admin dashboard route."""
    # Get counts for dashboard stats
    students_count = db.students.count_documents({})
    companies_count = db.companies.count_documents({})
    applications_count = db.applications.count_documents({})
    pending_applications = db.applications.count_documents({'status': 'pending'})
    
    return jsonify({
        'message': 'Welcome to admin dashboard',
        'status': 'success',
        'stats': {
            'students_count': students_count,
            'companies_count': companies_count,
            'applications_count': applications_count,
            'pending_applications': pending_applications
        }
    }), 200

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def list_users():
    """List all users (protected admin route)."""
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    skip = (page - 1) * per_page
    
    # Get total count
    total = db.students.count_documents({})
    
    # Get paginated users
    users = list(db.students.find({}, {
        'password': 0,  # Exclude password field
        'aadhar_no': 0,  # Exclude sensitive information
        'parivar_pehchan_patra_id': 0
    }).skip(skip).limit(per_page))
    
    # Convert ObjectId to string for JSON serialization
    for user in users:
        user['_id'] = str(user['_id'])
    
    return jsonify({
        'users': users,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }), 200

@admin_bp.route('/users/<user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(user_id):
    """Get a specific user by ID (protected admin route)."""
    user = db.students.find_one({'registration_no': user_id}, {
        'password': 0,  # Exclude password field
        'aadhar_no': 0,  # Exclude sensitive information
        'parivar_pehchan_patra_id': 0
    })
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Convert ObjectId to string for JSON serialization
    user['_id'] = str(user['_id'])
    
    return jsonify({
        'user': user
    }), 200

@admin_bp.route('/companies', methods=['GET'])
@jwt_required()
@admin_required
def list_companies():
    """List all companies (protected admin route)."""
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    skip = (page - 1) * per_page
    
    # Get total count
    total = db.companies.count_documents({})
    
    # Get paginated companies
    companies = list(db.companies.find({}).skip(skip).limit(per_page))
    
    # Convert ObjectId to string for JSON serialization
    for company in companies:
        company['_id'] = str(company['_id'])
    
    return jsonify({
        'companies': companies,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }), 200

@admin_bp.route('/companies', methods=['POST'])
@jwt_required()
@admin_required
def create_company():
    """Create a new company (protected admin route)."""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('job_title'):
        return jsonify({'error': 'Company name and job title are required'}), 400
    
    # Create company object
    company = {
        'name': data.get('name'),
        'logo': data.get('logo', ''),
        'job_title': data.get('job_title'),
        'job_description': data.get('job_description', ''),
        'job_type': data.get('job_type', 'Full-time'),
        'work_place': data.get('work_place', 'On-site'),
        'duration': data.get('duration', '6 months'),
        'stipend': data.get('stipend', 0),
        'requirements': data.get('requirements', []),
        'posted_date': time.time(),
        'deadline': data.get('deadline', time.time() + 30*24*60*60),  # Default 30 days
        'active': data.get('active', True)
    }
    
    # Insert the company
    result = db.companies.insert_one(company)
    
    if result.inserted_id:
        company['_id'] = str(result.inserted_id)
        return jsonify({
            'message': 'Company created successfully',
            'company': company
        }), 201
    else:
        return jsonify({'error': 'Failed to create company'}), 500

@admin_bp.route('/companies/<company_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_company(company_id):
    """Update a company (protected admin route)."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate ObjectId format
    if not ObjectId.is_valid(company_id):
        return jsonify({'error': 'Invalid company ID format'}), 400
    
    # Check if company exists
    company = db.companies.find_one({'_id': ObjectId(company_id)})
    if not company:
        return jsonify({'error': 'Company not found'}), 404
    
    # Update company fields
    update_data = {}
    for key, value in data.items():
        if key != '_id':  # Prevent updating the ID
            update_data[key] = value
    
    # Update the company
    result = db.companies.update_one(
        {'_id': ObjectId(company_id)},
        {'$set': update_data}
    )
    
    if result.modified_count:
        return jsonify({
            'message': 'Company updated successfully'
        }), 200
    else:
        return jsonify({'message': 'No changes made to company'}), 200

@admin_bp.route('/announcements', methods=['POST'])
@jwt_required()
@admin_required
def create_announcement():
    """Create a new announcement (protected admin route)."""
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({'error': 'Title and content are required'}), 400
    
    # Create announcement object
    announcement = {
        'title': data.get('title'),
        'content': data.get('content'),
        'date': datetime.utcnow(),
        'important': data.get('important', False),
        'attachment': data.get('attachment', ''),
        'posted_by': get_jwt_identity()
    }
    
    # Insert the announcement
    result = db.announcements.insert_one(announcement)
    
    if result.inserted_id:
        announcement['_id'] = str(result.inserted_id)
        return jsonify({
            'message': 'Announcement created successfully',
            'announcement': announcement
        }), 201
    else:
        return jsonify({'error': 'Failed to create announcement'}), 500

@admin_bp.route('/applications', methods=['GET'])
@jwt_required()
@admin_required
def list_applications():
    """List all applications (protected admin route)."""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    skip = (page - 1) * per_page

    status = request.args.get('status')
    query = {}
    if status:
        query['status'] = status

    total = db.applications.count_documents(query)
    applications = list(db.applications.find(query).skip(skip).limit(per_page))

    for application in applications:
        application['_id'] = str(application['_id'])
        application['company_id'] = str(application['company_id'])
        # student_id is already a string

    return jsonify({
        'applications': applications,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }), 200

@admin_bp.route('/applications/<application_id>/status', methods=['PUT'])
@jwt_required()
@admin_required
def update_application_status(application_id):
    """Update the status of a specific application (protected admin route)."""
    data = request.get_json()
    if not data or not data.get('status'):
        return jsonify({'error': 'New status is required'}), 400

    status_val = data.get('status')
    if status_val not in ['pending', 'approved', 'rejected']:
        return jsonify({'error': 'Invalid status value'}), 400

    if not ObjectId.is_valid(application_id):
        return jsonify({'error': 'Invalid application ID format'}), 400

    # Update the application status and set status_updated_date
    result = db.applications.update_one(
        {'_id': ObjectId(application_id)},
        {'$set': {'status': status_val, 'status_updated_date': datetime.now()}}
    )

    if result.modified_count:
        return jsonify({
            'message': 'Application status updated successfully'
        }), 200
    else:
        return jsonify({'message': 'No changes made to application status'}), 200