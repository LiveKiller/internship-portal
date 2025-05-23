from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from bson.objectid import ObjectId

from app import db

company_bp = Blueprint('company', __name__)

@company_bp.route('/', methods=['GET'])
@jwt_required()
def get_companies():
    """Get list of companies with active job postings."""
    # Get query parameters for filtering
    job_type = request.args.get('jobType')
    work_place = request.args.get('workPlace')
    duration = request.args.get('duration')
    stipend = request.args.get('stipend')
    posted_time = request.args.get('postedTime')
    
    # Build query filter
    query = {'active': True}
    if job_type:
        query['job_type'] = job_type
    if work_place:
        query['work_place'] = work_place
    if duration:
        query['duration'] = duration
    if stipend:
        try:
            min_stipend = int(stipend)
            query['stipend'] = {'$gte': min_stipend}
        except ValueError:
            pass
    if posted_time:
        # Convert posted_time filter to datetime
        try:
            days = int(posted_time)
            cutoff_date = datetime.now() - timedelta(days=days)
            query['posted_date'] = {'$gte': cutoff_date}
        except ValueError:
            pass
    
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Get total count for pagination
    total = db.companies.count_documents(query)
    
    # Apply pagination
    companies = list(db.companies.find(query).skip((page-1)*per_page).limit(per_page))
    
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

@company_bp.route('/<company_id>', methods=['GET'])
@jwt_required()
def get_company(company_id):
    """Get detailed information about a specific company."""
    try:
        # Validate the ObjectId format
        if not ObjectId.is_valid(company_id):
            return jsonify({'error': 'Invalid company ID format'}), 400
            
        company = db.companies.find_one({'_id': ObjectId(company_id)})
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Convert ObjectId to string for JSON serialization
        company['_id'] = str(company['_id'])
        
        return jsonify({
            'company': company
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@company_bp.route('/<company_id>/apply', methods=['POST'])
@jwt_required()
def apply_to_company(company_id):
    """Submit an application to a company."""
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Validate the ObjectId format
        if not ObjectId.is_valid(company_id):
            return jsonify({'error': 'Invalid company ID format'}), 400
            
        # Check if company exists
        company = db.companies.find_one({'_id': ObjectId(company_id)})
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Check if user exists and initialize companies field if needed
        user = db.students.find_one({'registration_no': current_user})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if 'companies' not in user:
            db.students.update_one(
                {'registration_no': current_user},
                {'$set': {'companies': {'applied': [], 'rejected': [], 'interviews_attended': [], 'interviews_not_attended': []}}}
            )
        
        # Check if user has already applied
        existing_application = db.applications.find_one({
            'company_id': ObjectId(company_id),
            'student_id': current_user
        })
        if existing_application:
            return jsonify({'error': 'Already applied to this company'}), 409
        
        # Create application with required fields from test
        application = {
            'company_id': ObjectId(company_id),
            'student_id': current_user,
            'status': 'pending',
            'applied_date': datetime.now(),
            'coverLetter': data.get('coverLetter', ''),
            'portfolio': data.get('portfolio', ''),
            'availability': data.get('availability', ''),
            'noticePeriod': data.get('noticePeriod', '')
        }
        
        # Save application
        result = db.applications.insert_one(application)
        
        if result.inserted_id:
            # Update student's applied companies
            db.students.update_one(
                {'registration_no': current_user},
                {'$push': {'companies.applied': ObjectId(company_id)}}
            )
            
            return jsonify({
                'message': 'Application submitted successfully',
                'application_id': str(result.inserted_id)
            }), 201
        else:
            return jsonify({'error': 'Failed to submit application'}), 500
    except Exception as e:
        print(f"Error in apply_to_company: {str(e)}")  # Add logging
        return jsonify({'error': str(e)}), 500

@company_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    """Get all applications for the current user."""
    current_user = get_jwt_identity()
    
    # Get all applications for the user
    applications = list(db.applications.find({'student_id': current_user}))
    
    # Convert ObjectId to string for JSON serialization and add company details
    for application in applications:
        application['_id'] = str(application['_id'])
        application['company_id'] = str(application['company_id'])
        
        # Get company details
        company = db.companies.find_one({'_id': ObjectId(application['company_id'])})
        if company:
            application['company'] = {
                'name': company.get('name', ''),
                'logo': company.get('logo', ''),
                'job_title': company.get('job_title', '')
            }
    
    return jsonify({
        'applications': applications
    }), 200

@company_bp.route('/<company_id>/status', methods=['GET'])
@jwt_required()
def get_application_status(company_id):
    """Get the application status for a specific company."""
    current_user = get_jwt_identity()
    
    try:
        # Validate the ObjectId format
        if not ObjectId.is_valid(company_id):
            return jsonify({'error': 'Invalid company ID format'}), 400
            
        # Find the application
        application = db.applications.find_one({
            'company_id': ObjectId(company_id),
            'student_id': current_user
        })
        
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        # Convert ObjectId to string for JSON serialization
        application['_id'] = str(application['_id'])
        application['company_id'] = str(application['company_id'])
        
        return jsonify({
            'status': application.get('status', 'pending'),
            'application': application
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
