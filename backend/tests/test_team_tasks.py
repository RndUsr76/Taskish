import pytest
from app.models import db, TeamTask, SubTask
from tests.conftest import auth_header


class TestTeamTasksCRUD:
    """Test team task CRUD operations."""

    def test_admin_create_task(self, client, admin_token, team):
        """Test admin can create team task."""
        response = client.post('/api/team-tasks',
            headers=auth_header(admin_token),
            json={
                'title': 'Team Task',
                'description': 'Description',
                'status': 'TODO'
            }
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['title'] == 'Team Task'
        assert data['data']['progress'] == 0

    def test_member_cannot_create_task(self, client, member_token):
        """Test member cannot create team task."""
        response = client.post('/api/team-tasks',
            headers=auth_header(member_token),
            json={'title': 'Task'}
        )
        assert response.status_code == 403

    def test_get_team_tasks(self, client, admin_token, member_token, team):
        """Test both admin and member can see team tasks."""
        # Admin creates task
        client.post('/api/team-tasks',
            headers=auth_header(admin_token),
            json={'title': 'Task 1'}
        )

        # Member can see it
        response = client.get('/api/team-tasks', headers=auth_header(member_token))
        assert response.status_code == 200
        assert len(response.get_json()['data']) == 1

    def test_admin_update_task(self, client, admin_token, team):
        """Test admin can update task."""
        create_response = client.post('/api/team-tasks',
            headers=auth_header(admin_token),
            json={'title': 'Original'}
        )
        task_id = create_response.get_json()['data']['id']

        response = client.put(f'/api/team-tasks/{task_id}',
            headers=auth_header(admin_token),
            json={'title': 'Updated'}
        )
        assert response.status_code == 200
        assert response.get_json()['data']['title'] == 'Updated'

    def test_member_cannot_update_task(self, client, admin_token, member_token, team):
        """Test member cannot update task."""
        create_response = client.post('/api/team-tasks',
            headers=auth_header(admin_token),
            json={'title': 'Task'}
        )
        task_id = create_response.get_json()['data']['id']

        response = client.put(f'/api/team-tasks/{task_id}',
            headers=auth_header(member_token),
            json={'title': 'Hacked'}
        )
        assert response.status_code == 403

    def test_admin_delete_task(self, client, admin_token, team):
        """Test admin can delete task."""
        create_response = client.post('/api/team-tasks',
            headers=auth_header(admin_token),
            json={'title': 'Task'}
        )
        task_id = create_response.get_json()['data']['id']

        response = client.delete(f'/api/team-tasks/{task_id}',
            headers=auth_header(admin_token)
        )
        assert response.status_code == 200


class TestTaskAssignment:
    """Test task assignment functionality."""

    def test_admin_assign_task(self, client, admin_token, member_user, team):
        """Test admin can assign task to member."""
        create_response = client.post('/api/team-tasks',
            headers=auth_header(admin_token),
            json={'title': 'Task'}
        )
        task_id = create_response.get_json()['data']['id']

        response = client.patch(f'/api/team-tasks/{task_id}/assign',
            headers=auth_header(admin_token),
            json={'assigned_user_id': member_user}
        )
        assert response.status_code == 200
        assert response.get_json()['data']['assigned_user_id'] == member_user

    def test_member_cannot_assign_task(self, client, admin_token, member_token, team):
        """Test member cannot assign task."""
        create_response = client.post('/api/team-tasks',
            headers=auth_header(admin_token),
            json={'title': 'Task'}
        )
        task_id = create_response.get_json()['data']['id']

        response = client.patch(f'/api/team-tasks/{task_id}/assign',
            headers=auth_header(member_token),
            json={'assigned_user_id': 1}
        )
        assert response.status_code == 403


class TestStatusUpdates:
    """Test status update functionality."""

    def test_assigned_user_can_update_status(self, client, admin_token, member_token, member_user, team):
        """Test assigned user can update task status."""
        # Admin creates and assigns task
        create_response = client.post('/api/team-tasks',
            headers=auth_header(admin_token),
            json={'title': 'Task', 'assigned_user_id': member_user}
        )
        task_id = create_response.get_json()['data']['id']

        # Member updates status
        response = client.patch(f'/api/team-tasks/{task_id}/status',
            headers=auth_header(member_token),
            json={'status': 'IN_PROGRESS'}
        )
        assert response.status_code == 200
        assert response.get_json()['data']['status'] == 'IN_PROGRESS'

    def test_unassigned_member_cannot_update_status(self, client, admin_token, member_token, admin_user, team):
        """Test unassigned member cannot update task status."""
        # Admin creates task assigned to admin
        create_response = client.post('/api/team-tasks',
            headers=auth_header(admin_token),
            json={'title': 'Task', 'assigned_user_id': admin_user}
        )
        task_id = create_response.get_json()['data']['id']

        # Member tries to update status
        response = client.patch(f'/api/team-tasks/{task_id}/status',
            headers=auth_header(member_token),
            json={'status': 'IN_PROGRESS'}
        )
        assert response.status_code == 403

    def test_admin_can_update_any_status(self, client, admin_token, member_user, team):
        """Test admin can update status of any task."""
        create_response = client.post('/api/team-tasks',
            headers=auth_header(admin_token),
            json={'title': 'Task', 'assigned_user_id': member_user}
        )
        task_id = create_response.get_json()['data']['id']

        response = client.patch(f'/api/team-tasks/{task_id}/status',
            headers=auth_header(admin_token),
            json={'status': 'DONE'}
        )
        assert response.status_code == 200


class TestSubTasks:
    """Test sub-task operations."""

    def test_admin_create_subtask(self, client, admin_token, team):
        """Test admin can create sub-task."""
        task_response = client.post('/api/team-tasks',
            headers=auth_header(admin_token),
            json={'title': 'Main Task'}
        )
        task_id = task_response.get_json()['data']['id']

        response = client.post(f'/api/team-tasks/{task_id}/sub-tasks',
            headers=auth_header(admin_token),
            json={'title': 'Sub Task'}
        )
        assert response.status_code == 201
        assert response.get_json()['data']['title'] == 'Sub Task'

    def test_member_cannot_create_subtask(self, client, admin_token, member_token, team):
        """Test member cannot create sub-task."""
        task_response = client.post('/api/team-tasks',
            headers=auth_header(admin_token),
            json={'title': 'Main Task'}
        )
        task_id = task_response.get_json()['data']['id']

        response = client.post(f'/api/team-tasks/{task_id}/sub-tasks',
            headers=auth_header(member_token),
            json={'title': 'Sub Task'}
        )
        assert response.status_code == 403

    def test_responsible_user_can_update_subtask_status(self, client, admin_token, member_token, member_user, team):
        """Test responsible user can update sub-task status."""
        # Create task and sub-task
        task_response = client.post('/api/team-tasks',
            headers=auth_header(admin_token),
            json={'title': 'Main Task'}
        )
        task_id = task_response.get_json()['data']['id']

        subtask_response = client.post(f'/api/team-tasks/{task_id}/sub-tasks',
            headers=auth_header(admin_token),
            json={'title': 'Sub Task', 'responsible_user_id': member_user}
        )
        subtask_id = subtask_response.get_json()['data']['id']

        # Member updates status
        response = client.patch(f'/api/team-tasks/{task_id}/sub-tasks/{subtask_id}/status',
            headers=auth_header(member_token),
            json={'status': 'DONE'}
        )
        assert response.status_code == 200
        assert response.get_json()['data']['status'] == 'DONE'

    def test_task_progress_calculated(self, client, admin_token, team):
        """Test task progress is calculated from sub-tasks."""
        # Create main task
        task_response = client.post('/api/team-tasks',
            headers=auth_header(admin_token),
            json={'title': 'Main Task'}
        )
        task_id = task_response.get_json()['data']['id']

        # Create 4 sub-tasks
        for i in range(4):
            client.post(f'/api/team-tasks/{task_id}/sub-tasks',
                headers=auth_header(admin_token),
                json={'title': f'Sub Task {i}'}
            )

        # Check initial progress (0%)
        response = client.get(f'/api/team-tasks/{task_id}',
            headers=auth_header(admin_token)
        )
        assert response.get_json()['data']['progress'] == 0

        # Complete 2 sub-tasks
        sub_tasks = response.get_json()['data']['sub_tasks']
        for st in sub_tasks[:2]:
            client.patch(f'/api/team-tasks/{task_id}/sub-tasks/{st["id"]}/status',
                headers=auth_header(admin_token),
                json={'status': 'DONE'}
            )

        # Check progress (50%)
        response = client.get(f'/api/team-tasks/{task_id}',
            headers=auth_header(admin_token)
        )
        assert response.get_json()['data']['progress'] == 50
