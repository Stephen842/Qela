from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Create sample test users'

    def handle(self, *args, **kwargs):
        users_data = [
            ('Adrian Cole', 'adrianc76', 'adrian.cole@example.com'),
            ('Bianca Reyes', 'biancar77', 'bianca.reyes@example.com'),
            ('Carter Blake', 'carterb78', 'carter.blake@example.com'),
            ('Diana Prince', 'dianap79', 'diana.prince@example.com'),
            ('Evan Turner', 'evant80', 'evan.turner@example.com'),
            ('Freya Morgan', 'freyam81', 'freya.morgan@example.com'),
            ('Gabriel Knight', 'gabrielk82', 'gabriel.knight@example.com'),
            ('Hailey Brooks', 'haileyb83', 'hailey.brooks@example.com'),
            ('Isaiah Coleman', 'isaiahc84', 'isaiah.coleman@example.com'),
            ('Jasmine Patel', 'jasminep85', 'jasmine.patel@example.com'),
            ('Kai Anderson', 'kaia86', 'kai.anderson@example.com'),
            ('Liam Bennett', 'liamb87', 'liam.bennett@example.com'),
            ('Mila Rodriguez', 'milar88', 'mila.rodriguez@example.com'),
            ('Noah Thompson', 'noaht89', 'noah.thompson@example.com'),
            ('Olive Harper', 'oliveh90', 'olive.harper@example.com'),
            ('Preston Hughes', 'prestonh91', 'preston.hughes@example.com'),
            ('Riley Sanders', 'rileys92', 'riley.sanders@example.com'),
            ('Sophia Lawson', 'sophial93', 'sophia.lawson@example.com'),
            ('Tristan Moore', 'tristanm94', 'tristan.moore@example.com'),
            ('Valerie Stone', 'valeries95', 'valerie.stone@example.com'),
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