import os
from flask import Flask
from pymongo import MongoClient
from flask_jwt_extended import JWTManager
from app.config import Config

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
    
    # Initialize MongoDB connection
    global mongo, db
    mongo = MongoClient(app.config['MONGO_URI'])
    db = mongo.get_database()
    
    # Create uploads directory structure if it doesn't exist
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'cv'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'certifications'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'announcements'), exist_ok=True)
    
    # Initialize database schemas
    from app.models.student import initialize_db_schemas
    initialize_db_schemas()
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.api.routes import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        return {
            'message': 'Welcome to the Internship Portal API',
            'status': 'running'
        }
    
    return app