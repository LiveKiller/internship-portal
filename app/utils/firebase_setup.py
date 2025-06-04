import os
import json
import logging
from datetime import datetime
from firebase_admin import credentials, initialize_app, db as firebase_db, storage as firebase_storage

logger = logging.getLogger(__name__)

# Firebase configuration
firebase_app = None
firebase_bucket = None

def initialize_firebase():
    """Initialize Firebase connection."""
    global firebase_app, firebase_bucket
    
    try:
        # Try to get Firebase credentials from environment variables
        firebase_credentials = os.environ.get('FIREBASE_CREDENTIALS')
        
        if firebase_credentials:
            # If credentials are provided as a JSON string, parse it
            try:
                cred_dict = json.loads(firebase_credentials)
                cred = credentials.Certificate(cred_dict)
            except json.JSONDecodeError:
                # If not a valid JSON, assume it's a path to a service account file
                cred = credentials.Certificate(firebase_credentials)
        else:
            # Check for credentials file
            cred_path = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
            
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
            else:
                logger.warning(f"Firebase credentials not found at {cred_path}")
                return False
        
        # Get Firebase configuration from environment variables
        firebase_config = {
            'databaseURL': os.environ.get('FIREBASE_DATABASE_URL', ''),
            'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET', '')
        }
        
        # Initialize Firebase app
        firebase_app = initialize_app(cred, firebase_config)
        
        # Initialize storage bucket if provided
        if firebase_config.get('storageBucket'):
            firebase_bucket = firebase_storage.bucket()
        
        logger.info("Firebase initialized successfully")
        return True
    
    except Exception as e:
        logger.error(f"Firebase initialization error: {str(e)}")
        return False

def log_to_firebase(action, data, collection='logs'):
    """
    Log an action to Firebase Realtime Database or Firestore.
    
    Args:
        action (str): The action being performed (e.g., 'login', 'application_submit')
        data (dict): The data related to the action
        collection (str): The collection/path to store the log
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not firebase_app:
        logger.warning("Firebase not initialized. Cannot log to Firebase.")
        return False
    
    try:
        # Create a log entry
        log_entry = {
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        # Push to Firebase Realtime Database
        ref = firebase_db.reference(f'/{collection}')
        ref.push(log_entry)
        
        return True
    
    except Exception as e:
        logger.error(f"Error logging to Firebase: {str(e)}")
        return False

def upload_to_firebase_storage(file_path, destination_path):
    """
    Upload a file to Firebase Storage.
    
    Args:
        file_path (str): Local path to the file
        destination_path (str): Destination path in Firebase Storage
        
    Returns:
        str: Public URL of the uploaded file or None if failed
    """
    if not firebase_app or not firebase_bucket:
        logger.warning("Firebase Storage not initialized. Cannot upload file.")
        return None
    
    try:
        blob = firebase_bucket.blob(destination_path)
        blob.upload_from_filename(file_path)
        blob.make_public()
        
        return blob.public_url
    
    except Exception as e:
        logger.error(f"Error uploading to Firebase Storage: {str(e)}")
        return None

def push_test_message():
    """
    Push a test message to Firebase to verify the connection.
    
    Returns:
        bool: True if successful, False otherwise
    """
    return log_to_firebase(
        action='test_connection',
        data={
            'message': 'This is a test message',
            'source': 'Internship Portal API',
            'environment': os.environ.get('FLASK_ENV', 'development')
        },
        collection='test_logs'
    ) 