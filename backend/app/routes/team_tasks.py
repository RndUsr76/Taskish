import logging
import os
from datetime import datetime
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, TeamTask, SubTask
from app.models.team_task import TaskStatus
from app.models.sub_task import SubTaskStatus
from app.utils.responses import success_response, error_response
from app.utils.decorators import admin_required
from app.utils.validators import validate_title, validate_status
from . import team_tasks_bp

# Set up logging for task creation
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'task_creation.log')

task_logger = logging.getLogger('task_creation')
task_logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
task_logger.addHandler(file_handler)


def get_current_user_or_error():
    """Helper to get current user and return error if not found."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return None, error_response('User not found', 404)
    return user, None


def check_team_access(user, task):
    """Check if user has access to the task's team."""
    if user.team_id != task.team_id:
        return error_response('Access denied', 403)
    return None


# Team Tasks Routes

@team_tasks_bp.route('', methods=['GET'])
@jwt_required()
def get_team_tasks():
    """Get all team tasks for the current user's team."""
    user, error = get_current_user_or_error()
    if error:
        return error

    if not user.team_id:
        return error_response('User is not in a team', 400)

    tasks = TeamTask.query.filter_by(team_id=user.team_id).order_by(TeamTask.created_at.desc()).all()
    return success_response([task.to_dict(include_assigned_user=True) for task in tasks])


@team_tasks_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_team_task():
    """Create a new team task (Admin only)."""
    task_logger.info("="*50)
    task_logger.info("CREATE_TEAM_TASK called")
    task_logger.info(f"Request method: {request.method}")
    task_logger.info(f"Request URL: {request.url}")
    task_logger.info(f"Request headers: {dict(request.headers)}")

    try:
        user, error = get_current_user_or_error()
        task_logger.info(f"User lookup result: user={user}, error={error}")
        if error:
            task_logger.error(f"User lookup failed, returning error: {error}")
            return error

        task_logger.info(f"Current user: id={user.id}, email={user.email}, role={user.role}, team_id={user.team_id}")

        data = request.get_json()
        task_logger.info(f"Request JSON data: {data}")
        task_logger.info(f"Request raw data: {request.data}")

        if not data:
            task_logger.error("No request body provided")
            return error_response('Request body is required', 400)

        # Validate title
        title_value = data.get('title', '')
        task_logger.info(f"Title value: '{title_value}'")
        valid, msg = validate_title(title_value)
        task_logger.info(f"Title validation: valid={valid}, msg={msg}")
        if not valid:
            task_logger.error(f"Title validation failed: {msg}")
            return error_response(msg, 400)

        # Validate status if provided
        status = data.get('status', TaskStatus.TODO.value)
        task_logger.info(f"Status value: '{status}'")
        valid_statuses = [s.value for s in TaskStatus]
        task_logger.info(f"Valid statuses: {valid_statuses}")
        valid, msg = validate_status(status, valid_statuses)
        task_logger.info(f"Status validation: valid={valid}, msg={msg}")
        if not valid:
            task_logger.error(f"Status validation failed: {msg}")
            return error_response(msg, 400)

        # Validate assigned user if provided
        assigned_user_id = data.get('assigned_user_id')
        task_logger.info(f"Assigned user ID: {assigned_user_id}")
        if assigned_user_id:
            assigned_user = User.query.get(assigned_user_id)
            task_logger.info(f"Assigned user lookup: {assigned_user}")
            if not assigned_user or assigned_user.team_id != user.team_id:
                task_logger.error(f"Invalid assigned user: assigned_user={assigned_user}, user.team_id={user.team_id}")
                return error_response('Invalid assigned user', 400)

        task_logger.info(f"Creating TeamTask with: team_id={user.team_id}, title={data['title']}, description={data.get('description')}, status={status}, assigned_user_id={assigned_user_id}")

        task = TeamTask(
            team_id=user.team_id,
            title=data['title'],
            description=data.get('description'),
            status=status,
            assigned_user_id=assigned_user_id
        )

        task_logger.info(f"Task object created: {task}")

        db.session.add(task)
        task_logger.info("Task added to session")

        db.session.commit()
        task_logger.info(f"Task committed to database, id={task.id}")

        result = task.to_dict(include_assigned_user=True)
        task_logger.info(f"Task dict result: {result}")
        task_logger.info("CREATE_TEAM_TASK completed successfully")

        return success_response(result, 'Task created successfully', 201)

    except Exception as e:
        task_logger.exception(f"Exception in create_team_task: {str(e)}")
        db.session.rollback()
        return error_response(f'Internal error: {str(e)}', 500)


