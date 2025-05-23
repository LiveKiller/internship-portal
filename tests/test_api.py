import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import random
import string
from app import create_app
import unittest
import json
from app.config import Config
from app import db

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def random_digits(n):
    return ''.join(random.choice(string.digits) for _ in range(n))


def test_index(client):
    rv = client.get('/')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['status'] == 'running'


def test_debug(client):
    rv = client.get('/api/debug')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['status'] == 'success'
    assert 'database_name' in data['debug_info']


def test_signup_missing_fields(client):
    rv = client.post('/api/auth/signup', json={})
    assert rv.status_code == 400
    data = rv.get_json()
    assert 'error' in data


def test_signup_and_login(client):
    reg_no = random_digits(9)
    email = f"{random_digits(6)}@test.com"
    password = "Password1"
    # Signup
    rv = client.post('/api/auth/signup', json={
        'registration_no': reg_no,
        'email': email,
        'password': password
    })
    assert rv.status_code == 201
    data = rv.get_json()
    assert 'access_token' in data

    # Login
    rv = client.post('/api/auth/login', json={
        'email_id': email,
        'password': password
    })
    assert rv.status_code == 200
    data = rv.get_json()
    token = data.get('access_token')
    assert token


def test_admin_login_and_dashboard(client):
    # Admin login
    rv = client.post('/api/admin/login', json={
        'username': 'savi@admin',
        'password': 'admin@savi'
    })
    assert rv.status_code == 200
    token = rv.get_json().get('access_token')
    assert token
    # Access dashboard
    rv = client.get('/api/admin/dashboard', headers={
        'Authorization': f'Bearer {token}'
    })
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'stats' in data 

