from datetime import datetime, timezone
from enum import Enum
from . import db


class TaskStatus(str, Enum):
    TODO = 'TODO'
    IN_PROGRESS = 'IN_PROGRESS'
    BLOCKED = 'BLOCKED'
    DONE = 'DONE'


class TeamTask(db.Model):
    """Team task visible to all team members."""
    __tablename__ = 'team_tasks'

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default=TaskStatus.TODO.value)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    team = db.relationship('Team', back_populates='tasks')
    assigned_user = db.relationship('User', back_populates='assigned_tasks', foreign_keys=[assigned_user_id])
    sub_tasks = db.relationship('SubTask', back_populates='team_task', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def progress(self) -> int:
        """Calculate progress based on completed sub-tasks."""
        total = self.sub_tasks.count()
        if total == 0:
            return 100 if self.status == TaskStatus.DONE.value else 0
        done = self.sub_tasks.filter_by(status=TaskStatus.DONE.value).count()
        return int((done / total) * 100)

    def to_dict(self, include_sub_tasks: bool = False, include_assigned_user: bool = False):
        result = {
            'id': self.id,
            'team_id': self.team_id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'assigned_user_id': self.assigned_user_id,
            'progress': self.progress,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_assigned_user and self.assigned_user:
            result['assigned_user'] = {
                'id': self.assigned_user.id,
                'name': self.assigned_user.name,
                'email': self.assigned_user.email
            }
        if include_sub_tasks:
            result['sub_tasks'] = [st.to_dict() for st in self.sub_tasks.all()]
        return result

    def __repr__(self):
        return f'<TeamTask {self.title}>'
