import os
from datetime import datetime, timedelta
from typing import Optional, Tuple

import jwt

from ..models.blacklist_token import BlacklistedToken
from ..models.user import User


class AuthenticationService:
    """
    Service for handling authentication-related operations
    """

    def __init__(self):
        self.secret_key = os.getenv(
            "JWT_SECRET_KEY", "your-secret-key"
        )  # Should be in env
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
        # Access token payload
        access_payload = {
            "user_id": str(user.id),
            "username": user.username,
            "roles": user.roles,
            "exp": datetime.now() + timedelta(minutes=self.access_token_expire_minutes),
            "type": "access",
        }

        # Refresh token payload
        refresh_payload = {
            "user_id": str(user.id),
            "exp": datetime.now() + timedelta(days=self.refresh_token_expire_days),
            "type": "refresh",
        }

        # Create tokens
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
            if BlacklistedToken.is_blacklisted(token):
                return None

            # Decode and verify token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Create a new access token using a refresh token"""
        payload = self.verify_token(refresh_token)
        if payload and payload.get("type") == "refresh":
            user = User.objects(id=payload["user_id"]).first()
            if user:
                new_access_token, _ = self.create_tokens(user)
                return new_access_token
        return None

    def blacklist_token(self, token: str):
        """Add a token to the blacklist"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            expires_at = datetime.fromtimestamp(payload["exp"])
            BlacklistedToken(token=token, expires_at=expires_at).save()
            return True
        except (jwt.InvalidTokenError, KeyError):
            return False

    def validate_token_type(self, token: str, expected_type: str) -> bool:
        """Validate that a token is of the expected type (access or refresh)"""
        payload = self.verify_token(token)
        return payload and payload.get("type") == expected_type
