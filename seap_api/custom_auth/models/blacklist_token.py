from datetime import datetime

import jwt
from mongoengine import DateTimeField, Document, StringField


class BlacklistedToken(Document):
    """Model for storing blacklisted/revoked JWT tokens"""

    token = StringField(required=True, unique=True)
    token_jti = StringField(required=True)  # JWT ID
    blacklisted_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField(required=True)
    blacklisted_by = StringField()  # User ID who blacklisted the token
    reason = StringField()  # Why the token was blacklisted

    meta = {
        "collection": "blacklisted_tokens",
        "indexes": [
            {"fields": ["token"], "unique": True},
            {"fields": ["token_jti"]},  # Index for quick JTI lookups
            {"fields": ["expires_at"], "expireAfterSeconds": 0},  # TTL index
        ],
    }

    @classmethod
    def is_blacklisted(cls, token, secret_key, algorithm="HS256"):
        """Check if a token is blacklisted"""
        try:
            # First check by token
            if cls.objects(token=token).first():
                return True

            # Then check by JTI if it's a refresh token
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            if payload.get("type") == "refresh" and payload.get("jti"):
                return cls.objects(token_jti=payload["jti"]).first() is not None

            return False
        except jwt.InvalidTokenError:
            return True
