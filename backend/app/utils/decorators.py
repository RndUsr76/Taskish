from functools import wraps
from flask_jwt_extended import get_jwt_identity
from app.models import User
from app.utils.responses import error_response


def admin_required(f):
    """Decorator to require admin role for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_admin():
            return error_response('Admin access required', 403)
        return f(*args, **kwargs)
    return decorated_function
