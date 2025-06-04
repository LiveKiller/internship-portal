import pytest
import json
from app import create_app
from flask_jwt_extended import create_access_token

class TestAPIEndpoints:
    """Test class for API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        app = create_app()
        app.config['TESTING'] = True
        app.config['JWT_SECRET_KEY'] = 'test-secret-key'
        
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def auth_headers(self, client):
        """Create headers with JWT for authenticated requests."""
        # Create a JWT token for test user
        with client.application.app_context():
            access_token = create_access_token(identity='2013XXXXX')
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            return headers
    
    def test_index_route(self, client):
        """Test the index route."""
        response = client.get('/')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'running'
        assert 'message' in data
    
    def test_debug_route(self, client):
        """Test the debug route."""
        response = client.get('/api/debug')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert 'status' in data
    
    def test_dashboard_route_unauthorized(self, client):
        """Test the dashboard route without authentication."""
        response = client.get('/api/dashboard')
        data = json.loads(response.data)
        
        assert response.status_code == 401
        assert 'error' in data
    
    def test_dashboard_route_authorized(self, client, auth_headers, monkeypatch):
        """Test the dashboard route with authentication."""
        # Mock the get_user_role function to return 'student'
        import app.auth.utils
        
        def mock_get_user_role(identity=None):
            return 'student'
        
        monkeypatch.setattr(app.auth.utils, 'get_user_role', mock_get_user_role)
        
        # Mock database calls
        from app import db
        monkeypatch.setattr(db.students, 'find_one', lambda x: {
            'registration_no': '2013XXXXX', 
            'name': {'first': 'Test', 'last': 'User'},
            'companies': {'applied': [], 'rejected': [], 'interviews_attended': [], 'interviews_not_attended': []}
        })
        monkeypatch.setattr(db.announcements, 'find', lambda: MockCursor([]))
        monkeypatch.setattr(db.messages, 'count_documents', lambda x: 0)
        monkeypatch.setattr(db.interviews, 'count_documents', lambda x: 0)
        monkeypatch.setattr(db.companies, 'count_documents', lambda x: 0)
        
        response = client.get('/api/dashboard', headers=auth_headers)
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert 'user' in data
        assert 'stats' in data
    
    def test_profile_route_authorized(self, client, auth_headers, monkeypatch):
        """Test the profile route with authentication."""
        # Mock the get_user_role function to return 'student'
        import app.auth.utils
        
        def mock_get_user_role(identity=None):
            return 'student'
        
        monkeypatch.setattr(app.auth.utils, 'get_user_role', mock_get_user_role)
        
        # Mock database calls
        from app import db
        monkeypatch.setattr(db.students, 'find_one', lambda x: {
            'registration_no': '2013XXXXX', 
            'name': {'first': 'Test', 'last': 'User'}
        })
        
        response = client.get('/api/profile', headers=auth_headers)
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert 'profile' in data

# Helper classes for mocking MongoDB cursors
class MockCursor:
    def __init__(self, items):
        self.items = items
    
    def sort(self, *args, **kwargs):
        return self
    
    def limit(self, *args, **kwargs):
        return self
    
    def __iter__(self):
        return iter(self.items)
    
    def __list__(self):
        return list(self.items) 