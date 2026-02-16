from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Create sample test users'

    def handle(self, *args, **kwargs):
        users_data = [
            ('Zion Matthews', 'zionm96', 'zion.matthews@example.com'),
            ('Amara Okafor', 'amarao97', 'amara.okafor@example.com'),
            ('Declan Walsh', 'declanw98', 'declan.walsh@example.com'),
            ('Elena Kovacs', 'elenak99', 'elena.kovacs@example.com'),
            ('Marcus Delgado', 'marcusd100', 'marcus.delgado@example.com'),
        ]

        for name, username, email in users_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'name': name, 'username': username}
            )

            if created:
                user.set_password('password123')
                user.is_active = True
                user.is_verified = True
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created {email}'))
            else:
                self.stdout.write(f'{email} already exists')