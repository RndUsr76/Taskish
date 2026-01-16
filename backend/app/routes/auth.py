from flask import request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from app.models import db, User, Team
from app.utils.responses import success_response, error_response
from app.utils.validators import validate_email, validate_password, validate_name
from . import auth_bp

# Store for revoked tokens (in production, use Redis or database)
revoked_tokens = set()


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    if not data:
        return error_response('Request body is required', 400)

    # Validate input
    errors = {}

    valid, msg = validate_name(data.get('name', ''))
    if not valid:
        errors['name'] = msg

    valid, msg = validate_email(data.get('email', ''))
    if not valid:
        errors['email'] = msg

    valid, msg = validate_password(data.get('password', ''))
    if not valid:
        errors['password'] = msg

    if errors:
        return error_response('Validation failed', 400, errors)

    # Check if email already exists
    if User.query.filter_by(email=data['email'].lower()).first():
        return error_response('Email already registered', 409)

    # Get or create default team
    team = Team.query.first()
    if not team:
        team = Team(name='Default Team')
        db.session.add(team)
        db.session.flush()

    # Determine role: first user is admin, others are members
    user_count = User.query.count()
    role = 'ADMIN' if user_count == 0 else 'MEMBER'

    # Create user
    user = User(
        name=data['name'],
        email=data['email'].lower(),
        role=role,
        team_id=team.id
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    # Create access token (identity must be a string)
    access_token = create_access_token(identity=str(user.id))

    return success_response({
        'user': user.to_dict(include_team=True),
        'access_token': access_token
    }, 'User registered successfully', 201)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token."""
    data = request.get_json()
    if not data:
        return error_response('Request body is required', 400)

    email = data.get('email', '').lower()
    password = data.get('password', '')

    if not email or not password:
        return error_response('Email and password are required', 400)

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return error_response('Invalid email or password', 401)

    access_token = create_access_token(identity=str(user.id))

    return success_response({
        'user': user.to_dict(include_team=True),
        'access_token': access_token
    }, 'Login successful')


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user by revoking their token."""
    jti = get_jwt()['jti']
    revoked_tokens.add(jti)
    return success_response(message='Logout successful')


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user."""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return error_response('User not found', 404)
    return success_response(user.to_dict(include_team=True))


def is_token_revoked(jwt_header, jwt_payload):
    """Check if token is revoked."""
    jti = jwt_payload['jti']
    return jti in revoked_tokens
