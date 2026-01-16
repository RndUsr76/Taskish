import pytest
from tests.conftest import auth_header


class TestRegistration:
    """Test user registration."""

    def test_register_success(self, client):
        """Test successful registration."""
        response = client.post('/api/auth/register', json={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['user']['email'] == 'test@example.com'
        assert data['data']['user']['role'] == 'ADMIN'  # First user is admin
        assert 'access_token' in data['data']

    def test_register_second_user_is_member(self, client):
        """Test second user gets member role."""
        # First user (admin)
        client.post('/api/auth/register', json={
            'name': 'Admin',
            'email': 'admin@example.com',
            'password': 'password123'
        })
        # Second user (member)
        response = client.post('/api/auth/register', json={
            'name': 'Member',
            'email': 'member@example.com',
            'password': 'password123'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['user']['role'] == 'MEMBER'

    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email fails."""
        client.post('/api/auth/register', json={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123'
        })
        response = client.post('/api/auth/register', json={
            'name': 'Another User',
            'email': 'test@example.com',
            'password': 'password456'
        })
        assert response.status_code == 409
        assert response.get_json()['success'] is False

    def test_register_invalid_email(self, client):
        """Test registration with invalid email fails."""
        response = client.post('/api/auth/register', json={
            'name': 'Test User',
            'email': 'invalid-email',
            'password': 'password123'
        })
        assert response.status_code == 400

    def test_register_short_password(self, client):
        """Test registration with short password fails."""
        response = client.post('/api/auth/register', json={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'short'
        })
        assert response.status_code == 400

    def test_register_missing_fields(self, client):
        """Test registration with missing fields fails."""
        response = client.post('/api/auth/register', json={})
        assert response.status_code == 400


class TestLogin:
    """Test user login."""

    def test_login_success(self, client, admin_user):
        """Test successful login."""
        response = client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'password123'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'access_token' in data['data']
        assert data['data']['user']['email'] == 'admin@test.com'

    def test_login_wrong_password(self, client, admin_user):
        """Test login with wrong password fails."""
        response = client.post('/api/auth/login', json={
            'email': 'admin@test.com',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user fails."""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@test.com',
            'password': 'password123'
        })
        assert response.status_code == 401


class TestCurrentUser:
    """Test getting current user."""

    def test_get_current_user(self, client, admin_token):
        """Test getting current user."""
        response = client.get('/api/auth/me', headers=auth_header(admin_token))
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['email'] == 'admin@test.com'

    def test_get_current_user_no_token(self, client):
        """Test getting current user without token fails."""
        response = client.get('/api/auth/me')
        assert response.status_code == 401


class TestLogout:
    """Test user logout."""

    def test_logout_success(self, client, admin_token):
        """Test successful logout."""
        response = client.post('/api/auth/logout', headers=auth_header(admin_token))
        assert response.status_code == 200

        # Token should be revoked
        response = client.get('/api/auth/me', headers=auth_header(admin_token))
        assert response.status_code == 401
