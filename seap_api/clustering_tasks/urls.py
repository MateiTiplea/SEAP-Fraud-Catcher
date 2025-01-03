from django.urls import path

from .views import ClusteringTaskDetailView, ClusteringTaskListView
urlpatterns = [
    path("tasks/", ClusteringTaskListView.as_view(), name="task-list"),
    path("tasks/<str:task_id>/", ClusteringTaskDetailView.as_view(), name="task-detail"),
]
