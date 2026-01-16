import re
from typing import Tuple, Optional


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """Validate email format."""
    if not email:
        return False, 'Email is required'
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, 'Invalid email format'
    if len(email) > 255:
        return False, 'Email must be less than 255 characters'
    return True, None


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """Validate password strength."""
    if not password:
        return False, 'Password is required'
    if len(password) < 8:
        return False, 'Password must be at least 8 characters'
    if len(password) > 128:
        return False, 'Password must be less than 128 characters'
    return True, None


def validate_name(name: str) -> Tuple[bool, Optional[str]]:
    """Validate user name."""
    if not name:
        return False, 'Name is required'
    if len(name) < 2:
        return False, 'Name must be at least 2 characters'
    if len(name) > 100:
        return False, 'Name must be less than 100 characters'
    return True, None


def validate_title(title: str) -> Tuple[bool, Optional[str]]:
    """Validate task/todo title."""
    if not title:
        return False, 'Title is required'
    if len(title) < 1:
        return False, 'Title must not be empty'
    if len(title) > 255:
        return False, 'Title must be less than 255 characters'
    return True, None


def validate_status(status: str, valid_statuses: list) -> Tuple[bool, Optional[str]]:
    """Validate status value."""
    if not status:
        return False, 'Status is required'
    if status not in valid_statuses:
        return False, f'Status must be one of: {", ".join(valid_statuses)}'
    return True, None
