from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = "Create sample test users"

    def handle(self, *args, **kwargs):
        users_data = [
            ("Xander Cage", "xanderc24", "xander.cage@example.com"),
            ("Yara Shahidi", "yaras25", "yara.shahidi@example.com"),
            ("Zoe Saldana", "zoes26", "zoe.saldana@example.com"),
            ("Aaron Paul", "aaronp27", "aaron.paul@example.com"),
            ("Beth Harmon", "bethh28", "beth.harmon@example.com"),
            ("Caleb Rivers", "calebr29", "caleb.rivers@example.com"),
            ("Dana Scully", "danas30", "dana.scully@example.com"),
            ("Elliot Alderson", "elliota31", "elliot.alderson@example.com"),
            ("Faith Connors", "faithc32", "faith.connors@example.com"),
            ("Gideon Graves", "gideong33", "gideon.graves@example.com"),
        ]

        for name, username, email in users_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"name": name, "username": username}
            )

            if created:
                user.set_password("password123")
                user.is_active = True
                user.is_verified = True
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created {email}"))
            else:
                self.stdout.write(f"{email} already exists")