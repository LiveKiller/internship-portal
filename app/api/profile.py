import os
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from app import db
from app.auth.utils import user_to_json
from app.utils.file_utils import save_uploaded_file, delete_file

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/', methods=['GET'])
@jwt_required()
def get_profile():
    """Get the profile of the current user."""
    current_user = get_jwt_identity()
    
    # Get user data
    user = db.students.find_one({'registration_no': current_user})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Convert user to JSON-serializable format
    user_data = user_to_json(user)
    
    return jsonify({
        'profile': user_data
    }), 200

@profile_bp.route('/', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update the profile of the current user."""
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Get user data
    user = db.students.find_one({'registration_no': current_user})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Fields that cannot be updated by the user
    protected_fields = ['_id', 'registration_no', 'password', 'registered', 'cv']
    
    # Remove protected fields from update data
    update_data = {k: v for k, v in data.items() if k not in protected_fields}
    
    # Update user data
    result = db.students.update_one(
        {'registration_no': current_user},
        {'$set': update_data}
    )
    
    if result.modified_count:
        return jsonify({
            'message': 'Profile updated successfully'
        }), 200
    else:
        return jsonify({'message': 'No changes made to profile'}), 200

@profile_bp.route('/upload-cv', methods=['POST'])
@jwt_required()
def upload_cv():
    """Upload a CV file."""
    current_user = get_jwt_identity()
    
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # Get user data to check if there's an existing CV to delete
    user = db.students.find_one({'registration_no': current_user})
    if user and user.get('cv'):
        # Delete the old CV file if it exists
        delete_file(user.get('cv'))
    
    # Save the new CV file
    success, result = save_uploaded_file(
        file=file,
        subdirectory='cv',
        user_id=current_user,
        file_prefix='CV'
    )
    
    if success:
        # Update CV path in user profile
        db.students.update_one(
            {'registration_no': current_user},
            {'$set': {'cv': result['relative_path']}}
        )
        
        return jsonify({
            'message': 'CV uploaded successfully',
            'filename': result['filename'],
            'path': result['relative_path']
        }), 201
    else:
        return jsonify({'error': result}), 400

@profile_bp.route('/add-experience', methods=['POST'])
@jwt_required()
def add_experience():
    """Add new work experience to profile."""
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['job_title', 'company_name', 'start_date', 'description', 'skills']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create experience object
    experience = {
        'job_title': data['job_title'],
        'company_name': data['company_name'],
        'start_date': data['start_date'],
        'end_date': data.get('end_date', 'current'),
        'description': data['description'],
        'skills': data['skills']
    }
    
    # Add experience to user profile
    result = db.students.update_one(
        {'registration_no': current_user},
        {'$push': {'experience': experience}}
    )
    
    if result.modified_count:
        return jsonify({
            'message': 'Experience added successfully',
            'experience': experience
        }), 201
    else:
        return jsonify({'error': 'Failed to add experience'}), 500

@profile_bp.route('/add-project', methods=['POST'])
@jwt_required()
def add_project():
    """Add new project to profile."""
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['project_name', 'project_description', 'project_link']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create project object
    project = {
        'project_name': data['project_name'],
        'project_description': data['project_description'],
        'project_link': data['project_link']
    }
    
    # Add project to user profile
    result = db.students.update_one(
        {'registration_no': current_user},
        {'$push': {'projects': project}}
    )
    
    if result.modified_count:
        return jsonify({
            'message': 'Project added successfully',
            'project': project
        }), 201
    else:
        return jsonify({'error': 'Failed to add project'}), 500

@profile_bp.route('/add-certification', methods=['POST'])
@jwt_required()
def add_certification():
    """Add new certification to profile."""
    current_user = get_jwt_identity()
    
    # Check if this is a form submission with a file or JSON data
    if request.content_type and 'multipart/form-data' in request.content_type:
        # Process multipart form data with file upload
        certificate_name = request.form.get('certificate_name')
        institute_name = request.form.get('institute_name')
        verification_link = request.form.get('verification_link')
        
        if not certificate_name or not institute_name or not verification_link:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check for the certificate file
        cert_file = None
        if 'certificate_file' in request.files:
            cert_file = request.files['certificate_file']
        
        # Create certification object
        certification = {
            'certificate_name': certificate_name,
            'institute_name': institute_name,
            'verification_link': verification_link,
            'pdf': ''  # Will be updated if file is uploaded
        }
        
        # Upload the certificate file if provided
        if cert_file and cert_file.filename != '':
            success, result = save_uploaded_file(
                file=cert_file,
                subdirectory='certifications',
                user_id=current_user,
                file_prefix='CERT'
            )
            
            if success:
                certification['pdf'] = result['relative_path']
            else:
                return jsonify({'error': result}), 400
    else:
        # Process JSON data without file
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['certificate_name', 'institute_name', 'verification_link']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create certification object
        certification = {
            'certificate_name': data['certificate_name'],
            'institute_name': data['institute_name'],
            'verification_link': data['verification_link'],
            'pdf': data.get('pdf', '')
        }
    
    # Add certification to user profile
    result = db.students.update_one(
        {'registration_no': current_user},
        {'$push': {'certifications': certification}}
    )
    
    if result.modified_count:
        return jsonify({
            'message': 'Certification added successfully',
            'certification': certification
        }), 201
    else:
        return jsonify({'error': 'Failed to add certification'}), 500

@profile_bp.route('/upload-certification/<certification_index>', methods=['POST'])
@jwt_required()
def upload_certification_file(certification_index):
    """Upload a certification document for an existing certification."""
    current_user = get_jwt_identity()
    
    try:
        certification_index = int(certification_index)
    except ValueError:
        return jsonify({'error': 'Invalid certification index'}), 400
    
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # Get user data to check if the certification exists
    user = db.students.find_one({'registration_no': current_user})
    if not user or 'certifications' not in user:
        return jsonify({'error': 'User has no certifications'}), 404
    
    certifications = user.get('certifications', [])
    if certification_index >= len(certifications):
        return jsonify({'error': 'Certification index out of range'}), 404
    
    # Get the existing certification
    certification = certifications[certification_index]
    
    # If there's an existing PDF, delete it
    if certification.get('pdf'):
        delete_file(certification.get('pdf'))
    
    # Save the new certification file
    success, result = save_uploaded_file(
        file=file,
        subdirectory='certifications',
        user_id=current_user,
        file_prefix=f'CERT_{certification_index}'
    )
    
    if success:
        # Update the certification with the new file path
        certifications[certification_index]['pdf'] = result['relative_path']
        
        # Update the user's certifications array
        db.students.update_one(
            {'registration_no': current_user},
            {'$set': {'certifications': certifications}}
        )
        
        return jsonify({
            'message': 'Certification file uploaded successfully',
            'filename': result['filename'],
            'path': result['relative_path']
        }), 201
    else:
        return jsonify({'error': result}), 400

@profile_bp.route('/update-skills', methods=['PUT'])
@jwt_required()
def update_skills():
    """Update skills in profile."""
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate skills data
    if 'technical' not in data and 'non_technical' not in data:
        return jsonify({'error': 'At least one of technical or non_technical skills must be provided'}), 400
    
    update_fields = {}
    if 'technical' in data:
        update_fields['skills.technical'] = data['technical']
    if 'non_technical' in data:
        update_fields['skills.non_technical'] = data['non_technical']
    
    # Update skills in user profile
    result = db.students.update_one(
        {'registration_no': current_user},
        {'$set': update_fields}
    )
    
    if result.modified_count:
        return jsonify({
            'message': 'Skills updated successfully'
        }), 200
    else:
        return jsonify({'message': 'No changes made to skills'}), 200