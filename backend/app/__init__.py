import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from app.config import config
from app.models import db

migrate = Migrate()
jwt = JWTManager()


def create_app(config_name=None):
    """Application factory for creating Flask app instances."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # JWT error handlers
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        print(f"JWT Invalid token: {error_string}")
        return jsonify({
            'success': False,
            'error': {'message': f'Invalid token: {error_string}', 'code': 422}
        }), 422

    @jwt.unauthorized_loader
    def unauthorized_callback(error_string):
        print(f"JWT Unauthorized: {error_string}")
        return jsonify({
            'success': False,
            'error': {'message': f'Missing token: {error_string}', 'code': 401}
        }), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"JWT Expired: {jwt_payload}")
        return jsonify({
            'success': False,
            'error': {'message': 'Token has expired', 'code': 401}
        }), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        print(f"JWT Revoked: {jwt_payload}")
        return jsonify({
            'success': False,
            'error': {'message': 'Token has been revoked', 'code': 401}
        }), 401

    # Register token revocation callback
    from app.routes.auth import is_token_revoked
    jwt.token_in_blocklist_loader(is_token_revoked)

    # Register blueprints
    from app.routes import auth_bp, users_bp, private_todos_bp, team_tasks_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(private_todos_bp)
    app.register_blueprint(team_tasks_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
