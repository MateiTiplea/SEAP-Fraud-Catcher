from datetime import datetime

from mongoengine import (
    BooleanField,
    DateTimeField,
    Document,
    EmailField,
    ListField,
    StringField,
)
from werkzeug.security import check_password_hash, generate_password_hash


class User(Document):
    """
    User model for MongoDB using MongoEngine.
    Includes basic user information and authentication fields.
    """

    username = StringField(required=True, unique=True, min_length=3, max_length=50)
    email = EmailField(required=True, unique=True)
    password_hash = StringField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    is_active = BooleanField(default=True)
    is_admin = BooleanField(default=False)
    roles = ListField(StringField(), default=["user"])
    last_login = DateTimeField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "users",
        "indexes": [
            {"fields": ["username"], "unique": True, "name": "unique_username"},
            {"fields": ["email"], "unique": True, "name": "unique_email"},
        ],
    }

    def set_password(self, password):
        """Set the user's password after hashing."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify the user's password."""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.now()
        self.save()

    def to_json(self):
        """Convert user object to JSON representation (excluding sensitive data)."""
        return {
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "roles": self.roles,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def save(self, *args, **kwargs):
        """Override save method to update timestamps."""
        if not self.created_at:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
        return super(User, self).save(*args, **kwargs)

    @staticmethod
    def create_user(username, email, password, **kwargs):
        """Create a new user with the given details."""
        user = User(
            username=username,
            email=email,
            first_name=kwargs.get("first_name", ""),
            last_name=kwargs.get("last_name", ""),
            is_admin=kwargs.get("is_admin", False),
            roles=kwargs.get("roles", ["user"]),
        )
        user.set_password(password)
        user.save()
        return user
