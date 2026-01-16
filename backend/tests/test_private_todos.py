import pytest
from app.models import db, PrivateTodo
from tests.conftest import auth_header


class TestPrivateTodos:
    """Test private todo CRUD operations."""

    def test_create_todo(self, client, admin_token):
        """Test creating a private todo."""
        response = client.post('/api/private-todos',
            headers=auth_header(admin_token),
            json={
                'title': 'Test Todo',
                'description': 'Test description',
                'status': 'TODO'
            }
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['title'] == 'Test Todo'
        assert data['data']['status'] == 'TODO'

    def test_create_todo_minimal(self, client, admin_token):
        """Test creating a todo with minimal data."""
        response = client.post('/api/private-todos',
            headers=auth_header(admin_token),
            json={'title': 'Minimal Todo'}
        )
        assert response.status_code == 201

    def test_create_todo_invalid_status(self, client, admin_token):
        """Test creating a todo with invalid status fails."""
        response = client.post('/api/private-todos',
            headers=auth_header(admin_token),
            json={'title': 'Test', 'status': 'INVALID'}
        )
        assert response.status_code == 400

    def test_get_todos(self, client, admin_token):
        """Test getting all user's todos."""
        # Create some todos
        client.post('/api/private-todos',
            headers=auth_header(admin_token),
            json={'title': 'Todo 1'}
        )
        client.post('/api/private-todos',
            headers=auth_header(admin_token),
            json={'title': 'Todo 2'}
        )

        response = client.get('/api/private-todos', headers=auth_header(admin_token))
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['data']) == 2

    def test_get_single_todo(self, client, admin_token):
        """Test getting a single todo."""
        create_response = client.post('/api/private-todos',
            headers=auth_header(admin_token),
            json={'title': 'Test Todo'}
        )
        todo_id = create_response.get_json()['data']['id']

        response = client.get(f'/api/private-todos/{todo_id}',
            headers=auth_header(admin_token)
        )
        assert response.status_code == 200
        assert response.get_json()['data']['title'] == 'Test Todo'

    def test_update_todo(self, client, admin_token):
        """Test updating a todo."""
        create_response = client.post('/api/private-todos',
            headers=auth_header(admin_token),
            json={'title': 'Original'}
        )
        todo_id = create_response.get_json()['data']['id']

        response = client.put(f'/api/private-todos/{todo_id}',
            headers=auth_header(admin_token),
            json={'title': 'Updated', 'status': 'DONE'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['title'] == 'Updated'
        assert data['data']['status'] == 'DONE'

    def test_delete_todo(self, client, admin_token):
        """Test deleting a todo."""
        create_response = client.post('/api/private-todos',
            headers=auth_header(admin_token),
            json={'title': 'To Delete'}
        )
        todo_id = create_response.get_json()['data']['id']

        response = client.delete(f'/api/private-todos/{todo_id}',
            headers=auth_header(admin_token)
        )
        assert response.status_code == 200

        # Verify deletion
        response = client.get(f'/api/private-todos/{todo_id}',
            headers=auth_header(admin_token)
        )
        assert response.status_code == 404


class TestPrivateTodoAuthorization:
    """Test private todo authorization."""

    def test_cannot_access_others_todos(self, client, admin_token, member_token):
        """Test user cannot access another user's todos."""
        # Admin creates a todo
        create_response = client.post('/api/private-todos',
            headers=auth_header(admin_token),
            json={'title': 'Admin Todo'}
        )
        todo_id = create_response.get_json()['data']['id']

        # Member tries to access it
        response = client.get(f'/api/private-todos/{todo_id}',
            headers=auth_header(member_token)
        )
        assert response.status_code == 403

    def test_cannot_update_others_todos(self, client, admin_token, member_token):
        """Test user cannot update another user's todos."""
        create_response = client.post('/api/private-todos',
            headers=auth_header(admin_token),
            json={'title': 'Admin Todo'}
        )
        todo_id = create_response.get_json()['data']['id']

        response = client.put(f'/api/private-todos/{todo_id}',
            headers=auth_header(member_token),
            json={'title': 'Hacked'}
        )
        assert response.status_code == 403

    def test_cannot_delete_others_todos(self, client, admin_token, member_token):
        """Test user cannot delete another user's todos."""
        create_response = client.post('/api/private-todos',
            headers=auth_header(admin_token),
            json={'title': 'Admin Todo'}
        )
        todo_id = create_response.get_json()['data']['id']

        response = client.delete(f'/api/private-todos/{todo_id}',
            headers=auth_header(member_token)
        )
        assert response.status_code == 403

    def test_todos_isolated_between_users(self, client, admin_token, member_token):
        """Test that each user only sees their own todos."""
        # Admin creates todos
        client.post('/api/private-todos',
            headers=auth_header(admin_token),
            json={'title': 'Admin Todo'}
        )

        # Member creates todos
        client.post('/api/private-todos',
            headers=auth_header(member_token),
            json={'title': 'Member Todo'}
        )

        # Admin should only see admin todos
        admin_response = client.get('/api/private-todos',
            headers=auth_header(admin_token)
        )
        assert len(admin_response.get_json()['data']) == 1
        assert admin_response.get_json()['data'][0]['title'] == 'Admin Todo'

        # Member should only see member todos
        member_response = client.get('/api/private-todos',
            headers=auth_header(member_token)
        )
        assert len(member_response.get_json()['data']) == 1
        assert member_response.get_json()['data'][0]['title'] == 'Member Todo'
