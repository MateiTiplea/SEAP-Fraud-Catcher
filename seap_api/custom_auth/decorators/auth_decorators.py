from functools import wraps

from rest_framework import status
from rest_framework.response import Response

from ..services.auth_service import AuthenticationService


def require_auth(roles=None):
    """
    Decorator for views that checks if the user is authenticated and has required roles.

    Args:
        roles (list): Optional list of roles required to access the endpoint
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(view_instance, request, *args, **kwargs):
            # Get the token from the request
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return Response(
                    {"error": "No valid authorization token provided"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            token = auth_header.split(" ")[1]
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
