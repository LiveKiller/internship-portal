import os
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename

from app import db
from app.auth.utils import user_to_json
from app.utils.file_utils import save_uploaded_file, delete_file

# Create blueprint with unique name and consistent URL prefix
student_profile_bp = Blueprint('student_profile', __name__, url_prefix='/api/student/profile')

@student_profile_bp.route('/', methods=['GET'])
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

@student_profile_bp.route('/update', methods=['PUT'])
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

@student_profile_bp.route('/upload-cv', methods=['POST'])
@jwt_required()
def upload_cv():
    """Upload a CV file."""
    current_user = get_jwt_identity()
    
    if 'cv' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['cv']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    try:
        # Save the file using our utility function
        filename = save_uploaded_file(file, 'cv', current_user)
        
        # Update user's CV path in database
        result = db.students.update_one(
            {'registration_no': current_user},
            {'$set': {'cv': filename}}
        )
        
        if result.modified_count:
            return jsonify({
                'message': 'CV uploaded successfully',
                'filename': filename
            }), 200
        else:
            return jsonify({'error': 'Failed to update CV information'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Failed to upload CV: {str(e)}'}), 500

@student_profile_bp.route('/download-cv', methods=['GET'])
@jwt_required()
def download_cv():
    """Download the user's CV."""
    current_user = get_jwt_identity()
    
    # Get user data to check CV path
    user = db.students.find_one({'registration_no': current_user})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    cv_path = user.get('cv')
    if not cv_path:
        return jsonify({'error': 'No CV uploaded'}), 404
    
    try:
        from app.utils.file_utils import get_file
        return get_file(cv_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'Failed to download CV: {str(e)}'}), 500

@student_profile_bp.route('/add-experience', methods=['POST'])
@jwt_required()
def add_experience():
    """Add new experience to profile."""
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['company_name', 'position', 'start_date', 'end_date', 'description']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create experience object
    experience = {
        'company_name': data['company_name'],
        'position': data['position'],
        'start_date': data['start_date'],
        'end_date': data['end_date'],
        'description': data['description'],
        'skills_used': data.get('skills_used', [])
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

@student_profile_bp.route('/update-experience/<index>', methods=['PUT'])
@jwt_required()
def update_experience(index):
    """Update an existing experience in profile."""
    current_user = get_jwt_identity()
    data = request.get_json()
    
    try:
        index = int(index)
    except ValueError:
        return jsonify({'error': 'Invalid experience index'}), 400
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Get user data to check if the experience exists
    user = db.students.find_one({'registration_no': current_user})
    if not user or 'experience' not in user:
        return jsonify({'error': 'User has no experiences'}), 404
    
    experiences = user.get('experience', [])
    if index >= len(experiences):
        return jsonify({'error': 'Experience index out of range'}), 404
    
    # Update the experience fields
    for key, value in data.items():
        experiences[index][key] = value
    
    # Update the user's experiences array
    result = db.students.update_one(
        {'registration_no': current_user},
        {'$set': {'experience': experiences}}
    )
    
    if result.modified_count:
        return jsonify({
            'message': 'Experience updated successfully',
            'experience': experiences[index]
        }), 200
    else:
        return jsonify({'message': 'No changes made to experience'}), 200

@student_profile_bp.route('/delete-experience/<index>', methods=['DELETE'])
@jwt_required()
def delete_experience(index):
    """Delete an experience from profile."""
    current_user = get_jwt_identity()
    
    try:
        index = int(index)
    except ValueError:
        return jsonify({'error': 'Invalid experience index'}), 400
    
    # Get user data to check if the experience exists
    user = db.students.find_one({'registration_no': current_user})
    if not user or 'experience' not in user:
        return jsonify({'error': 'User has no experiences'}), 404
    
    experiences = user.get('experience', [])
    if index >= len(experiences):
        return jsonify({'error': 'Experience index out of range'}), 404
    
    # Remove the experience at the specified index
    experiences.pop(index)
    
    # Update the user's experiences array
    result = db.students.update_one(
        {'registration_no': current_user},
        {'$set': {'experience': experiences}}
    )
    
    if result.modified_count:
        return jsonify({
            'message': 'Experience deleted successfully'
        }), 200
    else:
        return jsonify({'error': 'Failed to delete experience'}), 500

@student_profile_bp.route('/add-project', methods=['POST'])
@jwt_required()
def add_project():
    """Add new project to profile."""
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['project_name', 'description', 'technologies_used']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create project object
    project = {
        'project_name': data['project_name'],
        'description': data['description'],
        'technologies_used': data['technologies_used'],
        'start_date': data.get('start_date', ''),
        'end_date': data.get('end_date', ''),
        'github_link': data.get('github_link', ''),
        'live_link': data.get('live_link', '')
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

@student_profile_bp.route('/add-certification', methods=['POST'])
@jwt_required()
def add_certification():
    """Add new certification to profile."""
    current_user = get_jwt_identity()
    
    # Check if the request contains a file
    if 'file' in request.files:
        file = request.files['file']
        
        # Get form data
        certificate_name = request.form.get('certificate_name')
        institute_name = request.form.get('institute_name')
        verification_link = request.form.get('verification_link', '')
        
        if not certificate_name or not institute_name:
            return jsonify({'error': 'Certificate name and institute name are required'}), 400
        
        # Save the certification file
        success, result = save_uploaded_file(
            file=file,
            subdirectory='certifications',
            user_id=current_user
        )
        
        if not success:
            return jsonify({'error': result}), 400
        
        # Create certification object with file path
        certification = {
            'certificate_name': certificate_name,
            'institute_name': institute_name,
            'verification_link': verification_link,
            'pdf': result['relative_path']
        }
    else:
        # JSON data without file
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        if not data.get('certificate_name') or not data.get('institute_name'):
            return jsonify({'error': 'Certificate name and institute name are required'}), 400
        
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

@student_profile_bp.route('/upload-certification/<certification_index>', methods=['POST'])
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

@student_profile_bp.route('/update-skills', methods=['PUT'])
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
