from aspects.error_handlers import handle_exceptions
from aspects.loggers import log_method_calls
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
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


@method_decorator(ensure_csrf_cookie, name="dispatch")
class LoginView(APIView):
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, TypeError))
    def post(self, request):
        """Authenticate user and set token cookies"""
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

            response = Response({"user": user.to_json(), "message": "Login successful"})

            # Set cookies
            response.set_cookie(
                "access_token",
                access_token,
                max_age=30 * 60,  # 30 minutes
                httponly=True,
                secure=not settings.DEBUG,  # True in production
                samesite="Lax",
            )

            response.set_cookie(
                "refresh_token",
                refresh_token,
                max_age=7 * 24 * 60 * 60,  # 7 days
                httponly=True,
                secure=not settings.DEBUG,  # True in production
                samesite="Lax",
            )

            return response

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RefreshTokenView(APIView):
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, TypeError))
    def post(self, request):
        """Refresh access token and rotate refresh token"""
        try:
            # Get refresh token from cookie
            refresh_token = request.COOKIES.get("refresh_token")

            if not refresh_token:
                return Response(
                    {"error": "Refresh token required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            auth_service = AuthenticationService()
            new_tokens = auth_service.refresh_access_token(refresh_token)

            if not new_tokens:
                return Response(
                    {"error": "Invalid refresh token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            new_access_token, new_refresh_token = new_tokens

            # Create response with new tokens in cookies
            response = Response({"message": "Tokens refreshed successfully"})

            # Set new cookies
            response.set_cookie(
                "access_token",
                new_access_token,
                max_age=30 * 60,  # 30 minutes
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
            )

            response.set_cookie(
                "refresh_token",
                new_refresh_token,
                max_age=7 * 24 * 60 * 60,  # 7 days
                httponly=True,
                secure=not settings.DEBUG,
                samesite="Lax",
            )

            return response

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutView(APIView):
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, TypeError))
    @require_auth()
    def post(self, request):
        """Logout user by blacklisting the token and clearing cookies"""
        try:
            # Get token from cookie
            access_token = request.COOKIES.get("access_token")
            refresh_token = request.COOKIES.get("refresh_token")

            auth_service = AuthenticationService()

            # Blacklist both tokens if they exist
            if access_token:
                auth_service.blacklist_token(access_token, "User logout")
            if refresh_token:
                auth_service.blacklist_token(refresh_token, "User logout")

            # Create response and clear cookies
            response = Response({"message": "Successfully logged out"})

            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

            # Also delete CSRF cookie if you want to completely clear session
            response.delete_cookie("csrftoken")

            return response
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
