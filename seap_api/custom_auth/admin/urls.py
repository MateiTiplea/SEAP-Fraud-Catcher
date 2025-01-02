from django.urls import path

from .views import AdminDashboardView, AdminLoginView, AdminUserManagementView

urlpatterns = [
    path("login/", AdminLoginView.as_view(), name="admin-login"),
    path("", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("users/", AdminUserManagementView.as_view(), name="admin-users"),
]
