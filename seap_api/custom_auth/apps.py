from django.apps import AppConfig


class CustomAuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "custom_auth"  # simplified name
    label = "seap_auth"  # unique label to avoid conflicts
