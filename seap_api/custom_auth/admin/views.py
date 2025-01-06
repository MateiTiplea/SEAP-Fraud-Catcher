# custom_auth/admin/views.py
import subprocess
import uuid
from datetime import datetime

from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models.acquisition import Acquisition
from api.models.cluster import Cluster
from api.models.item import Item
from clustering_tasks.models import ClusteringTask, TaskStatus
from custom_auth.decorators.auth_decorators import require_auth
from custom_auth.models.user import User
from custom_auth.services.auth_service import AuthenticationService
from scraping_tasks.models.scraping_task import ScrapingTask, TaskStatus


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
                "recent_scraping_tasks": ScrapingTask.objects.order_by("-created_at")[
                    :5
                ],
                "recent_clustering_tasks": ClusteringTask.objects.order_by(
                    "-created_at"
                )[:5],
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


class AdminTasksView(APIView):
    @require_auth(roles=["admin"])
    def get(self, request):
        """Tasks management view showing all tasks"""
        try:
            tasks = ScrapingTask.objects.order_by("-created_at")
            return render(request, "admin/tasks.html", {"tasks": tasks})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_auth(roles=["admin"])
    def post(self, request):
        """Create a new scraping task"""
        try:
            # Get user from database
            user = User.objects.get(id=request.user_id)

            # Parse dates
            start_date = datetime.fromisoformat(request.data["start_date"])
            end_date = datetime.fromisoformat(request.data["end_date"])

            # Create task
            task = ScrapingTask(
                task_id=str(uuid.uuid4()),
                user=user,
                start_date=start_date,
                end_date=end_date,
                cpv_codes=request.data["cpv_codes"],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            task.save()

            # Start the scraping process
            process = subprocess.Popen(
                [
                    "python",
                    "manage.py",
                    "run_scraping",
                    "--task_id",
                    task.task_id,
                    "--start_date",
                    request.data["start_date"],
                    "--end_date",
                    request.data["end_date"],
                    "--cpv_codes",
                    ",".join(map(str, request.data["cpv_codes"])),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=settings.BASE_DIR,
            )

            # Update task with process ID
            task.pid = process.pid
            task.status = TaskStatus.RUNNING
            task.save()

            return Response({"task_id": task.task_id}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {"error": f"Invalid data format: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminTaskDetailView(APIView):
    @require_auth(roles=["admin"])
    def get(self, request, task_id):
        """Detailed view for a specific task"""
        try:
            task = ScrapingTask.objects.get(task_id=task_id)
            print(task.result_stats)
            # Get related acquisition data
            acquisitions = []
            if task.result_stats and "total_acquisitions_inserted" in task.result_stats:
                # Set time to start of day for start_date and end of day for end_date
                start_of_day = datetime.combine(
                    task.start_date.date(), datetime.min.time()
                )
                end_of_day = datetime.combine(task.end_date.date(), datetime.max.time())

                acquisitions = Acquisition.objects(
                    finalization_date__gte=start_of_day,
                    finalization_date__lte=end_of_day,
                    cpv_code_id__in=task.cpv_codes,
                ).order_by("-finalization_date")[
                    :50
                ]  # Limit to most recent 50

            context = {
                "task": task,
                "acquisitions": acquisitions,
                "stats": task.result_stats or {},
            }
            return render(request, "admin/task_detail.html", context)
        except ScrapingTask.DoesNotExist:
            return Response(
                {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminClusteringTasksView(APIView):
    @require_auth(roles=["admin"])
    def get(self, request):
        """Clustering tasks management view"""
        try:
            tasks = ClusteringTask.objects.order_by("-created_at")
            return render(request, "admin/clustering_tasks.html", {"tasks": tasks})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @require_auth(roles=["admin"])
    def post(self, request):
        """Create a new clustering task"""
        try:
            # Get user from database
            user = User.objects.get(id=request.user_id)

            # Create task
            task = ClusteringTask(
                task_id=str(uuid.uuid4()),
                user=user,
                status=TaskStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            task.save()

            # Start the clustering process
            process = subprocess.Popen(
                [
                    "python",
                    "manage.py",
                    "run_clustering",
                    "--task_id",
                    task.task_id,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=settings.BASE_DIR,
            )

            # Update task with process ID
            task.pid = process.pid
            task.status = TaskStatus.RUNNING
            task.save()

            return Response({"task_id": task.task_id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminClusteringTaskDetailView(APIView):
    @require_auth(roles=["admin"])
    def get(self, request, task_id):
        """Detailed view for a specific clustering task"""
        try:
            task = ClusteringTask.objects.get(task_id=task_id)

            # Calculate duration if both timestamps exist
            duration = None
            if task.completed_at and task.created_at:
                duration = task.completed_at - task.created_at

            context = {"task": task, "duration": duration}
            return render(request, "admin/clustering_task_detail.html", context)
        except ClusteringTask.DoesNotExist:
            return Response(
                {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminClustersView(APIView):
    @require_auth(roles=["admin"])
    def get(self, request):
        """View for displaying all clusters"""
        try:
            clusters = Cluster.objects.all()
            context = {
                "clusters": clusters,
                "total_clusters": clusters.count(),
            }
            return render(request, "admin/clusters.html", context)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminClusterDetailView(APIView):
    @require_auth(roles=["admin"])
    def get(self, request, cluster_id):
        """Detailed view for a specific cluster"""
        try:
            cluster = Cluster.objects.get(id=cluster_id)
            context = {
                "cluster": cluster,
                "core_point": cluster.core_point,
                "items": cluster.list_of_items,
                "total_items": len(cluster.list_of_items),
            }
            return render(request, "admin/cluster_detail.html", context)
        except Cluster.DoesNotExist:
            return Response(
                {"error": "Cluster not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
