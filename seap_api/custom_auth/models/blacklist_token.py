from datetime import datetime

from mongoengine import DateTimeField, Document, StringField


class BlacklistedToken(Document):
    """
    Model for storing blacklisted/revoked JWT tokens
    """

    token = StringField(required=True, unique=True)
    blacklisted_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField(required=True)

    meta = {
        "collection": "blacklisted_tokens",
        "indexes": [
            {"fields": ["token"], "unique": True},
            {"fields": ["expires_at"], "expireAfterSeconds": 0},  # TTL index
        ],
    }

    @staticmethod
    def is_blacklisted(token):
        """Check if a token is blacklisted"""
        return BlacklistedToken.objects(token=token).first() is not None
