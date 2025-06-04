from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId

from app import db
from app.auth.utils import user_to_json
from app.auth.role_required import role_required

# Create a blueprint with a unique name to avoid conflicts
students_bp = Blueprint('students_module', __name__, url_prefix='/api/students')

@students_bp.route('/', methods=['GET'])
@jwt_required()
@role_required(['admin', 'faculty'])
def get_all_students():
    """Get all students (admin/faculty only)."""
    # Get query parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    sort_by = request.args.get('sort_by', 'name.first')
    sort_order = int(request.args.get('sort_order', 1))  # 1 for ascending, -1 for descending
    
    # Calculate skip
    skip = (page - 1) * per_page
    
    # Get students with pagination
    students_cursor = db.students.find().sort(sort_by, sort_order).skip(skip).limit(per_page)
    students = list(students_cursor)
    
    # Convert to JSON-serializable format
    student_list = [user_to_json(student) for student in students]
    
    # Get total count
    total_students = db.students.count_documents({})
    total_pages = (total_students + per_page - 1) // per_page
    
    return jsonify({
        'students': student_list,
        'pagination': {
            'current_page': page,
            'per_page': per_page,
            'total_items': total_students,
            'total_pages': total_pages
        }
    }), 200

@students_bp.route('/<string:student_id>', methods=['GET'])
@jwt_required()
@role_required(['admin', 'faculty', 'student'])
def get_student(student_id):
    """Get a specific student by ID."""
    # Check if the requesting user is allowed to access this student
    identity = get_jwt_identity()
    role = db.students.find_one({'registration_no': identity})
    
    # If student is requesting and not their own profile, reject
    if role and role.get('role') == 'student' and identity != student_id:
        return jsonify({'error': 'You can only view your own profile'}), 403
    
    # Get the student
    student = db.students.find_one({'registration_no': student_id})
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Convert to JSON-serializable format
    student_data = user_to_json(student)
    
    return jsonify({
        'student': student_data
    }), 200

@students_bp.route('/upload-cv', methods=['POST'])
@jwt_required()
@role_required(['student'])
def upload_cv():
    """Upload student CV."""
    # Get the student ID
    student_id = get_jwt_identity()
    
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    # If the user does not select a file, the browser may
    # submit an empty file without a filename
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file extension
    allowed_extensions = {'pdf', 'doc', 'docx'}
    if not '.' in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'error': 'File type not allowed. Please upload PDF, DOC, or DOCX files only'}), 400
    
    # Secure the filename
    filename = secure_filename(file.filename)
    
    # Rename file to include student_id for uniqueness
    file_extension = filename.rsplit('.', 1)[1].lower()
    new_filename = f"{student_id}_cv.{file_extension}"
    
    # Save the file
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'cv')
    file_path = os.path.join(upload_folder, new_filename)
    file.save(file_path)
    
    # Update the student record with the CV file path
    db.students.update_one(
        {'registration_no': student_id},
        {'$set': {'cv_path': f"uploads/cv/{new_filename}"}}
    )
    
    return jsonify({
        'message': 'CV uploaded successfully',
        'file_path': f"uploads/cv/{new_filename}"
    }), 200

@students_bp.route('/upload-certification', methods=['POST'])
@jwt_required()
@role_required(['student'])
def upload_certification():
    """Upload student certification."""
    # Get the student ID
    student_id = get_jwt_identity()
    
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    # If the user does not select a file, the browser may
    # submit an empty file without a filename
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file extension
    allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png'}
    if not '.' in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'error': 'File type not allowed. Please upload PDF or image files only'}), 400
    
    # Get certification name from form data
    certification_name = request.form.get('name', 'Unnamed Certification')
    
    # Secure the filename
    filename = secure_filename(file.filename)
    
    # Rename file to include student_id and timestamp for uniqueness
    file_extension = filename.rsplit('.', 1)[1].lower()
    timestamp = int(db.utils.get_timestamp())
    new_filename = f"{student_id}_cert_{timestamp}.{file_extension}"
    
    # Save the file
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'certifications')
    file_path = os.path.join(upload_folder, new_filename)
    file.save(file_path)
    
    # Create certification object
    certification = {
        'name': certification_name,
        'file_path': f"uploads/certifications/{new_filename}",
        'upload_date': timestamp
    }
    
    # Update the student record with the certification
    db.students.update_one(
        {'registration_no': student_id},
        {'$push': {'certifications': certification}}
    )
    
    return jsonify({
        'message': 'Certification uploaded successfully',
        'certification': certification
    }), 200 