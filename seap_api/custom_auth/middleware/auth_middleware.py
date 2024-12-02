from django.http import JsonResponse

from ..services.auth_service import AuthenticationService


class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.auth_service = AuthenticationService()
        # Paths that don't require authentication
        self.public_paths = [
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/refresh-token",
        ]

    def __call__(self, request):
        # Skip authentication for public paths
        if request.path in self.public_paths:
            return self.get_response(request)

        # Get the token from the request
        auth_header = request.headers.get("Authorization")

        # If no token is provided, proceed (the decorator will handle protection if needed)
        if not auth_header or not auth_header.startswith("Bearer "):
            return self.get_response(request)

        token = auth_header.split(" ")[1]

        # Verify the token
        payload = self.auth_service.verify_token(token)
        if payload:
            # Add user information to request
            request.user_id = payload.get("user_id")
            request.user_roles = payload.get("roles", [])

        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Called just before Django calls the view.
        """
        # Check if view has auth_required attribute (set by decorator)
        if hasattr(view_func, "auth_required"):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JsonResponse({"error": "Authentication required"}, status=401)
        return None
