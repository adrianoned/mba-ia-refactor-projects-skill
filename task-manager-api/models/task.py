"""Model de Task — entidade principal do sistema."""
from database import db
from datetime import datetime, timezone


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="pending")
    priority = db.Column(db.Integer, default=3)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship("User", backref="tasks")
    category = db.relationship("Category", backref="tasks")

    def to_dict(self):
        """Serializacao padrao da task."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
            "due_date": str(self.due_date) if self.due_date else None,
            "tags": self.tags.split(",") if self.tags else [],
            "overdue": self.is_overdue(),
            "user_name": self.user.name if self.user else None,
            "category_name": self.category.name if self.category else None,
        }

    def validate_status(self, new_status):
        """Valida status contra lista permitida."""
        from config.settings import settings
        return new_status in settings.VALID_STATUSES

    def validate_priority(self, p):
        """Valida prioridade entre 1 e 5."""
        return 1 <= p <= 5

    def is_overdue(self):
        """Verifica se a task esta atrasada — logica centralizada (TR-10)."""
        if not self.due_date:
            return False
        if self.status in ("done", "cancelled"):
            return False
        now = datetime.now(timezone.utc)
        due = self.due_date
        # Torna aware se vier do strptime (naive)
        if due.tzinfo is None:
            due = due.replace(tzinfo=timezone.utc)
        return due < now
