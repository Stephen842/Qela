from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Create sample test users'

    def handle(self, *args, **kwargs):
        users_data = [
            ('Arjun Mehta', 'arjunm113', 'arjun.mehta@example.com'),
            ('Bella Novak', 'bellan114', 'bella.novak@example.com'),
            ('Calvin Brooks', 'calvinb115', 'calvin.brooks@example.com'),
            ('Daria Petrov', 'dariap116', 'daria.petrov@example.com'),
            ('Emmanuel Adeyemi', 'emmanuela117', 'emmanuel.adeyemi@example.com'),
            ('Fatima Zahra', 'fatimaz118', 'fatima.zahra@example.com'),
            ('Gavin O\'Connor', 'gavino119', 'gavin.oconnor@example.com'),
            ('Hana Suzuki', 'hanas120', 'hana.suzuki@example.com'),
            ('Ibrahim Musa', 'ibrahimm121', 'ibrahim.musa@example.com'),
            ('Julia Schmidt', 'julias122', 'julia.schmidt@example.com'),
            ('Kofi Mensah', 'kofim123', 'kofi.mensah@example.com'),
            ('Lena Hoffmann', 'lenah124', 'lena.hoffmann@example.com'),
            ('Miguel Santos', 'miguels125', 'miguel.santos@example.com'),
            ('Noura Khalid', 'nourak126', 'noura.khalid@example.com'),
            ('Omar Farouk', 'omarf127', 'omar.farouk@example.com'),
            ('Priya Nair', 'priyan128', 'priya.nair@example.com'),
            ('Quincy Adams', 'quincya129', 'quincy.adams@example.com'),
            ('Rafael Costa', 'rafaelc130', 'rafael.costa@example.com'),
            ('Sara Ibrahim', 'sarai131', 'sara.ibrahim@example.com'),
            ('Theo Laurent', 'theol132', 'theo.laurent@example.com'),
            ('Uche Okoye', 'ucheo133', 'uche.okoye@example.com'),
            ('Valentina Rossi', 'valentinar134', 'valentina.rossi@example.com'),
            ('William Carter', 'williamc135', 'william.carter@example.com'),
            ('Ximena Torres', 'ximenat136', 'ximena.torres@example.com'),
            ('Yusuf Ahmed', 'yusufa137', 'yusuf.ahmed@example.com'),
            ('Zanele Dlamini', 'zaneled138', 'zanele.dlamini@example.com'),
            ('Anders Lund', 'andersl139', 'anders.lund@example.com'),
            ('Bruna Ferreira', 'brunaf140', 'bruna.ferreira@example.com'),
            ('Chen Wei', 'chenw141', 'chen.wei@example.com'),
            ('Daniela Cruz', 'danielac142', 'daniela.cruz@example.com'),
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