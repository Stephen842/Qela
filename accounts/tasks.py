from celery import shared_task

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import timezone
from datetime import datetime, timedelta

from django.db import transaction

from accounts.models import User, IPActivity, BlacklistedIP
from accounts.tokens import account_activation_token, password_reset_token, email_verification_token


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={'max_retries': 3})
def send_account_activation_email(self, user_id):
    user = User.objects.get(id=user_id)

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)

    activation_link = f'{settings.FRONTEND_URL}/auth/verify-email/{uid}/{token}'

    context = {
        'user': user,
        'activation_link': activation_link,
    }

    subject = 'Activate Your QELA Account'

    text_body = render_to_string('emails/account_activation_email.txt', context)
    html_body = render_to_string('emails/account_activation_email.html', context)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    email.attach_alternative(html_body, 'text/html')
    email.send()


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={'max_retries': 3},)
def send_password_reset_email(self, user_id):
    user = User.objects.get(id=user_id)

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = password_reset_token.make_token(user)

    reset_link = f'{settings.FRONTEND_URL}/auth/password-reset-confirm/{uid}/{token}'

    context = {
        'user': user,
        'reset_link': reset_link,
    }

    subject = 'Reset Your QELA Password'

    text_body = render_to_string('emails/password_reset_email.txt', context)
    html_body = render_to_string('emails/password_reset_email.html', context)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    email.attach_alternative(html_body, 'text/html')
    email.send()


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={'max_retries': 3})
def send_email_change_verification(self, user_id, new_email):
    user = User.objects.get(id=user_id)

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    verification_link = f'{settings.FRONTEND_URL}/auth/verify-email/{uid}/{token}'

    context = {
        'user': user,
        'verification_link': verification_link,
        'new_email': new_email,
    }

    subject = 'Confirm Your QELA New Email Address'

    text_body = render_to_string('emails/email_change_verification.txt', context)
    html_body = render_to_string('emails/email_change_verification.html', context)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[new_email],
    )

    email.attach_alternative(html_body, 'text/html')
    email.send()


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_kwargs={"max_retries": 3})
def delete_deactivated_accounts_after_grace_period(self):
    '''
    Permanently deletes user accounts that were explicitly deactivated
    and have remained inactive for 30 days.
    '''
    grace_period = timezone.now() - timedelta(days=30)
    users_to_delete = User.objects.filter(is_deactivated=True, deactivated_at__lte=grace_period)
    
    with transaction.atomic():
        for user in users_to_delete:
            user.delete()


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_kwargs={"max_retries": 3})
def auto_blacklist_suspicious_ips(self):
    '''
    Two-stage protection:
    1) 75 requests in 2 minutes - mark suspicious (warning only)
    2) 100 requests in 3 minutes - blacklist IP
    '''
    window_2_min = datetime.now() - timedelta(minutes=2)
    window_3_min = datetime.now() - timedelta(minutes=3)

    # ---- STAGE 1: FLAG SUSPICIOUS (WARNING ONLY) ----
    suspicious_ips = IPActivity.objects.filter(
        last_seen__gte=window_2_min,
        request_count__gte=75,
        is_suspicious=False
    )

    # ---- STAGE 2: ACTUAL BLACKLISTING ----
    abusive_ips = IPActivity.objects.filter(
        last_seen__gte=window_3_min,
        request_count__gte=100,
    )

    with transaction.atomic():
        for activity in suspicious_ips:
            activity.is_suspicious = True
            activity.save(update_fields=['is_suspicious'])

        for activity in abusive_ips:
            BlacklistedIP.objects.get_or_create(
                ip_address=activity.ip_address,
                defaults={'reason': 'Too many requests in short time'}
            )
