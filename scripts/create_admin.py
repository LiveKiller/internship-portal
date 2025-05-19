import os
import sys
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.auth.utils import hash_password
from app.models.admin import Admin

def create_admin_user():
    """Create the initial admin user."""
    load_dotenv()
    
    app = create_app()
    
    with app.app_context():
        username = os.environ.get('ADMIN_USERNAME')
        password = os.environ.get('ADMIN_PASSWORD')
        access_key = os.environ.get('ADMIN_ACCESS_KEY')
        
        if not all([username, password, access_key]):
            print("Error: Admin credentials not found in environment variables")
            sys.exit(1)
        
        # Check if admin already exists
        existing_admin = Admin.get_admin_by_username(username)
        if existing_admin:
            print(f"Admin user '{username}' already exists")
            sys.exit(0)
        
        # Create admin user
        password_hash = hash_password(password)
        result = Admin.create_admin(username, password_hash, access_key)
        
        if result.inserted_id:
            print(f"Admin user '{username}' created successfully")
        else:
            print("Error creating admin user")
            sys.exit(1)

if __name__ == '__main__':
    create_admin_user() 