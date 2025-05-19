from datetime import datetime
from app import db

class Admin:
    @staticmethod
    def create_admin(username, password_hash, access_key):
        """Create a new admin user."""
        admin = {
            'username': username,
            'password': password_hash,
            'access_key': access_key,
            'created_at': datetime.utcnow(),
            'last_login': None,
            'is_active': True
        }
        return db.admins.insert_one(admin)

    @staticmethod
    def get_admin_by_username(username):
        """Get admin by username."""
        return db.admins.find_one({'username': username})

    @staticmethod
    def update_last_login(admin_id):
        """Update last login time."""
        return db.admins.update_one(
            {'_id': admin_id},
            {'$set': {'last_login': datetime.utcnow()}}
        ) 