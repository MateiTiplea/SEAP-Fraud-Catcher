"""
URL configuration for seap_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import include, path

v1_patterns = [
    path("", include("api.urls")),
    path("scraping/", include("scraping_tasks.urls")),

    path("clustering/", include("clustering_tasks.urls")),
]

urlpatterns = [
    path("api/v1/", include(v1_patterns)),
    path("api/auth/", include("custom_auth.urls")),
    path(
        "admin/",
        include(("custom_auth.admin.urls", "custom_admin"), namespace="custom_admin"),
    ),
]
