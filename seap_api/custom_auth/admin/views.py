# custom_auth/admin/views.py
from datetime import datetime

from django.shortcuts import redirect, render
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models.acquisition import Acquisition
from api.models.item import Item
from custom_auth.decorators.auth_decorators import require_auth
from custom_auth.models.user import User
from custom_auth.services.auth_service import AuthenticationService
from scraping_tasks.models.scraping_task import ScrapingTask


class AdminDashboardView(APIView):
    @require_auth(roles=["admin"])
    def get(self, request):
        """Admin dashboard showing system statistics"""
        try:
            # Gather stats
            stats = {
                "total_users": User.objects.count(),
                "total_acquisitions": Acquisition.objects.count(),
                "total_items": Item.objects.count(),
                "recent_tasks": ScrapingTask.objects.order_by("-created_at")[:5],
                "recent_users": User.objects.order_by("-created_at")[:5],
                "recent_acquisitions": Acquisition.objects.order_by(
                    "-publication_date"
                )[:5],
            }
            return render(request, "admin/dashboard.html", stats)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminUserManagementView(APIView):
    @require_auth(roles=["admin"])
    def get(self, request):
        """User management view"""
        try:
            users = User.objects.all().order_by("-created_at")
            return render(request, "admin/users.html", {"users": users})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_auth(roles=["admin"])
    def post(self, request):
        """Create or update user"""
        try:
            action = request.data.get("action")
            if action == "create":
                user = User.create_user(
                    username=request.data["username"],
                    email=request.data["email"],
                    password=request.data["password"],
                    first_name=request.data.get("first_name", ""),
                    last_name=request.data.get("last_name", ""),
                    is_admin=request.data.get("is_admin", False),
                    roles=request.data.get("roles", ["user"]),
                )
                return Response({"message": "User created successfully"})
            elif action == "update":
                user = User.objects.get(id=request.data["user_id"])
                allowed_fields = [
                    "email",
                    "first_name",
                    "last_name",
                    "is_admin",
                    "roles",
                ]
                for field in allowed_fields:
                    if field in request.data:
                        setattr(user, field, request.data[field])
                if "password" in request.data:
                    user.set_password(request.data["password"])
                user.save()
                return Response({"message": "User updated successfully"})
            elif action == "delete":
                user = User.objects.get(id=request.data["user_id"])
                user.delete()
                return Response({"message": "User deleted successfully"})
            else:
                return Response(
                    {"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminLoginView(APIView):
    """Admin login view that doesn't require authentication"""

    authentication_classes = []  # Disable authentication for this view
    permission_classes = []  # Disable permissions for this view

    def get(self, request):
        """Show login form"""
        # Redirect to dashboard if already authenticated
        token = request.COOKIES.get("access_token")
        if token:
            auth_service = AuthenticationService()
            payload = auth_service.verify_token(token)
            if payload and "admin" in payload.get("roles", []):
                return redirect("custom_admin:admin-dashboard")
        return render(request, "admin/login.html")

    def post(self, request):
        """Handle login form submission"""
        username = request.data.get("username")
        password = request.data.get("password")

        auth_service = AuthenticationService()
        user = auth_service.authenticate_user(username, password)

        if user and "admin" in user.roles:
            access_token, refresh_token = auth_service.create_tokens(user)

            # Create response and set cookies
            response = redirect("custom_admin:admin-dashboard")
            response.set_cookie(
                "access_token",
                access_token,
                max_age=30 * 60,  # 30 minutes
                httponly=True,
                samesite="Lax",
            )
            response.set_cookie(
                "refresh_token",
                refresh_token,
                max_age=7 * 24 * 60 * 60,  # 7 days
                httponly=True,
                samesite="Lax",
            )
            return response

        # If login failed, show error
        return render(
            request,
            "admin/login.html",
            {"error": "Invalid credentials or insufficient permissions"},
        )
