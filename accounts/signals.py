from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added

from .models import User, UserProfile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(social_account_added)
def create_profile_for_google_user(request, sociallogin, **kwargs):
    user = sociallogin.user
    # Only create profile if it doesn’t exist
    UserProfile.objects.get_or_create(user=user)