@team_tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_team_task(task_id):
    """Get a specific team task with sub-tasks."""
    user, error = get_current_user_or_error()
    if error:
        return error

    task = TeamTask.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)

    error = check_team_access(user, task)
    if error:
        return error

    return success_response(task.to_dict(include_sub_tasks=True, include_assigned_user=True))


@team_tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_team_task(task_id):
    """Update a team task (Admin only)."""
    user, error = get_current_user_or_error()
    if error:
        return error

    task = TeamTask.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)

    error = check_team_access(user, task)
    if error:
        return error

    data = request.get_json()
    if not data:
        return error_response('Request body is required', 400)

    if 'title' in data:
        valid, msg = validate_title(data['title'])
        if not valid:
            return error_response(msg, 400)
        task.title = data['title']

    if 'status' in data:
        valid_statuses = [s.value for s in TaskStatus]
        valid, msg = validate_status(data['status'], valid_statuses)
        if not valid:
            return error_response(msg, 400)
        task.status = data['status']

    if 'description' in data:
        task.description = data['description']

    if 'assigned_user_id' in data:
        if data['assigned_user_id']:
            assigned_user = User.query.get(data['assigned_user_id'])
            if not assigned_user or assigned_user.team_id != user.team_id:
                return error_response('Invalid assigned user', 400)
        task.assigned_user_id = data['assigned_user_id']

    db.session.commit()

    return success_response(task.to_dict(include_assigned_user=True), 'Task updated successfully')


@team_tasks_bp.route('/<int:task_id>/status', methods=['PATCH'])
@jwt_required()
def update_team_task_status(task_id):
    """Update task status (assigned user or admin)."""
    user, error = get_current_user_or_error()
    if error:
        return error

    task = TeamTask.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)

    error = check_team_access(user, task)
    if error:
        return error

    # Check if user is admin or assigned to the task
    if not user.is_admin() and task.assigned_user_id != user.id:
        return error_response('Only the assigned user or admin can update status', 403)

    data = request.get_json()
    if not data or 'status' not in data:
        return error_response('Status is required', 400)

    valid_statuses = [s.value for s in TaskStatus]
    valid, msg = validate_status(data['status'], valid_statuses)
    if not valid:
        return error_response(msg, 400)

    task.status = data['status']
    db.session.commit()

    return success_response(task.to_dict(include_assigned_user=True), 'Status updated successfully')


@team_tasks_bp.route('/<int:task_id>/assign', methods=['PATCH'])
@jwt_required()
@admin_required
def assign_team_task(task_id):
    """Assign task to a user (Admin only)."""
    user, error = get_current_user_or_error()
    if error:
        return error

    task = TeamTask.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)

    error = check_team_access(user, task)
    if error:
        return error

    data = request.get_json()
    if not data:
        return error_response('Request body is required', 400)

    assigned_user_id = data.get('assigned_user_id')
    if assigned_user_id:
        assigned_user = User.query.get(assigned_user_id)
        if not assigned_user or assigned_user.team_id != user.team_id:
            return error_response('Invalid assigned user', 400)

    task.assigned_user_id = assigned_user_id
    db.session.commit()

    return success_response(task.to_dict(include_assigned_user=True), 'Task assigned successfully')


@team_tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_team_task(task_id):
    """Delete a team task (Admin only)."""
    user, error = get_current_user_or_error()
    if error:
        return error

    task = TeamTask.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)

    error = check_team_access(user, task)
    if error:
        return error

    db.session.delete(task)
    db.session.commit()

    return success_response(message='Task deleted successfully')


# Sub-Tasks Routes

@team_tasks_bp.route('/<int:task_id>/sub-tasks', methods=['GET'])
@jwt_required()
def get_sub_tasks(task_id):
    """Get all sub-tasks for a team task."""
    user, error = get_current_user_or_error()
    if error:
        return error

    task = TeamTask.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)

    error = check_team_access(user, task)
    if error:
        return error

    sub_tasks = SubTask.query.filter_by(team_task_id=task_id).order_by(SubTask.created_at.asc()).all()
    return success_response([st.to_dict() for st in sub_tasks])


