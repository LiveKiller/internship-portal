"""
Database Fix Script

This script adds a test user to your database that should work with the test script.
It also adds some test data to help with getting started.

Usage: python fix_database.py
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
import bcrypt
from datetime import datetime

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/internship_portal')

def fix_database():
    """Fix the database by adding test users and data."""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db_name = MONGO_URI.split('/')[-1]
        db = client[db_name]
        
        print(f"Connected to database: {db_name}")
        
        # Create or update test user
        test_user = db.students.find_one({"registration_no": "231302050"})
        
        if test_user:
            print("Test user exists, updating password...")
            # Hash the password (same as registration number for testing)
            password = "231302050"
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Update the user
            db.students.update_one(
                {"registration_no": "231302050"},
                {"$set": {"password": hashed}}
            )
        else:
            print("Creating test user...")
            # Hash the password (same as registration number for testing)
            password = "231302050"
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Create minimal test user
            new_user = {
                "name": "Test Student",
                "roll_number": "231302050",
                "registration_no": "231302050",
                "email_id": "test@example.com",
                "mobile_no": "1234567890",
                "password": hashed,
                "registered": True
            }
            
            db.students.insert_one(new_user)
            print("Test user created")
        
        # Check for announcements
        if db.announcements.count_documents({}) == 0:
            print("Adding sample announcements...")
            announcements = [
                {
                    "title": "Welcome to the Internship Portal",
                    "content": "This is a sample announcement for testing purposes.",
                    "date": datetime.now(),
                    "posted_by": "admin"
                },
                {
                    "title": "New Companies Added",
                    "content": "Several new companies have been added to the portal. Check them out!",
                    "date": datetime.now(),
                    "posted_by": "admin"
                }
            ]
            db.announcements.insert_many(announcements)
        
        # Check for admin user
        admin = db.students.find_one({"registration_no": "admin"})
        if not admin:
            print("Creating admin user...")
            admin_password = "admin"
            admin_hashed = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
            
            admin_user = {
                "name": "Admin User",
                "roll_number": "admin",
                "registration_no": "admin",
                "email_id": "admin@example.com",
                "mobile_no": "0000000000",
                "password": admin_hashed,
                "registered": True
            }
            
            db.students.insert_one(admin_user)
            print("Admin user created")
        
        print("\nDatabase has been fixed successfully!")
        print("\nYou can now run the test script with:")
        print("python tests/test_api.py")
        
    except Exception as e:
        print(f"Error fixing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fix_database()