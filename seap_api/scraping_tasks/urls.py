from django.urls import path

from .views.task_views import TaskDetailView, TaskListView  # your actual views

urlpatterns = [
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("tasks/<str:task_id>/", TaskDetailView.as_view(), name="task-detail"),
]
