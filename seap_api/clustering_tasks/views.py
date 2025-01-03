from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from aspects.error_handlers import handle_exceptions
from aspects.loggers import log_method_calls
from clustering_tasks.models import ClusteringTask, TaskStatus
from clustering_tasks.serializers import ClusteringTaskSerializer
from custom_auth.decorators.auth_decorators import require_auth
from django.conf import settings
from custom_auth.models.user import User
import subprocess
import uuid
from datetime import datetime


class ClusteringTaskListView(APIView):
    # noinspection PyMethodMayBeStatic
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, KeyError))
    @require_auth(roles=["admin", "user"])
    def post(self, request):
        """Create and start a clustering task"""
        try:
            # Generate a unique task ID
            task_id = str(uuid.uuid4())

            user = User.objects.get(id=request.user_id)

            # Create the task
            task = ClusteringTask(
                task_id=task_id,
                user=user,
                status=TaskStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            task.save()

            # Start the clustering task in the background
            process = subprocess.Popen(
                [
                    "python",
                    "manage.py",
                    "run_clustering",
                    "--task_id",
                    task_id,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=settings.BASE_DIR,
            )

            # Save the process ID
            task.pid = process.pid
            # Update task status
            task.status = TaskStatus.RUNNING
            task.save()

            serializer = ClusteringTaskSerializer(task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # noinspection PyMethodMayBeStatic
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, KeyError))
    @require_auth(roles=["admin", "user"])
    def get(self, request):
        """List all clustering tasks"""
        try:
            tasks = ClusteringTask.objects().order_by("-created_at")
            serializer = ClusteringTaskSerializer(tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClusteringTaskDetailView(APIView):
    # noinspection PyMethodMayBeStatic
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, KeyError))
    @require_auth(roles=["admin", "user"])
    def get(self, request, task_id):
        """Retrieve a specific clustering task"""
        try:
            task = ClusteringTask.objects().get(task_id=task_id)
            serializer = ClusteringTaskSerializer(task)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ClusteringTask.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # noinspection PyMethodMayBeStatic
    @log_method_calls
    @handle_exceptions(error_types=(ValueError, KeyError))
    @require_auth(roles=["admin", "user"])
    def delete(self, request, task_id):
        """Delete a specific clustering task"""
        try:
            task = ClusteringTask.objects().get(task_id=task_id, user=request.user)
            task.delete()
            return Response({"message": "Task deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except ClusteringTask.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
