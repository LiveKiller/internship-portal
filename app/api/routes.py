from flask import Blueprint, jsonify

from app.api.dashboard import dashboard_bp
from app.api.announcement import announcement_bp
from app.api.messages import messages_bp
from app.api.profile import profile_bp
from app.api.portfolio import portfolio_bp

api_bp = Blueprint('api', __name__)

# Register API submodules
api_bp.register_blueprint(dashboard_bp, url_prefix='/dashboard')
api_bp.register_blueprint(announcement_bp, url_prefix='/announcement')
api_bp.register_blueprint(messages_bp, url_prefix='/messages')
api_bp.register_blueprint(profile_bp, url_prefix='/profile')
api_bp.register_blueprint(portfolio_bp, url_prefix='/portfolio')

# Debug route
@api_bp.route('/debug', methods=['GET'])
def debug():
    """Debug route to check database connection and collections."""
    from app import db
    import pymongo
    import os
    
    try:
        debug_info = {
            'database_connection': 'Connected',
            'database_name': db.name,
            'collections': db.list_collection_names(),
            'uploads_directory': os.path.exists('app/uploads'),
            'upload_subdirectories': {
                'cv': os.path.exists('app/uploads/cv'),
                'certifications': os.path.exists('app/uploads/certifications'),
                'announcements': os.path.exists('app/uploads/announcements')
            },
            'pymongo_version': pymongo.__version__
        }
        
        # Check if we can actually query the database
        try:
            students_count = db.students.count_documents({})
            debug_info['students_count'] = students_count
        except Exception as e:
            debug_info['students_query_error'] = str(e)
        
        return jsonify({
            'status': 'success',
            'debug_info': debug_info
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Debug information could not be retrieved',
            'error': str(e)
        }), 500