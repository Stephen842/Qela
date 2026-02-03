from django.contrib.auth.backends import BaseBackend
from django.utils import timezone
from datetime import timedelta
from .models import User

class CustomAuthBackend(BaseBackend):
    '''
    Custom authentication backend:
    - Login with email or username (case-insensitive)
    - Reactivates deactivated users if they log in within 30 days
    - Blocks login if deactivation period has expired
    '''
    def authenticate(self, request, username=None, password=None, **kwargs):
        login_value = username or kwargs.get('email')
        if not login_value or not password:
            return None
            
        login_value = login_value.lower() # Ensure case insensitivity

        # Fetch user by email or username
        if '@' in login_value:
            user = User.objects.filter(email__iexact=login_value).first()
        else:
            user = User.objects.filter(username__iexact=login_value).first()

        # Check password and account status
        if not user or not user.check_password(password):
            return None

        # Handle deactivated accounts
        if user.is_deactivated:
            if not user.deactivated_at:
                return None
            
            # Check 30-days grace period
            if timezone.now() <= user.deactivated_at + timedelta(days=30):
                # reactivate accounts
                user.is_deactivated = False
                user.is_active = True
                user.deactivated_at = None
                user.save(update_fields=['is_deactivated', 'is_active', 'deactivated_at'])
            else:
                # Grace period expired - block login
                return None
            
        # Block inactive users
        if not user.is_active:
            return None

        return user            

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None