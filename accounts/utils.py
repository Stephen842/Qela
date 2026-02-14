from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework.permissions import BasePermission

from django.utils import timezone
from datetime import timedelta
from django_redis import get_redis_connection


def check_resend_limit(user_id):
    RESEND_LIMIT = 5
    RESEND_TTL = 60 * 60

    redis = get_redis_connection('default')
    key = f'resend_verification:{user_id}'

    current_count = redis.get(key)

    if current_count and int(current_count) >= RESEND_LIMIT:
        ttl = redis.ttl(key)
        return False, ttl

    pipe = redis.pipeline()
    pipe.incr(key, 1)
    pipe.expire(key, RESEND_TTL)
    pipe.execute()

    return True, None


def blacklist_all_user_tokens(user):
    '''
    Invalidates all refresh tokens for a user.
    Access tokens will naturally expire.
    '''
    tokens = OutstandingToken.objects.filter(user=user)

    for token in tokens:
        BlacklistedToken.objects.get_or_create(token=token)


ACCOUNT_UPDATE_COOLDOWN_DAYS = 90
def can_update_account(user):
    if not user.account_updated_at:
        return True
    
    return timezone.now() >= user.account_updated_at + timedelta(days=ACCOUNT_UPDATE_COOLDOWN_DAYS)


class IsPlatformAdmin(BasePermission):
    '''
    Only allow access to platform-level super admin
    '''

    def has_permission(self, request, view):
        return(request.user.is_authenticated and request.user.is_platform_admin)
