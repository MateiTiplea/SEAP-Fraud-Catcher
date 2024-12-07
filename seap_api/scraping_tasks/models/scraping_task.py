# scraping_tasks/models/task.py
from custom_auth.models.user import User
from django_mongoengine import Document
from mongoengine import (
    PULL,
    DateTimeField,
    DictField,
    FloatField,
    IntField,
    ListField,
    ReferenceField,
    StringField,
)


class TaskStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScrapingTask(Document):
    """MongoDB Document for Scraping Tasks"""

    # Basic tracking fields
    task_id = StringField(primary_key=True)  # UUID for unique identification
    user = ReferenceField(User, required=True)
    status = StringField(
        required=True,
        choices=[
            TaskStatus.PENDING,
            TaskStatus.RUNNING,
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
        ],
        default=TaskStatus.PENDING,
    )
    progress = FloatField(min_value=0, max_value=100, default=0)
    pid = IntField()  # Process ID when running

    # Task parameters
    start_date = DateTimeField(required=True)
    end_date = DateTimeField(required=True)
    cpv_codes = ListField(IntField(), default=list)

    # Results/Metadata
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)
    completed_at = DateTimeField()
    message = StringField()
    error = StringField()  # For storing error messages if task fails
    result_stats = (
        DictField()
    )  # For storing task results (e.g. num_acquisitions_scraped)

    meta = {"collection": "scraping_tasks", "indexes": ["user", "status", "created_at"]}
