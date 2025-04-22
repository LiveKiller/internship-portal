"""
Database reset utility script.

This script allows you to reset the MongoDB database by dropping all collections
and reinitializing them with the appropriate schema validation.

Usage: python reset_db.py

This is useful when you need to start fresh or when you've modified the database schema.
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/internship_portal')

def reset_database():
    """Reset the database by dropping all collections and reinitializing them."""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db_name = MONGO_URI.split('/')[-1]
        db = client[db_name]
        
        print(f"Connected to database: {db_name}")
        
        # Get all collections
        collections = db.list_collection_names()
        print(f"Found {len(collections)} collections: {', '.join(collections)}")
        
        # Confirm reset
        confirm = input("Are you sure you want to reset the database? All data will be lost! (y/n): ")
        if confirm.lower() != 'y':
            print("Database reset aborted.")
            return
        
        # Drop all collections
        for collection in collections:
            db.drop_collection(collection)
            print(f"Dropped collection: {collection}")
        
        print("All collections have been dropped.")
        print("\nDatabase has been reset successfully.")
        print("\nCreate sample data? (y/n): ")
        
        create_sample = input()
        if create_sample.lower() == 'y':
            create_sample_data(db)
            print("Sample data created successfully.")
        
        print("\nRestart your application to initialize the database schema.")
        
    except Exception as e:
        print(f"Error resetting database: {e}")
        sys.exit(1)

def create_sample_data(db):
    """Create sample data for testing."""
    # Create admin user
    admin = {
        'name': 'Admin User',
        'roll_number': 'admin',
        'registration_no': 'admin',
        'email_id': 'admin@example.com',
        'mobile_no': '9999999999',
        'password': b'$2b$12$rj7/Y44RdvLRxE0kEm./B.JXxS7X3jU3S8uVl9se/8UQrAEpDPe4W',  # 'admin' hashed
        'registered': True
    }
    db.students.insert_one(admin)
    print("Created admin user (username: admin, password: admin)")
    
    # Create test student
    test_student = {
        'name': 'Test Student',
        'roll_number': '231302050',
        'registration_no': '231302050',
        'email_id': 'test@example.com',
        'mobile_no': '8888888888',
        'password': b'$2b$12$8Xn5vUULMUd0Ncq/UrFCp.VbCN3R0xr3aQiML0hQT62mnJ0d7b9nC',  # '231302050' hashed
        'registered': True,
        'date_of_birth': '2000-01-01',
        'gender': 'Male',
        'category': 'General',
        'skills': {
            'technical': ['Python', 'JavaScript', 'React'],
            'non_technical': ['Communication', 'Teamwork']
        },
        'projects': [
            {
                'project_name': 'Student Portal',
                'project_description': 'A web application for student management',
                'project_link': 'https://github.com/test/student-portal'
            }
        ],
        'experience': [],
        'education': {
            'tenth': 85.5,
            'twelfth': 90.0,
            'graduation': 'B.Tech in CSE'
        },
        'certifications': [],
        'companies': {
            'applied': [],
            'rejected': [],
            'interviews_attended': [],
            'interviews_not_attended': []
        }
    }
    db.students.insert_one(test_student)
    print("Created test student (username: 231302050, password: 231302050)")
    
    # Create sample announcements
    announcements = [
        {
            'title': 'Welcome to Internship Portal',
            'content': 'We are excited to launch the new Internship Portal for students. Please create your account and update your profile.',
            'date': datetime.now(),
            'posted_by': 'admin'
        },
        {
            'title': 'Summer Internship Opportunities',
            'content': 'Several companies have posted summer internship opportunities. Check the portal regularly for updates.',
            'date': datetime.now(),
            'posted_by': 'admin'
        }
    ]
    db.announcements.insert_many(announcements)
    print("Created sample announcements")
    
    # Create sample messages
    messages = [
        {
            'sender_id': 'admin',
            'recipient_id': '231302050',
            'subject': 'Welcome to the portal',
            'content': 'Welcome to the internship portal! Please complete your profile to get started.',
            'timestamp': datetime.now(),
            'read': False
        }
    ]
    db.messages.insert_many(messages)
    print("Created sample messages")

if __name__ == '__main__':
    reset_database()