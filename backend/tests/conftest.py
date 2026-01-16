import pytest
from app import create_app
from app.models import db, User, Team, PrivateTodo, TeamTask, SubTask


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def team(app):
    """Create a test team."""
    with app.app_context():
        team = Team(name='Test Team')
        db.session.add(team)
        db.session.commit()
        team_id = team.id
    return team_id


@pytest.fixture
def admin_user(app, team):
    """Create an admin user."""
    with app.app_context():
        user = User(
            name='Admin User',
            email='admin@test.com',
            role='ADMIN',
            team_id=team
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    return user_id


@pytest.fixture
def member_user(app, team):
    """Create a member user."""
    with app.app_context():
        user = User(
            name='Member User',
            email='member@test.com',
            role='MEMBER',
            team_id=team
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    return user_id


@pytest.fixture
def admin_token(client, admin_user):
    """Get JWT token for admin user."""
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'password123'
    })
    return response.get_json()['data']['access_token']


@pytest.fixture
def member_token(client, member_user):
    """Get JWT token for member user."""
    response = client.post('/api/auth/login', json={
        'email': 'member@test.com',
        'password': 'password123'
    })
    return response.get_json()['data']['access_token']


def auth_header(token):
    """Create authorization header."""
    return {'Authorization': f'Bearer {token}'}
