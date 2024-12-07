from custom_auth.models.user import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates an admin user"

    def add_arguments(self, parser):
        parser.add_argument("--username", type=str, required=True)
        parser.add_argument("--email", type=str, required=True)
        parser.add_argument("--password", type=str, required=True)
        parser.add_argument("--first_name", type=str, default="")
        parser.add_argument("--last_name", type=str, default="")

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]
        first_name = options["first_name"]
        last_name = options["last_name"]

        # Check if user already exists
        if User.objects(username=username).first():
            self.stdout.write(
                self.style.ERROR(f"User with username {username} already exists")
            )
            return

        if User.objects(email=email).first():
            self.stdout.write(
                self.style.ERROR(f"User with email {email} already exists")
            )
            return

        try:
            # Create admin user
            user = User.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_admin=True,
                roles=["admin", "user"],
            )

            self.stdout.write(
                self.style.SUCCESS(f"Successfully created admin user: {username}")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating admin user: {str(e)}"))
