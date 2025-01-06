from django.urls import path

from .views import (
    AdminClusterDetailView,
    AdminClusteringTaskDetailView,
    AdminClusteringTasksView,
    AdminClustersView,
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
    path(
        "clustering-tasks/",
        AdminClusteringTasksView.as_view(),
        name="admin-clustering-tasks",
    ),
    path(
        "clustering-tasks/<str:task_id>/",
        AdminClusteringTaskDetailView.as_view(),
        name="admin-clustering-task-detail",
    ),
    path("clusters/", AdminClustersView.as_view(), name="admin-clusters"),
    path(
        "clusters/<str:cluster_id>/",
        AdminClusterDetailView.as_view(),
        name="admin-cluster-detail",
    ),
]
