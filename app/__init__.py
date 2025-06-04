import os
from flask import Flask
from pymongo import MongoClient
from flask_jwt_extended import JWTManager
from app.config import Config
from flask_cors import CORS
import logging
from urllib.parse import urlparse
from datetime import timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize MongoDB connection
mongo = None
db = None

# Initialize JWT
jwt = JWTManager()

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure JWT settings
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['JWT_ERROR_MESSAGE_KEY'] = 'error'
    
    # Initialize JWT with Flask app
    jwt.init_app(app)
    
    # Configure CORS
    cors_origins = os.environ.get('CORS_ORIGINS', '*')
    if cors_origins != '*':
        cors_origins = cors_origins.split(',')
    
    CORS(app, resources={
        r"/*": {
            "origins": cors_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
        }
    })
    
    # Initialize MongoDB connection
    global mongo, db
    try:
        mongo_uri = app.config['MONGO_URI']
        logger.info(f"Attempting to connect to MongoDB at {mongo_uri.split('@')[-1]}")
        
        # Parse the MongoDB URI to get the database name
        parsed_uri = urlparse(mongo_uri)
        path_parts = parsed_uri.path.split('/')
        db_name = path_parts[1] if len(path_parts) > 1 else None
        
        # If no database name in URI, use default
        if not db_name:
            db_name = 'internship_portal'
            logger.info(f"No database name found in URI, using default: {db_name}")
        else:
            logger.info(f"Using database name from URI: {db_name}")
        
        # Connect to MongoDB
        mongo = MongoClient(mongo_uri)
        # Test the connection
        mongo.admin.command('ping')
        # Get specific database
        db = mongo[db_name]
        logger.info(f"Successfully connected to MongoDB database: {db.name}")
    except Exception as e:
        logger.error(f"MongoDB connection error: {str(e)}")
        # Don't raise the error, let the application start
        # The debug endpoint will show the connection status
    
    # Create uploads directory structure if it doesn't exist
    try:
        upload_base = os.path.abspath(app.config['UPLOAD_FOLDER'])
        logger.info(f"Creating upload directories at: {upload_base}")
        os.makedirs(upload_base, exist_ok=True)
        os.makedirs(os.path.join(upload_base, 'cv'), exist_ok=True)
        os.makedirs(os.path.join(upload_base, 'certifications'), exist_ok=True)
        os.makedirs(os.path.join(upload_base, 'announcements'), exist_ok=True)
        logger.info("Successfully created upload directories")
    except Exception as e:
        logger.error(f"Error creating upload directories: {str(e)}")
    
    # Initialize database schemas
    if db is not None:
        from app.models.student import initialize_db_schemas
        try:
            initialize_db_schemas()
            logger.info("Successfully initialized database schemas")
        except Exception as e:
            logger.error(f"Error initializing database schemas: {str(e)}")
    
    # Import and register blueprints
    # NOTE: Blueprint names have been standardized to avoid conflicts
    
    # Student blueprints with standardized naming and URL prefixes
    from app.routes.api.student.routes import student_bp
    from app.routes.api.student.dashboard_routes import student_dashboard_bp
    from app.routes.api.student.profile_routes import student_profile_bp
    from app.routes.api.student.portfolio_routes import student_portfolio_bp
    from app.routes.api.student.notifications_routes import student_notifications_bp
    from app.routes.api.student.recommendations_routes import student_recommendations_bp
    from app.routes.api.student.announcement_routes import student_announcements_bp
    from app.routes.api.student.messages_routes import message_bp
    
    # Faculty routes
    from app.routes.api.faculty.dashboard_routes import faculty_dashboard_bp
    
    # Archive module for backward compatibility
    from app.archive.messages import messages_bp as archived_messages_bp
    
    # Register student routes directly
    app.register_blueprint(student_bp)  # URL prefix defined in the blueprint
    app.register_blueprint(student_dashboard_bp)  # URL prefix defined in the blueprint
    app.register_blueprint(student_profile_bp)  # URL prefix defined in the blueprint
    app.register_blueprint(student_portfolio_bp)  # URL prefix defined in the blueprint
    app.register_blueprint(student_notifications_bp)  # URL prefix defined in the blueprint
    app.register_blueprint(student_recommendations_bp)  # URL prefix defined in the blueprint
    app.register_blueprint(student_announcements_bp)  # URL prefix defined in the blueprint
    app.register_blueprint(message_bp)  # URL prefix defined in the blueprint
    
    # Register faculty routes directly
    app.register_blueprint(faculty_dashboard_bp)  # URL prefix defined in the blueprint
    
    # Register archive routes for backward compatibility
    app.register_blueprint(archived_messages_bp)  # URL prefix defined in the blueprint
    
    # Import and register the main API blueprint which contains nested blueprints
    # This will handle admin, company, auth, and search routes
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {
            'status': 'error',
            'error': 'Token has expired',
            'message': 'Please log in again to get a new token'
        }, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {
            'status': 'error',
            'error': 'Invalid token',
            'message': 'Token verification failed'
        }, 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return {
            'status': 'error',
            'error': 'Authorization required',
            'message': 'No JWT token provided'
        }, 401
    
    @app.route('/')
    def index():
        return {
            'message': 'Welcome to the Internship Portal API',
            'status': 'running'
        }
    
    return app

# Create the application instance
app = create_app()