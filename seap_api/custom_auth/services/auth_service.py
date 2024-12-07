import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple

import jwt

from ..models.blacklist_token import BlacklistedToken
from ..models.user import User


class AuthenticationService:
    """Service for handling authentication-related operations"""

    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password"""
        user = User.objects(username=username).first()
        if user and user.check_password(password):
            return user
        return None

    def create_tokens(self, user: User) -> Tuple[str, str]:
        """Create access and refresh tokens for the user"""
        access_payload = {
            "user_id": str(user.id),
            "username": user.username,
            "roles": user.roles,
            "exp": datetime.now() + timedelta(minutes=self.access_token_expire_minutes),
            "type": "access",
        }

        refresh_payload = {
            "user_id": str(user.id),
            "exp": datetime.now() + timedelta(days=self.refresh_token_expire_days),
            "type": "refresh",
            "jti": str(uuid.uuid4()),
        }

        access_token = jwt.encode(
            access_payload, self.secret_key, algorithm=self.algorithm
        )
        refresh_token = jwt.encode(
            refresh_payload, self.secret_key, algorithm=self.algorithm
        )

        return access_token, refresh_token

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify a token and return its payload if valid"""
        try:
            # Check if token is blacklisted
            if BlacklistedToken.is_blacklisted(token, self.secret_key, self.algorithm):
                return None

            # Decode and verify token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[Tuple[str, str]]:
        """Create new access token and rotate refresh token"""
        payload = self.verify_token(refresh_token)
        if payload and payload.get("type") == "refresh":
            user = User.objects(id=payload["user_id"]).first()
            if user:
                # Blacklist the used refresh token
                self.blacklist_token(refresh_token)

                # Generate new tokens
                return self.create_tokens(user)
        return None

    def blacklist_token(self, token: str, reason: str = "Token rotated"):
        """Add a token to the blacklist"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            expires_at = datetime.fromtimestamp(payload["exp"])
            jti = payload.get("jti", str(uuid.uuid4()))

            BlacklistedToken(
                token=token,
                token_jti=jti,
                expires_at=expires_at,
                blacklisted_by=payload.get("user_id"),
                reason=reason,
            ).save()
            return True
        except (jwt.InvalidTokenError, KeyError):
            return False

    def validate_token_type(self, token: str, expected_type: str) -> bool:
        """Validate that a token is of the expected type"""
        payload = self.verify_token(token)
        return payload and payload.get("type") == expected_type
