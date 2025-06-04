from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
import time

from app import db
from app.auth.utils import get_user_role
from app.auth.role_required import role_required

# Create a blueprint with a unique name to avoid conflicts
companies_bp = Blueprint('companies_module', __name__, url_prefix='/companies')

@companies_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_companies():
    """Get all active companies with pagination."""
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    sort_by = request.args.get('sort_by', 'name')
    sort_order = int(request.args.get('sort_order', 1))  # 1 for ascending, -1 for descending
    show_inactive = request.args.get('show_inactive', 'false').lower() == 'true'
    
    # Calculate skip
    skip = (page - 1) * per_page
    
    # Create query filter
    query_filter = {} if show_inactive else {'active': True}
    
    # Get companies with pagination
    companies_cursor = db.companies.find(query_filter).sort(sort_by, sort_order).skip(skip).limit(per_page)
    companies = list(companies_cursor)
    
    # Convert ObjectId to string for JSON serialization
    for company in companies:
        company['_id'] = str(company['_id'])
    
    # Get total count
    total_companies = db.companies.count_documents(query_filter)
    total_pages = (total_companies + per_page - 1) // per_page
    
    return jsonify({
        'companies': companies,
        'pagination': {
            'current_page': page,
            'per_page': per_page,
            'total_items': total_companies,
            'total_pages': total_pages
        }
    }), 200

@companies_bp.route('/<string:company_id>', methods=['GET'])
@jwt_required()
def get_company(company_id):
    """Get a specific company by ID."""
    try:
        # Convert string ID to ObjectId
        obj_id = ObjectId(company_id)
        
        # Get the company
        company = db.companies.find_one({'_id': obj_id})
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Convert ObjectId to string for JSON serialization
        company['_id'] = str(company['_id'])
        
        return jsonify({
            'company': company
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@companies_bp.route('/', methods=['POST'])
@jwt_required()
@role_required(['admin'])
def create_company():
    """Create a new company (admin only)."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Required fields
    required_fields = ['name', 'description', 'requirements', 'contact_email']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f"Missing required field: {field}"}), 400
    
    # Set default values for optional fields
    data.setdefault('active', True)
    data.setdefault('deadline', int(time.time()) + 604800)  # Default 1 week from now
    data.setdefault('created_at', int(time.time()))
    data.setdefault('updated_at', int(time.time()))
    
    # Insert the new company
    result = db.companies.insert_one(data)
    
    # Get the created company
    created_company = db.companies.find_one({'_id': result.inserted_id})
    created_company['_id'] = str(created_company['_id'])
    
    return jsonify({
        'message': 'Company created successfully',
        'company': created_company
    }), 201

@companies_bp.route('/<string:company_id>', methods=['PUT'])
@jwt_required()
@role_required(['admin', 'company'])
def update_company(company_id):
    """Update an existing company (admin or company only)."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Convert string ID to ObjectId
        obj_id = ObjectId(company_id)
        
        # Get the company to make sure it exists
        company = db.companies.find_one({'_id': obj_id})
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Fields that are not allowed to be updated
        protected_fields = ['_id', 'created_at']
        
        # Remove protected fields from the update data
        update_data = {k: v for k, v in data.items() if k not in protected_fields}
        
        # Always update the updated_at timestamp
        update_data['updated_at'] = int(time.time())
        
        # Update the company
        result = db.companies.update_one(
            {'_id': obj_id},
            {'$set': update_data}
        )
        
        if result.modified_count:
            # Get the updated company
            updated_company = db.companies.find_one({'_id': obj_id})
            updated_company['_id'] = str(updated_company['_id'])
            
            return jsonify({
                'message': 'Company updated successfully',
                'company': updated_company
            }), 200
        else:
            return jsonify({
                'message': 'No changes were made to the company'
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@companies_bp.route('/<string:company_id>/apply', methods=['POST'])
@jwt_required()
@role_required(['student'])
def apply_to_company(company_id):
    """Apply to a company (student only)."""
    student_id = get_jwt_identity()
    
    try:
        # Convert string ID to ObjectId
        obj_id = ObjectId(company_id)
        
        # Get the company to make sure it exists and is active
        company = db.companies.find_one({'_id': obj_id, 'active': True})
        if not company:
            return jsonify({'error': 'Company not found or inactive'}), 404
        
        # Check if the deadline has passed
        current_time = int(time.time())
        if current_time > company.get('deadline', 0):
            return jsonify({'error': 'Application deadline has passed'}), 400
        
        # Check if student has already applied
        student = db.students.find_one({'registration_no': student_id})
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        applied_companies = student.get('companies', {}).get('applied', [])
        if company_id in applied_companies:
            return jsonify({'error': 'You have already applied to this company'}), 400
        
        # Add company to student's applied list
        db.students.update_one(
            {'registration_no': student_id},
            {'$push': {'companies.applied': company_id}}
        )
        
        # Create application record
        application = {
            'student_id': student_id,
            'company_id': company_id,
            'company_name': company.get('name'),
            'applied_at': current_time,
            'status': 'pending'
        }
        
        db.applications.insert_one(application)
        
        return jsonify({
            'message': 'Successfully applied to company',
            'company_name': company.get('name')
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400 