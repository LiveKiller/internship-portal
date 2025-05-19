import sys
import os
import time
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
from bson.binary import Binary

def hash_password(password):
    """Hash a password using bcrypt and return as binary."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return Binary(hashed)  # Store as Binary type for MongoDB

def initialize_database():
    """Initialize the database with required data."""
    print("Initializing database...")
    
    # Connect to MongoDB
    mongo_uri = os.environ.get('MONGO_URI', 'mongodb+srv://user-idfk:password%40user-idfk@cluster0.ji3cu1q.mongodb.net/chat_app?retryWrites=true&w=majority')
    
    try:
        client = MongoClient(mongo_uri)
        db_name = mongo_uri.split('/')[-1].split('?')[0]
        db = client[db_name]
        
        # Create admin user if not exists
        admin = db.admins.find_one({'username': 'savi@admin'})
        if not admin:
            print("Creating admin user...")
            admin_data = {
                'username': 'savi@admin',
                'password': hash_password('admin@savi'),
                'access_key': 'admin@123',
                'created_at': time.time(),
                'last_login': None,
                'is_active': True
            }
            db.admins.insert_one(admin_data)
            print("Admin user created")
        else:
            print("Admin user already exists")
            
        # Create test student if not exists
        test_student = db.students.find_one({'email_id': 'test@google.com'})
        if not test_student:
            print("Creating test student...")
            student_data = {
                'name': 'Test Student',
                'roll_number': '2713XXXXX',
                'registration_no': '2713XXXXX',
                'email_id': 'test@google.com',
                'mobile_no': '9999999999',
                'password': hash_password('Test12345'),
                'registered': True,
                'date_of_birth': '',
                'gender': 'Other',
                'category': '',
                'caste': '',
                'aadhar_no': '',
                'parivar_pehchan_patra_id': '',
                'blood_group': '',
                'disability': 'No',
                'address': {
                    'street': '',
                    'pin': '',
                    'district': '',
                    'state': '',
                    'country': ''
                },
                'father': {
                    'name': '',
                    'mobile_no': '',
                    'email_id': ''
                },
                'mother': {
                    'name': '',
                    'mobile_no': '',
                    'email_id': ''
                },
                'specialization': '',
                'pass_out_year': 0,
                'year_of_admission': 0,
                'marks': 0.0,
                'attendance': 0.0,
                'experience': [],
                'skills': {
                    'technical': [],
                    'non_technical': []
                },
                'projects': [],
                'education': {
                    'tenth': 0.0,
                    'twelfth': 0.0,
                    'graduation': ''
                },
                'cv': '',
                'companies': {
                    'applied': [],
                    'rejected': [],
                    'interviews_attended': [],
                    'interviews_not_attended': []
                },
                'certifications': [],
                'messages': ''
            }
            db.students.insert_one(student_data)
            print("Test student created")
        else:
            print("Test student already exists")
            
        # Create test company if not exists
        test_company = db.companies.find_one({'name': 'Test Company'})
        if not test_company:
            print("Creating test company...")
            company_data = {
                'name': 'Test Company',
                'logo': '',
                'job_title': 'Test Engineer',
                'job_description': 'This is a test job posting',
                'job_type': 'Full-time',
                'work_place': 'On-site',
                'duration': '6 months',
                'stipend': 15000,
                'requirements': ['Python', 'MongoDB', 'Flask'],
                'posted_date': time.time(),
                'deadline': time.time() + 30*24*60*60,  # 30 days from now
                'active': True
            }
            db.companies.insert_one(company_data)
            print("Test company created")
        else:
            print("Test company already exists")
            
        print("Database initialization complete")
        return True
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        return False

if __name__ == "__main__":
    initialize_database() 