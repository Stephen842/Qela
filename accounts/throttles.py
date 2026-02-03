from rest_framework.throttling import ScopedRateThrottle

class LoginThrottle(ScopedRateThrottle):
    scope = 'login'


class RegisterThrottle(ScopedRateThrottle):
    scope = 'register'


class EmailVerificationThrottle(ScopedRateThrottle):
    scope = 'verify_email'


class ResendEmailVerificationThrottle(ScopedRateThrottle):
    scope = 'resend_verification'


class PasswordResetThrottle(ScopedRateThrottle):
    scope = 'password_reset'


class ChangePasswordThrottle(ScopedRateThrottle):
    scope = 'change_password'


class AccountUpdateThrottle(ScopedRateThrottle):
    scope = 'account_update'


class AccountDeactivationThrottle(ScopedRateThrottle):
    scope = 'account_deactivate'