@team_tasks_bp.route('/<int:task_id>/sub-tasks', methods=['POST'])
@jwt_required()
@admin_required
def create_sub_task(task_id):
    """Create a sub-task (Admin only)."""
    user, error = get_current_user_or_error()
    if error:
        return error

    task = TeamTask.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)

    error = check_team_access(user, task)
    if error:
        return error

    data = request.get_json()
    if not data:
        return error_response('Request body is required', 400)

    # Validate title
    valid, msg = validate_title(data.get('title', ''))
    if not valid:
        return error_response(msg, 400)

    # Validate status if provided
    status = data.get('status', SubTaskStatus.TODO.value)
    valid_statuses = [s.value for s in SubTaskStatus]
    valid, msg = validate_status(status, valid_statuses)
    if not valid:
        return error_response(msg, 400)

    # Validate responsible user if provided
    responsible_user_id = data.get('responsible_user_id')
    if responsible_user_id:
        responsible_user = User.query.get(responsible_user_id)
        if not responsible_user or responsible_user.team_id != user.team_id:
            return error_response('Invalid responsible user', 400)

    sub_task = SubTask(
        team_task_id=task_id,
        title=data['title'],
        status=status,
        responsible_user_id=responsible_user_id
    )

    db.session.add(sub_task)
    db.session.commit()

    return success_response(sub_task.to_dict(), 'Sub-task created successfully', 201)


@team_tasks_bp.route('/<int:task_id>/sub-tasks/<int:sub_task_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_sub_task(task_id, sub_task_id):
    """Update a sub-task (Admin only)."""
    user, error = get_current_user_or_error()
    if error:
        return error

    task = TeamTask.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)

    error = check_team_access(user, task)
    if error:
        return error

    sub_task = SubTask.query.get(sub_task_id)
    if not sub_task or sub_task.team_task_id != task_id:
        return error_response('Sub-task not found', 404)

    data = request.get_json()
    if not data:
        return error_response('Request body is required', 400)

    if 'title' in data:
        valid, msg = validate_title(data['title'])
        if not valid:
            return error_response(msg, 400)
        sub_task.title = data['title']

    if 'status' in data:
        valid_statuses = [s.value for s in SubTaskStatus]
        valid, msg = validate_status(data['status'], valid_statuses)
        if not valid:
            return error_response(msg, 400)
        sub_task.status = data['status']

    if 'responsible_user_id' in data:
        if data['responsible_user_id']:
            responsible_user = User.query.get(data['responsible_user_id'])
            if not responsible_user or responsible_user.team_id != user.team_id:
                return error_response('Invalid responsible user', 400)
        sub_task.responsible_user_id = data['responsible_user_id']

    db.session.commit()

    return success_response(sub_task.to_dict(), 'Sub-task updated successfully')


@team_tasks_bp.route('/<int:task_id>/sub-tasks/<int:sub_task_id>/status', methods=['PATCH'])
@jwt_required()
def update_sub_task_status(task_id, sub_task_id):
    """Update sub-task status (responsible user or admin)."""
    user, error = get_current_user_or_error()
    if error:
        return error

    task = TeamTask.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)

    error = check_team_access(user, task)
    if error:
        return error

    sub_task = SubTask.query.get(sub_task_id)
    if not sub_task or sub_task.team_task_id != task_id:
        return error_response('Sub-task not found', 404)

    # Check if user is admin or responsible for the sub-task
    if not user.is_admin() and sub_task.responsible_user_id != user.id:
        return error_response('Only the responsible user or admin can update status', 403)

    data = request.get_json()
    if not data or 'status' not in data:
        return error_response('Status is required', 400)

    valid_statuses = [s.value for s in SubTaskStatus]
    valid, msg = validate_status(data['status'], valid_statuses)
    if not valid:
        return error_response(msg, 400)

    sub_task.status = data['status']
    db.session.commit()

    return success_response(sub_task.to_dict(), 'Status updated successfully')


@team_tasks_bp.route('/<int:task_id>/sub-tasks/<int:sub_task_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_sub_task(task_id, sub_task_id):
    """Delete a sub-task (Admin only)."""
    user, error = get_current_user_or_error()
    if error:
        return error

    task = TeamTask.query.get(task_id)
    if not task:
        return error_response('Task not found', 404)

    error = check_team_access(user, task)
    if error:
        return error

    sub_task = SubTask.query.get(sub_task_id)
    if not sub_task or sub_task.team_task_id != task_id:
        return error_response('Sub-task not found', 404)

    db.session.delete(sub_task)
    db.session.commit()

    return success_response(message='Sub-task deleted successfully')
