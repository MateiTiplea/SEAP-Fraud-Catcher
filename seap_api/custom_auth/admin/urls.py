from django.urls import path

from .views import (
    AdminDashboardView,
    AdminLoginView,
    AdminTaskDetailView,
    AdminTasksView,
    AdminUserManagementView,
)

urlpatterns = [
    path("login/", AdminLoginView.as_view(), name="admin-login"),
    path("", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("users/", AdminUserManagementView.as_view(), name="admin-users"),
    path("tasks/", AdminTasksView.as_view(), name="admin-tasks"),
    path(
        "tasks/<str:task_id>/", AdminTaskDetailView.as_view(), name="admin-task-detail"
    ),
]
