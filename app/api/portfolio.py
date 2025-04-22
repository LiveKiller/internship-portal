from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import os

from app import db
from app.auth.utils import user_to_json
from app.utils.file_utils import get_file

portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/', methods=['GET'])
@jwt_required()
def get_portfolio():
    """Get the portfolio data of the current user."""
    current_user = get_jwt_identity()
    
    # Get user data
    user = db.students.find_one({'registration_no': current_user})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Extract portfolio-relevant fields
    portfolio_data = {
        'name': user.get('name', ''),
        'roll_number': user.get('roll_number', ''),
        'registration_no': user.get('registration_no', ''),
        'email_id': user.get('email_id', ''),
        'mobile_no': user.get('mobile_no', ''),
        'specialization': user.get('specialization', ''),
        'skills': user.get('skills', {'technical': [], 'non_technical': []}),
        'experience': user.get('experience', []),
        'projects': user.get('projects', []),
        'education': user.get('education', {'tenth': 0.0, 'twelfth': 0.0, 'graduation': ''}),
        'certifications': user.get('certifications', []),
        'cv': user.get('cv', '')
    }
    
    return jsonify({
        'portfolio': portfolio_data
    }), 200

@portfolio_bp.route('/download-cv', methods=['GET'])
@jwt_required()
def download_cv():
    """Download the CV of the current user."""
    current_user = get_jwt_identity()
    
    # Get user data to check CV path
    user = db.students.find_one({'registration_no': current_user})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    cv_path = user.get('cv')
    if not cv_path:
        return jsonify({'error': 'No CV uploaded'}), 404
    
    # Extract the original filename from the path for a better download experience
    _, filename = os.path.split(cv_path)
    # Remove user ID and UUID prefix for a cleaner filename
    parts = filename.split('_')
    if len(parts) >= 3:  # Format is CV_userid_uuid_originalname
        original_name = '_'.join(parts[3:])
    else:
        original_name = filename
    
    # Get the file using our utility function
    return get_file(cv_path, as_attachment=True, custom_filename=original_name)

@portfolio_bp.route('/download-certification/<certification_index>', methods=['GET'])
@jwt_required()
def download_certification(certification_index):
    """Download a certification file."""
    current_user = get_jwt_identity()
    
    try:
        certification_index = int(certification_index)
    except ValueError:
        return jsonify({'error': 'Invalid certification index'}), 400
    
    # Get user data to check certification path
    user = db.students.find_one({'registration_no': current_user})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    certifications = user.get('certifications', [])
    if certification_index >= len(certifications):
        return jsonify({'error': 'Certification index out of range'}), 404
    
    # Get the certification file path
    certification = certifications[certification_index]
    cert_path = certification.get('pdf')
    
    if not cert_path:
        return jsonify({'error': 'No certificate file uploaded for this certification'}), 404
    
    # Extract a readable filename for download
    cert_name = certification.get('certificate_name', 'certificate')
    institute = certification.get('institute_name', '')
    
    # Create a clean filename for download
    download_name = f"{cert_name}_{institute}.pdf"
    download_name = download_name.replace(' ', '_')
    
    # Get the file using our utility function
    return get_file(cert_path, as_attachment=True, custom_filename=download_name)

@portfolio_bp.route('/public/<registration_no>', methods=['GET'])
def get_public_portfolio(registration_no):
    """Get the public portfolio of a specific user."""
    # Get user data
    user = db.students.find_one({'registration_no': registration_no})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Extract only public portfolio fields
    public_portfolio = {
        'name': user.get('name', ''),
        'registration_no': user.get('registration_no', ''),
        'specialization': user.get('specialization', ''),
        'skills': user.get('skills', {'technical': [], 'non_technical': []}),
        'projects': user.get('projects', []),
        'certifications': user.get('certifications', [])
    }
    
    return jsonify({
        'portfolio': public_portfolio
    }), 200