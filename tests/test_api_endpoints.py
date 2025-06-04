import unittest
import json
import os
import sys
from datetime import datetime
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.datastructures import Headers

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.config import TestConfig

class APITestCase(unittest.TestCase):
    """Test case for the API endpoints"""

    def setUp(self):
        """Set up test client and other test variables."""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.client.testing = True
        
        # Create test user credentials
        self.student_credentials = {
            "registration_no": "TEST123",
            "password": "testpassword"
        }
        
        self.admin_credentials = {
            "username": "admin",
            "password": "admin@savi"
        }
        
        # Authentication tokens
        self.student_token = None
        self.admin_token = None
        
        # Test data
        self.test_company = {
            "name": "Test Company",
            "description": "A test company for API testing",
            "website": "https://testcompany.com",
            "logo_url": "https://testcompany.com/logo.png",
            "industry": "Technology",
            "location": "Test Location",
            "positions": ["Software Engineer", "Data Scientist"],
            "requirements": ["Python", "Flask", "MongoDB"],
            "deadline": int(datetime.now().timestamp()) + 604800,  # 1 week from now
            "active": True
        }
        
        self.test_announcement = {
            "title": "Test Announcement",
            "content": "This is a test announcement",
            "important": True
        }
        
        self.test_message = {
            "recipient_id": "TEST456",
            "content": "This is a test message",
            "subject": "Test Subject"
        }
        
        self.test_experience = {
            "company_name": "Test Company",
            "position": "Test Position",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "description": "This is a test experience",
            "skills_used": ["Python", "Flask", "MongoDB"]
        }
        
        self.test_project = {
            "project_name": "Test Project",
            "description": "This is a test project",
            "technologies_used": ["Python", "Flask", "MongoDB"],
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "github_link": "https://github.com/test/test-project",
            "live_link": "https://test-project.com"
        }
        
        # Initialize test database
        with self.app.app_context():
            # Clear existing data and populate with test data
            try:
                from app import db
                # Drop existing collections
                db.students.drop()
                db.companies.drop()
                db.announcements.drop()
                db.messages.drop()
                db.applications.drop()
                
                # Create test student
                db.students.insert_one({
                    "registration_no": "TEST123",
                    "password": "$2b$12$rj8MnLcKBxAgL7GUHvYkNuRZD0T9nMM6NrVJx5SJVeEHhlR6NJKH2",  # hashed 'testpassword'
                    "name": "Test Student",
                    "email": "test@example.com",
                    "phone": "1234567890",
                    "course": "Test Course",
                    "branch": "Test Branch",
                    "year": 3,
                    "cgpa": 8.5,
                    "registered": True,
                    "skills": {
                        "technical": ["Python", "Flask", "MongoDB"],
                        "non_technical": ["Communication", "Teamwork"]
                    },
                    "experience": [],
                    "projects": [],
                    "certifications": []
                })
                
                # Create another test student for messaging
                db.students.insert_one({
                    "registration_no": "TEST456",
                    "password": "$2b$12$rj8MnLcKBxAgL7GUHvYkNuRZD0T9nMM6NrVJx5SJVeEHhlR6NJKH2",  # hashed 'testpassword'
                    "name": "Another Test Student",
                    "email": "another@example.com",
                    "phone": "0987654321",
                    "course": "Test Course",
                    "branch": "Test Branch",
                    "year": 2,
                    "cgpa": 9.0,
                    "registered": True
                })
                
                # Create test company
                company_id = db.companies.insert_one({
                    "name": "Existing Test Company",
                    "description": "An existing test company",
                    "website": "https://existingtestcompany.com",
                    "logo_url": "https://existingtestcompany.com/logo.png",
                    "industry": "Technology",
                    "location": "Existing Test Location",
                    "positions": ["Software Engineer"],
                    "requirements": ["Python"],
                    "deadline": int(datetime.now().timestamp()) + 604800,
                    "active": True
                }).inserted_id
                
                # Create test announcement
                db.announcements.insert_one({
                    "title": "Existing Test Announcement",
                    "content": "This is an existing test announcement",
                    "date": datetime.now(),
                    "important": False,
                    "attachment": "",
                    "posted_by": "admin"
                })
                
                # Create test application
                db.applications.insert_one({
                    "student_id": "TEST123",
                    "company_id": company_id,
                    "status": "pending",
                    "applied_date": datetime.now(),
                    "resume_url": "test_resume.pdf"
                })
                
                print("Test database initialized successfully")
            except Exception as e:
                print(f"Error initializing test database: {str(e)}")

    def tearDown(self):
        """Tear down all initialized variables."""
        pass

    def get_auth_headers(self, token):
        """Helper method to get authentication headers."""
        return Headers({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        })

    def login_student(self):
        """Helper method to log in as a student and get a token."""
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps(self.student_credentials),
            content_type='application/json'
        )
        data = json.loads(response.data)
        self.student_token = data.get('access_token')
        return self.student_token

    def login_admin(self):
        """Helper method to log in as an admin and get a token."""
        response = self.client.post(
            '/api/admin/login',
            data=json.dumps(self.admin_credentials),
            content_type='application/json'
        )
        data = json.loads(response.data)
        self.admin_token = data.get('access_token')
        return self.admin_token

    # AUTH TESTS
    def test_1_auth_signup(self):
        """Test user signup."""
        signup_data = {
            "registration_no": "TEST789",
            "password": "testpassword",
            "name": "New Test Student",
            "email": "newtest@example.com",
            "phone": "5555555555",
            "course": "Test Course",
            "branch": "Test Branch",
            "year": 1,
            "cgpa": 8.0
        }
        
        response = self.client.post(
            '/api/auth/signup',
            data=json.dumps(signup_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'User registered successfully')

    def test_2_auth_login(self):
        """Test user login."""
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps(self.student_credentials),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.student_token = data['access_token']

    def test_3_auth_check_auth(self):
        """Test check auth endpoint."""
        token = self.login_student()
        
        response = self.client.get(
            '/api/auth/check-auth',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['authenticated'], True)

    # ADMIN TESTS
    def test_4_admin_login(self):
        """Test admin login."""
        response = self.client.post(
            '/api/admin/login',
            data=json.dumps(self.admin_credentials),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
        self.admin_token = data['access_token']

    def test_5_admin_dashboard(self):
        """Test admin dashboard endpoint."""
        token = self.login_admin()
        
        response = self.client.get(
            '/api/admin/dashboard',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('stats', data)

    def test_6_admin_list_users(self):
        """Test admin list users endpoint."""
        token = self.login_admin()
        
        response = self.client.get(
            '/api/admin/users',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('users', data)

    def test_7_admin_get_user(self):
        """Test admin get user endpoint."""
        token = self.login_admin()
        
        response = self.client.get(
            '/api/admin/users/TEST123',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('user', data)

    def test_8_admin_list_companies(self):
        """Test admin list companies endpoint."""
        token = self.login_admin()
        
        response = self.client.get(
            '/api/admin/companies',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('companies', data)

    def test_9_admin_create_company(self):
        """Test admin create company endpoint."""
        token = self.login_admin()
        
        response = self.client.post(
            '/api/admin/companies/create',
            data=json.dumps(self.test_company),
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('company', data)
        self.company_id = data['company']['_id']

    def test_10_admin_create_announcement(self):
        """Test admin create announcement endpoint."""
        token = self.login_admin()
        
        response = self.client.post(
            '/api/admin/announcements',
            data=json.dumps(self.test_announcement),
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('announcement', data)

    # STUDENT TESTS
    def test_11_student_profile(self):
        """Test student profile endpoint."""
        token = self.login_student()
        
        response = self.client.get(
            '/api/student/profile/',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('profile', data)

    def test_12_student_update_profile(self):
        """Test student update profile endpoint."""
        token = self.login_student()
        
        update_data = {
            "name": "Updated Test Student",
            "email": "updated@example.com"
        }
        
        response = self.client.put(
            '/api/student/profile/update',
            data=json.dumps(update_data),
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Profile updated successfully')

    def test_13_student_add_experience(self):
        """Test student add experience endpoint."""
        token = self.login_student()
        
        response = self.client.post(
            '/api/student/profile/add-experience',
            data=json.dumps(self.test_experience),
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('experience', data)

    def test_14_student_add_project(self):
        """Test student add project endpoint."""
        token = self.login_student()
        
        response = self.client.post(
            '/api/student/profile/add-project',
            data=json.dumps(self.test_project),
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('project', data)

    def test_15_student_update_skills(self):
        """Test student update skills endpoint."""
        token = self.login_student()
        
        skills_data = {
            "technical": ["Python", "Flask", "MongoDB", "React"],
            "non_technical": ["Communication", "Teamwork", "Leadership"]
        }
        
        response = self.client.put(
            '/api/student/profile/update-skills',
            data=json.dumps(skills_data),
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Skills updated successfully')

    def test_16_student_get_portfolio(self):
        """Test student get portfolio endpoint."""
        token = self.login_student()
        
        response = self.client.get(
            '/api/student/portfolio/',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('portfolio', data)

    def test_17_student_dashboard(self):
        """Test student dashboard endpoint."""
        token = self.login_student()
        
        response = self.client.get(
            '/api/student/dashboard/',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)

    def test_18_student_dashboard_stats(self):
        """Test student dashboard stats endpoint."""
        token = self.login_student()
        
        response = self.client.get(
            '/api/student/dashboard/stats',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)

    def test_19_student_get_announcements(self):
        """Test student get announcements endpoint."""
        token = self.login_student()
        
        response = self.client.get(
            '/api/student/announcements/',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('announcements', data)

    def test_20_student_get_important_announcements(self):
        """Test student get important announcements endpoint."""
        token = self.login_student()
        
        response = self.client.get(
            '/api/student/announcements/important',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('announcements', data)

    def test_21_student_get_recent_announcements(self):
        """Test student get recent announcements endpoint."""
        token = self.login_student()
        
        response = self.client.get(
            '/api/student/announcements/recent',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('announcements', data)

    def test_22_student_get_notifications(self):
        """Test student get notifications endpoint."""
        token = self.login_student()
        
        response = self.client.get(
            '/api/student/notifications/',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)

    def test_23_student_get_unread_count(self):
        """Test student get unread notifications count endpoint."""
        token = self.login_student()
        
        response = self.client.get(
            '/api/student/notifications/unread-count',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('unread_count', data)

    def test_24_student_send_message(self):
        """Test student send message endpoint."""
        token = self.login_student()
        
        response = self.client.post(
            '/api/student/messages/send',
            data=json.dumps(self.test_message),
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('message_id', data)
        self.message_id = data['message_id']

    def test_25_student_get_messages(self):
        """Test student get messages endpoint."""
        token = self.login_student()
        
        # First send a message
        self.test_24_student_send_message()
        
        response = self.client.get(
            '/api/student/messages/',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('messages', data)

    def test_26_student_get_message(self):
        """Test student get specific message endpoint."""
        token = self.login_student()
        
        # First send a message
        self.test_24_student_send_message()
        
        # Get the message ID from the response
        message_id = self.message_id
        
        response = self.client.get(
            f'/api/student/messages/{message_id}',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)

    def test_27_student_delete_message(self):
        """Test student delete message endpoint."""
        token = self.login_student()
        
        # First send a message
        self.test_24_student_send_message()
        
        # Get the message ID from the response
        message_id = self.message_id
        
        response = self.client.delete(
            f'/api/student/messages/{message_id}/delete',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Message deleted successfully')

    # COMPANY TESTS
    def test_28_get_companies(self):
        """Test get companies endpoint."""
        token = self.login_student()
        
        response = self.client.get(
            '/api/company/',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('companies', data)
        
        # Save a company ID for later tests
        if data['companies']:
            self.company_id = data['companies'][0]['_id']

    def test_29_get_company(self):
        """Test get specific company endpoint."""
        token = self.login_student()
        
        # First get all companies
        self.test_28_get_companies()
        
        # Get a company ID
        company_id = self.company_id
        
        response = self.client.get(
            f'/api/company/{company_id}',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('company', data)

    def test_30_apply_to_company(self):
        """Test apply to company endpoint."""
        token = self.login_student()
        
        # First get all companies
        self.test_28_get_companies()
        
        # Get a company ID
        company_id = self.company_id
        
        application_data = {
            "cover_letter": "This is a test cover letter",
            "resume_url": "test_resume.pdf"
        }
        
        response = self.client.post(
            f'/api/company/{company_id}/apply',
            data=json.dumps(application_data),
            headers=self.get_auth_headers(token)
        )
        
        # This might fail if the student has already applied to this company
        # So we'll accept either 201 (created) or 400 (already applied)
        self.assertIn(response.status_code, [201, 400])

    def test_31_get_application_status(self):
        """Test get application status endpoint."""
        token = self.login_student()
        
        # First get all companies
        self.test_28_get_companies()
        
        # Get a company ID
        company_id = self.company_id
        
        response = self.client.get(
            f'/api/company/{company_id}/status',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)

    # SEARCH TESTS
    def test_32_search_companies(self):
        """Test search companies endpoint."""
        token = self.login_student()
        
        response = self.client.get(
            '/api/search/companies?query=test',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('results', data)

    def test_33_search_students(self):
        """Test search students endpoint."""
        token = self.login_admin()
        
        response = self.client.get(
            '/api/search/students?query=test',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('results', data)

    def test_34_search_announcements(self):
        """Test search announcements endpoint."""
        token = self.login_student()
        
        response = self.client.get(
            '/api/search/announcements?query=test',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('results', data)

    def test_35_global_search(self):
        """Test global search endpoint."""
        token = self.login_student()
        
        response = self.client.get(
            '/api/search/global?query=test',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('results', data)

    # FACULTY TESTS
    def test_36_faculty_dashboard(self):
        """Test faculty dashboard endpoint."""
        token = self.login_admin()  # Using admin token for faculty endpoints
        
        response = self.client.get(
            '/api/faculty/dashboard/',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)

    def test_37_faculty_stats(self):
        """Test faculty stats endpoint."""
        token = self.login_admin()  # Using admin token for faculty endpoints
        
        response = self.client.get(
            '/api/faculty/dashboard/stats',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)

    def test_38_faculty_students(self):
        """Test faculty students endpoint."""
        token = self.login_admin()  # Using admin token for faculty endpoints
        
        response = self.client.get(
            '/api/faculty/dashboard/students',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)

    # RECOMMENDATIONS TESTS
    def test_39_get_recommended_companies(self):
        """Test get recommended companies endpoint."""
        token = self.login_student()
        
        response = self.client.get(
            '/api/student/recommendations/companies',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)

    def test_40_get_trending_companies(self):
        """Test get trending companies endpoint."""
        token = self.login_student()
        
        response = self.client.get(
            '/api/student/recommendations/trending',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)

    def test_41_get_similar_companies(self):
        """Test get similar companies endpoint."""
        token = self.login_student()
        
        # First get all companies
        self.test_28_get_companies()
        
        # Get a company ID
        company_id = self.company_id
        
        response = self.client.get(
            f'/api/student/recommendations/similar-companies/{company_id}',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)

    # ANALYTICS TESTS
    def test_42_get_analytics_overview(self):
        """Test get analytics overview endpoint."""
        token = self.login_admin()
        
        response = self.client.get(
            '/api/admin/analytics/overview',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)

    def test_43_get_application_timeline(self):
        """Test get application timeline endpoint."""
        token = self.login_admin()
        
        response = self.client.get(
            '/api/admin/analytics/applications/timeline',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)

    def test_44_get_popular_companies(self):
        """Test get popular companies endpoint."""
        token = self.login_admin()
        
        response = self.client.get(
            '/api/admin/analytics/companies/popular',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)

    def test_45_get_student_activity(self):
        """Test get student activity endpoint."""
        token = self.login_admin()
        
        response = self.client.get(
            '/api/admin/analytics/students/activity',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)

    def test_46_get_monthly_report(self):
        """Test get monthly report endpoint."""
        token = self.login_admin()
        
        response = self.client.get(
            '/api/admin/analytics/monthly-report',
            headers=self.get_auth_headers(token)
        )
        
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main() 