def test_admin_token_fixture(client):
    # Ensure admin_token fixture works
    rv = client.post('/api/admin/login', json={'username': 'savi@admin', 'password': 'admin@savi'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'access_token' in data

@pytest.fixture
def admin_token(client):
    rv = client.post('/api/admin/login', json={'username': 'savi@admin', 'password': 'admin@savi'})
    return rv.get_json()['access_token']

@pytest.fixture
def student_credentials(client):
    reg_no = random_digits(9)
    email = f"{random_digits(6)}@test.com"
    password = "Password1"
    # signup
    rv = client.post('/api/auth/signup', json={
        'registration_no': reg_no,
        'email': email,
        'password': password
    })
    assert rv.status_code == 201
    token = rv.get_json()['access_token']
    return {'reg_no': reg_no, 'token': token}

def test_full_company_and_application_flow(client, admin_token, student_credentials):
    # Admin creates a company
    headers_admin = {'Authorization': f'Bearer {admin_token}'}
    rv = client.post('/api/admin/companies', json={'name': 'TestCo', 'job_title': 'Engineer'}, headers=headers_admin)
    assert rv.status_code == 201
    company = rv.get_json()['company']
    cid = company['_id']

    # Student profile access
    headers_student = {'Authorization': f"Bearer {student_credentials['token']}"}
    rv = client.get('/api/profile/', headers=headers_student)
    assert rv.status_code == 200
    profile = rv.get_json()['profile']
    assert profile['registration_no'] == student_credentials['reg_no']

    # Student applies to company
    apply_data = {'coverLetter': 'CL', 'portfolio': 'http://p', 'availability': 'ASAP', 'noticePeriod': 'None'}
    rv = client.post(f'/api/company/{cid}/apply', json=apply_data, headers=headers_student)
    assert rv.status_code == 201
    app_id = rv.get_json()['application_id']

    # Student views own applications
    rv = client.get('/api/company/applications', headers=headers_student)
    assert rv.status_code == 200
    apps = rv.get_json()['applications']
    assert any(a['_id'] == app_id for a in apps)

    # Student checks application status
    rv = client.get(f'/api/company/{cid}/status', headers=headers_student)
    assert rv.status_code == 200
    assert rv.get_json()['status'] == 'pending'

    # Admin views all applications
    rv = client.get('/api/admin/applications', headers=headers_admin)
    assert rv.status_code == 200
    admin_apps = rv.get_json()['applications']
    assert any(a['_id'] == app_id for a in admin_apps)

    # Admin updates application status
    rv = client.put(f'/api/admin/applications/{app_id}/status', json={'status': 'approved'}, headers=headers_admin)
    assert rv.status_code == 200

    # Student sees updated status
    rv = client.get(f'/api/company/{cid}/status', headers=headers_student)
    assert rv.get_json()['application']['status'] == 'approved'

def test_search_endpoints_and_announcements(client, admin_token, student_credentials):
    headers_admin = {'Authorization': f'Bearer {admin_token}'}
    # Admin creates announcement
    rv = client.post('/api/admin/announcements', json={'title': 'TestAnn', 'content': 'Hello'}, headers=headers_admin)
    assert rv.status_code == 201
    ann = rv.get_json()['announcement']
    aid = ann['_id']

    # Search company by keyword
    rv = client.get('/api/search/companies', query_string={'q': 'TestCo'}, headers={'Authorization': f"Bearer {student_credentials['token']}"})
    assert rv.status_code == 200
    results = rv.get_json()['companies']
    assert any(c['name'] == 'TestCo' for c in results)

    # Admin searches students
    rv = client.get('/api/search/students', query_string={'q': student_credentials['reg_no']}, headers=headers_admin)
    assert rv.status_code == 200
    studs = rv.get_json()['students']
    assert any(s['registration_no'] == student_credentials['reg_no'] for s in studs)

    # Search announcements
    rv = client.get('/api/search/announcements', query_string={'q': 'TestAnn'}, headers={'Authorization': f"Bearer {student_credentials['token']}"})
    assert rv.status_code == 200
    anns = rv.get_json()['announcements']
    assert any(a['_id'] == aid for a in anns)

    # Global search
    rv = client.get('/api/search/global', query_string={'q': 'TestAnn'}, headers={'Authorization': f"Bearer {student_credentials['token']}"})
    assert rv.status_code == 200
    glob = rv.get_json()
    assert 'companies' in glob and 'announcements' in glob 

class TestConfig(Config):
    TESTING = True
    MONGO_URI = "mongodb://localhost:27017/internship_portal_test"

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.test_user = {
            "registration_no": "211300001",
            "email": "test@example.com",
            "password": "Test123password",
            "name": "Test User"
        }
        
        # Clear test database collections
        with self.app.app_context():
            db.students.delete_many({})
            db.companies.delete_many({})
            db.notifications.delete_many({})
            db.messages.delete_many({})
    
    def test_signup(self):
        """Test user registration"""
        response = self.client.post('/auth/signup',
                                  json=self.test_user)
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue('access_token' in data)
        self.assertEqual(data['message'], 'User registered successfully')
    
    def test_login(self):
        """Test user login"""
        # First register a user
        self.client.post('/auth/signup', json=self.test_user)
        
        # Then try to login
        response = self.client.post('/auth/login',
                                  json={
                                      "email_id": self.test_user["email"],
                                      "password": self.test_user["password"]
                                  })
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue('access_token' in data)
        self.assertEqual(data['message'], 'Login successful')
    
    def test_protected_route(self):
        """Test accessing a protected route with and without authentication"""
        # Try accessing without token
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, 401)
        
        # Register and get token
        response = self.client.post('/auth/signup', json=self.test_user)
        token = json.loads(response.data)['access_token']
        
        # Try accessing with token
        response = self.client.get('/api/profile/',
                                 headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
    
    def test_profile_update(self):
        """Test profile update functionality"""
        # Register and get token
        response = self.client.post('/auth/signup', json=self.test_user)
        token = json.loads(response.data)['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Update profile
        update_data = {
            "mobile_no": "1234567890",
            "specialization": "Computer Science",
            "year_of_admission": 2021
        }
        
        response = self.client.put('/api/profile/',
                                 json=update_data,
                                 headers=headers)
        self.assertEqual(response.status_code, 200)
        
        # Verify update
        response = self.client.get('/api/profile/', headers=headers)
        data = json.loads(response.data)['profile']
        self.assertEqual(data['mobile_no'], update_data['mobile_no'])
        self.assertEqual(data['specialization'], update_data['specialization'])
        self.assertEqual(data['year_of_admission'], update_data['year_of_admission'])
    
    def test_company_listing(self):
        """Test company listing functionality"""
        # Register and get token
        response = self.client.post('/auth/signup', json=self.test_user)
        token = json.loads(response.data)['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Add a test company to the database
        with self.app.app_context():
            db.companies.insert_one({
                "name": "Test Company",
                "job_title": "Software Engineer Intern",
                "job_type": "Internship",
                "work_place": "Remote",
                "duration": "3 months",
                "stipend": 20000,
                "active": True
            })
        
        # Get company listings
        response = self.client.get('/api/company/', headers=headers)
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['companies']), 1)
        self.assertEqual(data['companies'][0]['name'], "Test Company")
    
    def test_notification_system(self):
        """Test notification functionality"""
        # Register and get token
        response = self.client.post('/auth/signup', json=self.test_user)
        token = json.loads(response.data)['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Add a test notification
        with self.app.app_context():
            db.notifications.insert_one({
                "recipient_id": self.test_user["registration_no"],
                "title": "Test Notification",
                "content": "This is a test notification",
                "read": False
            })
        
        # Get notifications
        response = self.client.get('/api/notifications/', headers=headers)
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['notifications']), 1)
        self.assertEqual(data['notifications'][0]['title'], "Test Notification")

if __name__ == '__main__':
    unittest.main() 