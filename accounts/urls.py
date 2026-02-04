from django.urls import path, include
from accounts.views import RegisterView, LoginView, LogoutView, VerifyEmailView, ResendEmailVerificationView, PasswordResetRequestView, PasswordResetConfirmView, ChangePasswordView, UserAccountView, UserProfileView, GoogleLoginView, DeactivateAccountView 
from . import views

urlpatterns = [
    # -------------------------
    # Auth / JWT
    # -------------------------
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),

    # -------------------------
    # Email verification
    # -------------------------
    path('auth/verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('auth/resend-verification/', ResendEmailVerificationView.as_view(), name='resend-verification'),

    # -------------------------
    # Password reset
    # -------------------------
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('auth/password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    # -------------------------
    # Password change (authenticated)
    # -------------------------
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),

    # -------------------------
    # Google OAuth
    # -------------------------
    path('auth/google/login/', GoogleLoginView.as_view(), name='google-login'),
    path('auth/', include('dj_rest_auth.urls')),

    # -------------------------
    # Account & Profile settings & Account deactivation
    # -------------------------
    path('settings/', UserAccountView.as_view(), name='account-settings'),
    path('profile/', UserProfileView.as_view(), name='profile-settings'),
    path('deactivate/', DeactivateAccountView.as_view(), name='account-deactivate'),


    # -------------------------
    # Testing of template files
    # -------------------------
    path('testing/', views.testing, name='testing'),
]