from flask import Blueprint, jsonify

# Import all route modules
from app.routes.api.auth import auth_routes
from app.routes.api.admin import admin_routes, analytics_routes
from app.routes.api.student import dashboard_routes, profile_routes, portfolio_routes
from app.routes.api.student import notifications_routes, announcement_routes, recommendations_routes
from app.routes.api.company import company_routes
from app.routes.api.search import search_routes

# Import archive messages
from app.archive import messages

# Import new unified routes
from app.routes import dashboard, profile

# Create main API blueprint
api_bp = Blueprint('api', __name__)

# Register all route blueprints
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

# Register unified role-based routes
try:
    api_bp.register_blueprint(dashboard.dashboard_bp, url_prefix='/dashboard')
except AttributeError:
    print("Warning: dashboard_bp not found in dashboard")

try:
    api_bp.register_blueprint(profile.profile_bp, url_prefix='/profile')
except AttributeError:
    print("Warning: profile_bp not found in profile")

# Register old routes for backward compatibility
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
    api_bp.register_blueprint(notifications_routes.notification_bp, url_prefix='/notifications')
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

# Register archived message routes
try:
    api_bp.register_blueprint(messages.message_bp, url_prefix='/messages')
except AttributeError:
    print("Warning: message_bp not found in messages")

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
    from app import db, mongo
    
    try:
        # Test MongoDB connection
        mongo.admin.command('ping')
        
        # Get basic debug info
        debug_info = {
            'database_name': db.name,
            'collections': db.list_collection_names(),
            'students_count': db.students.count_documents({})
        }
        
        return jsonify({
            'status': 'success',
            'debug_info': debug_info
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Firebase test route
@api_bp.route('/firebase-test', methods=['GET'])
def firebase_test():
    """Test route to verify Firebase connection."""
    from app.utils.firebase_setup import initialize_firebase, push_test_message
    
    try:
        # Initialize Firebase
        firebase_initialized = initialize_firebase()
        
        if not firebase_initialized:
            return jsonify({
                'status': 'error',
                'message': 'Firebase initialization failed'
            }), 500
        
        # Push test message
        message_sent = push_test_message()
        
        if message_sent:
            return jsonify({
                'status': 'success',
                'message': 'Firebase test message sent successfully'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to send Firebase test message'
            }), 500
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Dummy data population route
@api_bp.route('/populate-dummy-data', methods=['POST'])
def populate_dummy_data_route():
    """Route to populate the database with dummy data for testing."""
    from app.utils.dummy_data import populate_dummy_data
    
    try:
        # Populate dummy data
        summary = populate_dummy_data()
        
        return jsonify({
            'status': 'success',
            'message': 'Dummy data populated successfully',
            'summary': summary
        }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
