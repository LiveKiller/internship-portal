from flask import Blueprint, jsonify

# Import all route modules
from app.routes.api.auth import auth_routes
from app.routes.api.admin import admin_routes, analytics_routes
from app.routes.api.student import dashboard_routes, profile_routes, portfolio_routes
from app.routes.api.student import notifications_routes, announcement_routes, recommendations_routes, messages_routes
from app.routes.api.company import company_routes
from app.routes.api.search import search_routes

# Create main API blueprint
api_bp = Blueprint('api', __name__)

# Register all route blueprints
# Register all route blueprints with correct names
try:
    api_bp.register_blueprint(auth_routes.auth_bp, url_prefix='/auth')
except AttributeError:
    print("Warning: auth_bp not found in auth_routes")

try:
    api_bp.register_blueprint(admin_routes.admin_bp, url_prefix='/admin')
except AttributeError:
    print("Warning: admin_bp not found in admin_routes")

try:
    api_bp.register_blueprint(analytics_routes.analytics_bp, url_prefix='/admin/analytics')
except AttributeError:
    print("Warning: analytics_bp not found in analytics_routes")

try:
    api_bp.register_blueprint(dashboard_routes.dashboard_bp, url_prefix='/student/dashboard')
except AttributeError:
    print("Warning: dashboard_bp not found in dashboard_routes")

try:
    api_bp.register_blueprint(profile_routes.profile_bp, url_prefix='/student/profile')
except AttributeError:
    print("Warning: profile_bp not found in profile_routes")

try:
    api_bp.register_blueprint(portfolio_routes.portfolio_bp, url_prefix='/student/portfolio')
except AttributeError:
    print("Warning: portfolio_bp not found in portfolio_routes")

try:
    api_bp.register_blueprint(notifications_routes.notification_bp, url_prefix='/student/notifications')
except AttributeError:
    print("Warning: notification_bp not found in notifications_routes")

try:
    api_bp.register_blueprint(announcement_routes.announcement_bp, url_prefix='/student/announcements')
except AttributeError:
    print("Warning: announcement_bp not found in announcement_routes")

try:
    api_bp.register_blueprint(recommendations_routes.recommendation_bp, url_prefix='/student/recommendations')
except AttributeError:
    print("Warning: recommendation_bp not found in recommendations_routes")

try:
    api_bp.register_blueprint(messages_routes.message_bp, url_prefix='/student/messages')
except AttributeError:
    print("Warning: message_bp not found in messages_routes")

try:
    api_bp.register_blueprint(company_routes.company_bp, url_prefix='/company')
except AttributeError:
    print("Warning: company_bp not found in company_routes")

try:
    api_bp.register_blueprint(search_routes.search_bp, url_prefix='/search')
except AttributeError:
    print("Warning: search_bp not found in search_routes")

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
