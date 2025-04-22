import requests
import json
import os
import time
import random
import string

# API Testing Configuration
BASE_URL = "http://localhost:5000"  # Update if using a different host/port
TEST_USER = {
    "registration_no": "231302050",
    "email": "test@example.com",
    "name": "Test User",
    "mobile_no": "9876543210"
}
access_token = None  # Will be set after login

def random_string(length=10):
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def print_test_result(test_name, response):
    """Print test result in a formatted way."""
    print(f"\n=== {test_name} ===")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    
    if 200 <= response.status_code < 300:
        print("✅ Test Passed")
    else:
        print("❌ Test Failed")

def test_signup():
    """Test user signup."""
    url = f"{BASE_URL}/auth/signup"
    response = requests.post(url, json=TEST_USER)
    print_test_result("Signup Test", response)
    return response

def test_login():
    """Test user login."""
    global access_token
    
    url = f"{BASE_URL}/auth/login"
    response = requests.post(url, json={"registration_no": TEST_USER["registration_no"]})
    print_test_result("Login Test", response)
    
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        print(f"Access token: {access_token}")
    
    return response

def test_authentication_check():
    """Test authentication check."""
    url = f"{BASE_URL}/auth/check-auth"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    print_test_result("Authentication Check Test", response)
    return response

def test_get_dashboard():
    """Test getting dashboard data."""
    url = f"{BASE_URL}/api/dashboard/"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    print_test_result("Get Dashboard Test", response)
    return response

def test_get_profile():
    """Test getting user profile."""
    url = f"{BASE_URL}/api/profile/"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    print_test_result("Get Profile Test", response)
    return response

def test_update_profile():
    """Test updating user profile."""
    url = f"{BASE_URL}/api/profile/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    updated_data = {
        "name": "Updated Test User",
        "specialization": "Computer Science",
        "education": {
            "tenth": 85.5,
            "twelfth": 90.0,
            "graduation": "B.Tech in CSE"
        }
    }
    
    response = requests.put(url, json=updated_data, headers=headers)
    print_test_result("Update Profile Test", response)
    return response

def test_add_experience():
    """Test adding work experience."""
    url = f"{BASE_URL}/api/profile/add-experience"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    experience_data = {
        "job_title": "Software Developer Intern",
        "company_name": "Tech Company",
        "start_date": "2023-05-01",
        "end_date": "2023-08-31",
        "description": "Worked on web development projects",
        "skills": ["Python", "JavaScript", "React"]
    }
    
    response = requests.post(url, json=experience_data, headers=headers)
    print_test_result("Add Experience Test", response)
    return response

def test_add_project():
    """Test adding a project."""
    url = f"{BASE_URL}/api/profile/add-project"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    project_data = {
        "project_name": "Student Portal",
        "project_description": "A web application for student management",
        "project_link": "https://github.com/test/student-portal"
    }
    
    response = requests.post(url, json=project_data, headers=headers)
    print_test_result("Add Project Test", response)
    return response

def test_update_skills():
    """Test updating skills."""
    url = f"{BASE_URL}/api/profile/update-skills"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    skills_data = {
        "technical": ["Python", "Flask", "MongoDB", "JavaScript", "Vue.js"],
        "non_technical": ["Communication", "Teamwork", "Problem Solving"]
    }
    
    response = requests.put(url, json=skills_data, headers=headers)
    print_test_result("Update Skills Test", response)
    return response

def test_add_certification():
    """Test adding a certification."""
    url = f"{BASE_URL}/api/profile/add-certification"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    certification_data = {
        "certificate_name": "Web Development Bootcamp",
        "institute_name": "Udemy",
        "verification_link": "https://udemy.com/certificate/123456"
    }
    
    response = requests.post(url, json=certification_data, headers=headers)
    print_test_result("Add Certification Test", response)
    return response

def test_get_portfolio():
    """Test getting portfolio data."""
    url = f"{BASE_URL}/api/portfolio/"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    print_test_result("Get Portfolio Test", response)
    return response

def test_public_portfolio():
    """Test getting public portfolio."""
    url = f"{BASE_URL}/api/portfolio/public/{TEST_USER['registration_no']}"
    response = requests.get(url)
    print_test_result("Get Public Portfolio Test", response)
    return response

def test_get_all_announcements():
    """Test getting all announcements."""
    url = f"{BASE_URL}/api/announcement/"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    print_test_result("Get All Announcements Test", response)
    return response

def test_send_message():
    """Test sending a message."""
    url = f"{BASE_URL}/api/messages/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    message_data = {
        "recipient_id": "admin",  # Usually would be another user's registration number
        "subject": "Test Message",
        "content": "This is a test message content."
    }
    
    response = requests.post(url, json=message_data, headers=headers)
    print_test_result("Send Message Test", response)
    return response

def test_get_all_messages():
    """Test getting all messages."""
    url = f"{BASE_URL}/api/messages/"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    print_test_result("Get All Messages Test", response)
    return response

def run_tests():
    """Run all API tests."""
    print("\n========== STARTING API TESTS ==========\n")
    
    # Authentication tests
    signup_response = test_signup()
    login_response = test_login()
    
    if access_token is None:
        print("❌ Failed to get access token. Aborting remaining tests.")
        return
    
    test_authentication_check()
    
    # User profile tests
    test_get_profile()
    test_update_profile()
    test_add_experience()
    test_add_project()
    test_update_skills()
    test_add_certification()
    
    # Dashboard test
    test_get_dashboard()
    
    # Portfolio tests
    test_get_portfolio()
    test_public_portfolio()
    
    # Announcement tests
    test_get_all_announcements()
    
    # Message tests
    test_send_message()
    test_get_all_messages()
    
    print("\n========== ALL TESTS COMPLETED ==========")

if __name__ == "__main__":
    run_tests()