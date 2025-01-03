# Create your models here.
from django_mongoengine import Document
from mongoengine import (
    DateTimeField, DictField, FloatField, StringField, ReferenceField
)

from custom_auth.models.user import User


class TaskStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ClusteringTask(Document):
    task_id = StringField(primary_key=True)
    user = ReferenceField(User, required=True)
    status = StringField(
        required=True,
        choices=[TaskStatus.PENDING, TaskStatus.RUNNING, TaskStatus.COMPLETED, TaskStatus.FAILED],
        default=TaskStatus.PENDING,
    )
    progress = FloatField(min_value=0, max_value=100, default=0)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)
    completed_at = DateTimeField()
    error = StringField()
    result_stats = DictField(default=dict)

    meta = {"collection": "clustering_tasks", "indexes": ["user", "status", "created_at"]}
