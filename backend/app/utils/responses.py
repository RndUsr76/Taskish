from flask import jsonify
from typing import Any, Optional


def success_response(data: Any = None, message: Optional[str] = None, status_code: int = 200):
    """Create a standardized success response."""
    response = {'success': True}
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    return jsonify(response), status_code


def error_response(message: str, status_code: int = 400, errors: Optional[dict] = None):
    """Create a standardized error response."""
    response = {
        'success': False,
        'error': {
            'message': message,
            'code': status_code
        }
    }
    if errors:
        response['error']['details'] = errors
    return jsonify(response), status_code
