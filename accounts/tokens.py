from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six


class AccountActivatorTokenGenerator(PasswordResetTokenGenerator):
    '''
    Generates a secure token for email verification
    '''

    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_verified)
        )
account_activation_token = AccountActivatorTokenGenerator()


class PasswordResetToken(PasswordResetTokenGenerator):
    '''
    Generates a secure token for password reset.
    '''

    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.password)
        )
password_reset_token = PasswordResetToken()


class EmailChangeTokenGenerator(PasswordResetTokenGenerator):
    '''
    Generates a secure token for email verification
    '''

    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user._new_email or '')
        )
email_verification_token = EmailChangeTokenGenerator()