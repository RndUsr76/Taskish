from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Team
from app.utils.responses import success_response, error_response
from . import users_bp


@users_bp.route('/teams/<int:team_id>/users', methods=['GET'])
@jwt_required()
def get_team_users(team_id):
    """Get all users in a team (for assignment dropdowns)."""
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)

    if not current_user:
        return error_response('User not found', 404)

    # Check if user belongs to the team
    if current_user.team_id != team_id:
        return error_response('Access denied', 403)

    team = Team.query.get(team_id)
    if not team:
        return error_response('Team not found', 404)

    users = User.query.filter_by(team_id=team_id).all()
    return success_response([{
        'id': u.id,
        'name': u.name,
        'email': u.email,
        'role': u.role
    } for u in users])
