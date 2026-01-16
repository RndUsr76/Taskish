from datetime import datetime, timezone
from enum import Enum
import bcrypt
from . import db


class UserRole(str, Enum):
    ADMIN = 'ADMIN'
    MEMBER = 'MEMBER'


class User(db.Model):
    """User model with authentication and team membership."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=UserRole.MEMBER.value)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    team = db.relationship('Team', back_populates='users')
    private_todos = db.relationship('PrivateTodo', back_populates='owner', lazy='dynamic', cascade='all, delete-orphan')
    assigned_tasks = db.relationship('TeamTask', back_populates='assigned_user', lazy='dynamic', foreign_keys='TeamTask.assigned_user_id')
    responsible_subtasks = db.relationship('SubTask', back_populates='responsible_user', lazy='dynamic', foreign_keys='SubTask.responsible_user_id')

    def set_password(self, password: str):
        """Hash and set the user's password."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN.value

    def to_dict(self, include_team: bool = False):
        result = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'team_id': self.team_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_team and self.team:
            result['team'] = self.team.to_dict()
        return result

    def __repr__(self):
        return f'<User {self.email}>'
