import os
from flask import Flask
from pymongo import MongoClient
from flask_jwt_extended import JWTManager
from app.config import Config
from flask_cors import CORS
import logging
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
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
    
    # Initialize JWT with Flask app
    jwt.init_app(app)
    # Enable CORS
    CORS(app)
    
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
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.routes import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        return {
            'message': 'Welcome to the Internship Portal API',
            'status': 'running'
        }
    
    return app

# Create the application instance
app = create_app()