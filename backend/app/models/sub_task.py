from datetime import datetime, timezone
from enum import Enum
from . import db


class SubTaskStatus(str, Enum):
    TODO = 'TODO'
    IN_PROGRESS = 'IN_PROGRESS'
    BLOCKED = 'BLOCKED'
    DONE = 'DONE'


class SubTask(db.Model):
    """Sub-task belonging to a team task."""
    __tablename__ = 'sub_tasks'

    id = db.Column(db.Integer, primary_key=True)
    team_task_id = db.Column(db.Integer, db.ForeignKey('team_tasks.id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=SubTaskStatus.TODO.value)
    responsible_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    team_task = db.relationship('TeamTask', back_populates='sub_tasks')
    responsible_user = db.relationship('User', back_populates='responsible_subtasks', foreign_keys=[responsible_user_id])

    def to_dict(self, include_responsible_user: bool = True):
        result = {
            'id': self.id,
            'team_task_id': self.team_task_id,
            'title': self.title,
            'status': self.status,
            'responsible_user_id': self.responsible_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_responsible_user and self.responsible_user:
            result['responsible_user'] = {
                'id': self.responsible_user.id,
                'name': self.responsible_user.name,
                'email': self.responsible_user.email
            }
        return result

    def __repr__(self):
        return f'<SubTask {self.title}>'
