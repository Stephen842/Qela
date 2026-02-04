from django.urls import path, include
from accounts.views import RegisterView, LoginView, LogoutView, VerifyEmailView, ResendEmailVerificationView, PasswordResetRequestView, PasswordResetConfirmView, ChangePasswordView, UserAccountView, UserProfileView, GoogleLoginView, DeactivateAccountView, AdminDashboardView, AdminUserListView, AdminProfileListView, AdminSessionListView, AdminIPActivityView, AdminBlacklistView
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
    # Super admin dashboard & analytics
    # -------------------------
    path('super-admin-dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('users/', AdminUserListView.as_view(), name='admin-users'),
    path('profiles/', AdminProfileListView.as_view(), name='admin-profiles'),
    path('sessions/', AdminSessionListView.as_view(), name='admin-sessions'),
    path('ip-activity/', AdminIPActivityView.as_view(), name='admin-ip-activity'),
    path('blacklist/', AdminBlacklistView.as_view(), name='admin-blacklist'),


    # -------------------------
    # Testing of template files
    # -------------------------
    path('testing/', views.testing, name='testing'),
]