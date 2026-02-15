from django.core.management.base import BaseCommand
from accounts.models import UserProfile
from django_countries import countries
import random

class Command(BaseCommand):
    help = "Populate empty UserProfile fields safely"

    def handle(self, *args, **kwargs):
        bios = [
            "Loves coding and exploring new tech.",
            "Passionate about blockchain and AI.",
            "Enjoys learning new programming languages.",
            "Avid reader and lifelong learner.",
            "Tech enthusiast and gamer.",
            "Creative thinker with a love for problem solving.",
            "Explorer of both virtual and real worlds.",
            "Motivated to make a difference in the tech community.",
            "Dedicated to building scalable software.",
            "Always seeking new challenges."
        ]

        genders = ['male', 'female', 'other']
        country_codes = [code for code, name in countries]

        profiles = UserProfile.objects.all()

        # Get existing phone numbers to avoid duplicates
        existing_numbers = set(
            UserProfile.objects.exclude(phone_number__isnull=True)
            .values_list("phone_number", flat=True)
        )

        counter = 1

        for profile in profiles:
            updated = False

            if not profile.bio:
                profile.bio = random.choice(bios)
                updated = True

            if not profile.gender:
                profile.gender = random.choice(genders)
                updated = True

            if not profile.country:
                profile.country = random.choice(country_codes)
                updated = True

            if not profile.phone_number:
                # Generate unique phone number
                while True:
                    phone_number = f"+23480{10000000 + counter}"
                    counter += 1
                    if phone_number not in existing_numbers:
                        existing_numbers.add(phone_number)
                        profile.phone_number = phone_number
                        updated = True
                        break

            if updated:
                profile.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Updated profile for {profile.user.email}")
                )
