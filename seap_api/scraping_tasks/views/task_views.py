# scraping_tasks/views.py
import os
import subprocess
import uuid
from datetime import datetime

from aspects.error_handlers import handle_exceptions
from aspects.loggers import log_method_calls
from custom_auth.decorators.auth_decorators import require_auth
from custom_auth.models.user import User
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from scraping_tasks.models.scraping_task import ScrapingTask, TaskStatus
from scraping_tasks.serializers import TaskSerializer


class TaskListView(APIView):
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, KeyError))
    @require_auth(roles=["admin", "user"])
    def get(self, request):
        """Get all tasks for the authenticated user"""
        try:
            tasks = ScrapingTask.objects().order_by("-created_at")
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @log_method_calls
    @handle_exceptions(error_types=(ValueError, TypeError))
    @require_auth(roles=["admin", "user"])
    def post(self, request):
        """Create a new scraping task and start it in background"""
        try:
            # Validate required fields
            required_fields = ["start_date", "end_date", "cpv_codes"]
            for field in required_fields:
                if field not in request.data:
                    return Response(
                        {"error": f"Missing required field: {field}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Get user from database
            user = User.objects.get(id=request.user_id)

            # Create task record
            task = ScrapingTask(
                task_id=str(uuid.uuid4()),
                user=user,  # Use fetched user object
                start_date=datetime.fromisoformat(request.data["start_date"]),
                end_date=datetime.fromisoformat(request.data["end_date"]),
                cpv_codes=request.data["cpv_codes"],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            task.save()

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
                stdout=subprocess.DEVNULL,  # Suppress output
                stderr=subprocess.DEVNULL,
                cwd=settings.BASE_DIR,  # Run from Django project root
            )

            # Update task with process ID
            task.pid = process.pid
            task.status = TaskStatus.RUNNING
            task.save()

            serializer = TaskSerializer(task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {"error": f"Invalid data format: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TaskDetailView(APIView):
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, KeyError))
    @require_auth(roles=["admin", "user"])
    def get(self, request, task_id):
        """Get a specific task by ID"""
        try:
            task = ScrapingTask.objects(task_id=task_id).first()

            if not task:
                return Response(
                    {"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND
                )

            serializer = TaskSerializer(task)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
