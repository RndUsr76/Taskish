from flask import Blueprint

# Create blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
users_bp = Blueprint('users', __name__, url_prefix='/api')
private_todos_bp = Blueprint('private_todos', __name__, url_prefix='/api/private-todos')
team_tasks_bp = Blueprint('team_tasks', __name__, url_prefix='/api/team-tasks')

# Import routes to register them
from . import auth, users, private_todos, team_tasks

__all__ = ['auth_bp', 'users_bp', 'private_todos_bp', 'team_tasks_bp']
