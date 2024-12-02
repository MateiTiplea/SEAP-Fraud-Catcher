from aspects.error_handlers import handle_exceptions
from aspects.loggers import log_method_calls
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..decorators.auth_decorators import require_auth
from ..models.user import User
from ..services.auth_service import AuthenticationService


class RegisterView(APIView):
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, TypeError))
    def post(self, request):
        """Register a new user"""
        try:
            data = request.data
            required_fields = ["username", "email", "password"]

            # Check for required fields
            if not all(field in data for field in required_fields):
                return Response(
                    {"error": "Missing required fields"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if user already exists
            if User.objects(username=data["username"]).first():
                return Response(
                    {"error": "Username already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if User.objects(email=data["email"]).first():
                return Response(
                    {"error": "Email already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create user with default non-admin settings
            user = User.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                first_name=data.get("first_name", ""),
                last_name=data.get("last_name", ""),
                is_admin=False,  # Explicitly set to False
                roles=["user"],  # Only basic user role
            )

            return Response(user.to_json(), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginView(APIView):
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, TypeError))
    def post(self, request):
        """Authenticate user and return tokens"""
        try:
            data = request.data
            auth_service = AuthenticationService()

            # Authenticate user
            user = auth_service.authenticate_user(
                data.get("username"), data.get("password")
            )

            if not user:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Generate tokens
            access_token, refresh_token = auth_service.create_tokens(user)

            # Update last login
            user.update_last_login()

            return Response(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": user.to_json(),
                }
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RefreshTokenView(APIView):
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, TypeError))
    def post(self, request):
        """Refresh access token"""
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            auth_service = AuthenticationService()
            new_access_token = auth_service.refresh_access_token(refresh_token)

            if not new_access_token:
                return Response(
                    {"error": "Invalid refresh token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            return Response({"access_token": new_access_token})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutView(APIView):
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, TypeError))
    @require_auth()
    def post(self, request):
        """Logout user by blacklisting the token"""
        try:
            auth_header = request.headers.get("Authorization")
            token = auth_header.split(" ")[1]

            auth_service = AuthenticationService()
            auth_service.blacklist_token(token)

            return Response({"message": "Successfully logged out"})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
