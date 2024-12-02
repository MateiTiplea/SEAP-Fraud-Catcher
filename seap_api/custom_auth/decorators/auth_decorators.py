from functools import wraps

from rest_framework import status
from rest_framework.response import Response

from ..services.auth_service import AuthenticationService


def require_auth(roles=None):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(view_instance, request, *args, **kwargs):
            # Try to get token from cookie first, then fallback to Authorization header
            token = request.COOKIES.get("access_token")

            if not token:
                # Fallback to Authorization header
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]

            if not token:
                return Response(
                    {"error": "No valid authorization token provided"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            auth_service = AuthenticationService()

            # Verify the token
            payload = auth_service.verify_token(token)
            if not payload:
                return Response(
                    {"error": "Invalid or expired token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Check token type
            if not auth_service.validate_token_type(token, "access"):
                return Response(
                    {"error": "Invalid token type"}, status=status.HTTP_401_UNAUTHORIZED
                )

            # Check roles if specified
            if roles:
                user_roles = set(payload.get("roles", []))
                required_roles = set(roles)
                if not required_roles.intersection(user_roles):
                    return Response(
                        {"error": "Insufficient permissions"},
                        status=status.HTTP_403_FORBIDDEN,
                    )

            # Add user information to request
            request.user_id = payload.get("user_id")
            request.user_roles = payload.get("roles", [])

            return view_func(view_instance, request, *args, **kwargs)

        return wrapped_view

    return decorator
