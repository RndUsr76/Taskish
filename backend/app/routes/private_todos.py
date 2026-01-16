import logging
import os
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.models import db, User, PrivateTodo
from app.models.private_todo import TodoStatus
from app.utils.responses import success_response, error_response
from app.utils.validators import validate_title, validate_status
from . import private_todos_bp

# Set up logging for todo creation
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'todo_creation.log')

todo_logger = logging.getLogger('todo_creation')
todo_logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
todo_logger.addHandler(file_handler)


@private_todos_bp.route('', methods=['GET'])
@jwt_required()
def get_private_todos():
    """Get all private todos for the current user."""
    user_id = int(get_jwt_identity())
    todos = PrivateTodo.query.filter_by(owner_user_id=user_id).order_by(PrivateTodo.created_at.desc()).all()
    return success_response([todo.to_dict() for todo in todos])


@private_todos_bp.route('', methods=['POST'])
@jwt_required()
def create_private_todo():
    """Create a new private todo."""
    todo_logger.info("="*50)
    todo_logger.info("CREATE_PRIVATE_TODO called")
    todo_logger.info(f"Request method: {request.method}")
    todo_logger.info(f"Request URL: {request.url}")
    todo_logger.info(f"Request headers: {dict(request.headers)}")

    try:
        user_id = int(get_jwt_identity())
        todo_logger.info(f"User ID from JWT: {user_id}")

        data = request.get_json()
        todo_logger.info(f"Request JSON data: {data}")
        todo_logger.info(f"Request raw data: {request.data}")

        if not data:
            todo_logger.error("No request body provided")
            return error_response('Request body is required', 400)

        # Validate title
        title_value = data.get('title', '')
        todo_logger.info(f"Title value: '{title_value}'")
        valid, msg = validate_title(title_value)
        todo_logger.info(f"Title validation: valid={valid}, msg={msg}")
        if not valid:
            todo_logger.error(f"Title validation failed: {msg}")
            return error_response(msg, 400)

        # Validate status if provided
        status = data.get('status', TodoStatus.TODO.value)
        todo_logger.info(f"Status value: '{status}'")
        valid_statuses = [s.value for s in TodoStatus]
        valid, msg = validate_status(status, valid_statuses)
        todo_logger.info(f"Status validation: valid={valid}, msg={msg}")
        if not valid:
            todo_logger.error(f"Status validation failed: {msg}")
            return error_response(msg, 400)

        # Parse due date if provided
        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                todo_logger.info(f"Parsed due_date: {due_date}")
            except ValueError as e:
                todo_logger.error(f"Invalid due_date format: {e}")
                return error_response('Invalid due_date format', 400)

        todo_logger.info(f"Creating PrivateTodo with: owner_user_id={user_id}, title={data['title']}, description={data.get('description')}, status={status}, due_date={due_date}")

        todo = PrivateTodo(
            owner_user_id=user_id,
            title=data['title'],
            description=data.get('description'),
            status=status,
            due_date=due_date
        )

        todo_logger.info(f"Todo object created: {todo}")

        db.session.add(todo)
        todo_logger.info("Todo added to session")

        db.session.commit()
        todo_logger.info(f"Todo committed to database, id={todo.id}")

        result = todo.to_dict()
        todo_logger.info(f"Todo dict result: {result}")
        todo_logger.info("CREATE_PRIVATE_TODO completed successfully")

        return success_response(result, 'Todo created successfully', 201)

    except Exception as e:
        todo_logger.exception(f"Exception in create_private_todo: {str(e)}")
        db.session.rollback()
        return error_response(f'Internal error: {str(e)}', 500)


@private_todos_bp.route('/<int:todo_id>', methods=['GET'])
@jwt_required()
def get_private_todo(todo_id):
    """Get a specific private todo."""
    user_id = int(get_jwt_identity())
    todo = PrivateTodo.query.get(todo_id)

    if not todo:
        return error_response('Todo not found', 404)

    if todo.owner_user_id != user_id:
        return error_response('Access denied', 403)

    return success_response(todo.to_dict())


@private_todos_bp.route('/<int:todo_id>', methods=['PUT'])
@jwt_required()
def update_private_todo(todo_id):
    """Update a private todo."""
    user_id = int(get_jwt_identity())
    todo = PrivateTodo.query.get(todo_id)

    if not todo:
        return error_response('Todo not found', 404)

    if todo.owner_user_id != user_id:
        return error_response('Access denied', 403)

    data = request.get_json()
    if not data:
        return error_response('Request body is required', 400)

    # Validate title if provided
    if 'title' in data:
        valid, msg = validate_title(data['title'])
        if not valid:
            return error_response(msg, 400)
        todo.title = data['title']

    # Validate status if provided
    if 'status' in data:
        valid_statuses = [s.value for s in TodoStatus]
        valid, msg = validate_status(data['status'], valid_statuses)
        if not valid:
            return error_response(msg, 400)
        todo.status = data['status']

    if 'description' in data:
        todo.description = data['description']

    if 'due_date' in data:
        if data['due_date']:
            try:
                todo.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return error_response('Invalid due_date format', 400)
        else:
            todo.due_date = None

    db.session.commit()

    return success_response(todo.to_dict(), 'Todo updated successfully')


@private_todos_bp.route('/<int:todo_id>', methods=['DELETE'])
@jwt_required()
def delete_private_todo(todo_id):
    """Delete a private todo."""
    user_id = int(get_jwt_identity())
    todo = PrivateTodo.query.get(todo_id)

    if not todo:
        return error_response('Todo not found', 404)

    if todo.owner_user_id != user_id:
        return error_response('Access denied', 403)

    db.session.delete(todo)
    db.session.commit()

    return success_response(message='Todo deleted successfully')
