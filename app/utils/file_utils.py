"""
Utility functions for file operations like uploads and downloads.
"""
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app, jsonify, send_from_directory

# File type allowlists
ALLOWED_CV_EXTENSIONS = {'pdf', 'doc', 'docx'}
ALLOWED_CERT_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
ALLOWED_ANNOUNCEMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt'}

def allowed_file_extension(filename, allowed_extensions):
    """
    Check if the file has an allowed extension.
    
    Args:
        filename (str): The filename to check
        allowed_extensions (set): Set of allowed extensions
        
    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, subdirectory, user_id=None, file_prefix=''):
    """
    Save an uploaded file to the appropriate subdirectory with a unique name.
    
    Args:
        file: The file object from request.files
        subdirectory (str): Subdirectory within UPLOAD_FOLDER (e.g., 'cv', 'certifications')
        user_id (str, optional): User ID to include in the filename for better organization
        file_prefix (str, optional): Prefix to add to the filename
        
    Returns:
        tuple: (success, result)
            - If success is True, result is a dict with relative_path and filename
            - If success is False, result is an error message
    """
    if file.filename == '':
        return False, 'No selected file'
    
    # Determine allowed extensions based on subdirectory
    if subdirectory == 'cv':
        allowed_extensions = ALLOWED_CV_EXTENSIONS
    elif subdirectory == 'certifications':
        allowed_extensions = ALLOWED_CERT_EXTENSIONS
    elif subdirectory == 'announcements':
        allowed_extensions = ALLOWED_ANNOUNCEMENT_EXTENSIONS
    else:
        allowed_extensions = {'pdf'}  # Default to PDF only for unknown subdirectories
    
    if not allowed_file_extension(file.filename, allowed_extensions):
        return False, f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}'
    
    try:
        # Create a unique filename
        original_filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())[:8]  # Using a shorter UUID for filename
        
        # Build the filename
        parts = []
        if file_prefix:
            parts.append(file_prefix)
        if user_id:
            parts.append(user_id)
        parts.append(unique_id)
        parts.append(original_filename)
        
        filename = '_'.join(parts)
        
        # Ensure the subdirectory exists
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subdirectory)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Return the relative path for storing in database
        relative_path = os.path.join(subdirectory, filename)
        
        return True, {
            'relative_path': relative_path,
            'filename': filename
        }
    
    except Exception as e:
        return False, f'Error saving file: {str(e)}'

def get_file(relative_path, as_attachment=True, custom_filename=None):
    """
    Retrieve a file for download based on its relative path.
    
    Args:
        relative_path (str): Relative path of the file from UPLOAD_FOLDER
        as_attachment (bool): Whether to send as attachment (download) or inline
        custom_filename (str, optional): Custom filename for the download
        
    Returns:
        Response: Flask response object with file data or error
    """
    if not relative_path:
        return jsonify({'error': 'No file path provided'}), 404
    
    try:
        # Split the relative path to get directory and filename
        path_parts = relative_path.split(os.path.sep)
        
        if len(path_parts) < 2:
            # If no subdirectory, assume it's directly in UPLOAD_FOLDER
            directory = current_app.config['UPLOAD_FOLDER']
            filename = path_parts[0]
        else:
            # Otherwise, join UPLOAD_FOLDER with the subdirectory
            subdirectory = path_parts[0]
            filename = path_parts[-1]
            directory = os.path.join(current_app.config['UPLOAD_FOLDER'], subdirectory)
        
        # For security, validate that the file exists within allowed directories
        if not os.path.exists(os.path.join(directory, filename)):
            return jsonify({'error': 'File not found'}), 404
        
        # Send the file
        download_name = custom_filename if custom_filename else filename
        return send_from_directory(
            directory, 
            filename,
            as_attachment=as_attachment,
            download_name=download_name
        )
    
    except Exception as e:
        return jsonify({'error': f'Error retrieving file: {str(e)}'}), 500

def delete_file(relative_path):
    """
    Delete a file based on its relative path.
    
    Args:
        relative_path (str): Relative path of the file from UPLOAD_FOLDER
        
    Returns:
        tuple: (success, message)
    """
    if not relative_path:
        return False, 'No file path provided'
    
    try:
        # Get the absolute path
        abs_path = os.path.join(current_app.config['UPLOAD_FOLDER'], relative_path)
        
        # For security, validate that the file exists within UPLOAD_FOLDER
        if not os.path.abspath(abs_path).startswith(
            os.path.abspath(current_app.config['UPLOAD_FOLDER'])
        ):
            return False, 'Invalid file path'
        
        # Check if file exists
        if not os.path.exists(abs_path):
            return False, 'File not found'
        
        # Delete the file
        os.remove(abs_path)
        return True, 'File deleted successfully'
    
    except Exception as e:
        return False, f'Error deleting file: {str(e)}'