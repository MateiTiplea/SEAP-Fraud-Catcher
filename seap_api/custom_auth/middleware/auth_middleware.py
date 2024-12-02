from django.http import JsonResponse

from ..services.auth_service import AuthenticationService


class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.auth_service = AuthenticationService()
        self.public_paths = [
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/refresh-token",
        ]

    def __call__(self, request):
        if request.path in self.public_paths:
            return self.get_response(request)

        # Try to get token from cookie first, then fallback to Authorization header
        token = request.COOKIES.get("access_token")

        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if token:
            payload = self.auth_service.verify_token(token)
            if payload:
                request.user_id = payload.get("user_id")
                request.user_roles = payload.get("roles", [])

        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Called just before Django calls the view.
        Checks if the view requires authentication and verifies the token if needed.
        """
        if hasattr(view_func, "auth_required"):
            token = request.COOKIES.get("access_token")

            if not token:
                auth_header = request.headers.get("Authorization")
                if not auth_header or not auth_header.startswith("Bearer "):
                    return JsonResponse(
                        {"error": "Authentication required"}, status=401
                    )
                token = auth_header.split(" ")[1]

            # Verify token
            payload = self.auth_service.verify_token(token)
            if not payload:
                return JsonResponse({"error": "Invalid or expired token"}, status=401)

        return None
