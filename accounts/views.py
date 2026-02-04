from django.shortcuts import render, redirect
from django.utils.timezone import now, timedelta
from django.db.models import Count

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from accounts.serializers import UserProfileSerializer, UserAccountSerializer, RegisterSerializer, LoginSerializer, LogoutSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer, ChangePasswordSerializer, EmailVerificationSerializer, ResendEmailVerificationSerializer, GoogleLoginSerializer, DeactivateAccountSerializer
from accounts.throttles import AccountUpdateThrottle, RegisterThrottle, LoginThrottle, PasswordResetThrottle, ChangePasswordThrottle, EmailVerificationThrottle, ResendEmailVerificationThrottle, GoogleLoginThrottle, AccountDeactivationThrottle
from accounts.models import User, UserProfile, UserSession, IPActivity, BlacklistedIP
from accounts.utils import IsPlatformAdmin


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
    

class UserAccountView(generics.RetrieveUpdateAPIView):
    serializer_class = UserAccountSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [AccountUpdateThrottle]

    def get_object(self):
        return self.request.user


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': 'Registration successful. Check your email to verify your account.'}, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = {
            'access': serializer.validated_data['access'],
            'refresh': serializer.validated_data['refresh'],
            'user': {
                'id': serializer.validated_data['user'].id,
                'name': serializer.validated_data['user'].name,
                'email': serializer.validated_data['user'].email,
                'username': serializer.validated_data['user'].username,
            }
        }

        return Response(data, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Logged out successfully.'}, status=200)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetThrottle]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'If an account exists, a reset email has been sent.'}, status=200)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data={**request.data, 'uidb64': uidb64, 'token': token})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password reset successful.'}, status=200)
    

class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ChangePasswordThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password updated successfully.'}, status=200)


class VerifyEmailView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [EmailVerificationThrottle]

    def get(self, request, uidb64, token):
        serializer = EmailVerificationSerializer(data={'uidb64': uidb64, 'token': token})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'detail': 'Account successfully verified.'}, status=status.HTTP_200_OK)


class ResendEmailVerificationView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ResendEmailVerificationThrottle]

    def post(self, request):
        serializer = ResendEmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'detail': 'Verification email sent successfully.'}, status=status.HTTP_200_OK,)


class GoogleLoginView(generics.GenericAPIView):
    serializer_class = GoogleLoginSerializer
    permission_classes = [AllowAny]
    throttle_classes = [GoogleLoginThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return Response(data, status=status.HTTP_200_OK)


class DeactivateAccountView(generics.GenericAPIView):
    serializer_class = DeactivateAccountSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [AccountDeactivationThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Account deactivated. You can reactivate by logging in within 30 days.'}, status=status.HTTP_200_OK,)


class AdminDashboardView(APIView):
    #permission_classes = [IsAuthenticated, IsPlatformAdmin]

    def get(self, request):
        last_7_days = now() - timedelta(days=7)

        context = {
            # User metrics
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'platform_admins': User.objects.filter(is_platform_admin=True).count(),
            'deactivated_users': User.objects.filter(is_deactivated=True).count(),
            'new_users_last_7_days': User.objects.filter(date_joined__gte=last_7_days).count(),

            # Session metrics
            'total_sessions': UserSession.objects.count(),
            'active_sessions': UserSession.objects.filter(is_active=True).count(),
            'inactive_sessions': UserSession.objects.filter(is_active=False).count(),
            'unique_devices': UserSession.objects.values('ip_address').distinct().count(),

            # Security metrics
            'suspicious_ips': IPActivity.objects.filter(is_suspicious=True).count(),
            'blacklisted_ips': BlacklistedIP.objects.filter(is_active=True).count(),

            'top_active_ips': IPActivity.objects.values('ip_address')
                .annotate(total=Count('id')).order_by('-total')[:10],
            
            'top_active_users': IPActivity.objects.values('user__email')
                .annotate(total_requests=Count('id')).order_by('-total_requests')[:10],

            'title': 'QELA | Admin Dashboard',
        }

        return render(request, 'admin-analytics/dashboard.html', context)


class AdminUserListView(APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdmin]

    def get(self, request):
        users = User.objects.all().order_by('-date_joined')
        context = {
            'users': users
        }
        return render(request, 'admin_analytics/users.html', context)
    

class AdminProfileListView(APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdmin]

    def get(self, request):
        profiles = UserProfile.objects.select_related('user').all()
        context = {
            'profiles': profiles
        }
        return render(request, 'admin_analytics/profiles.html', context)


class AdminSessionListView(APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdmin]

    def get(self, request):
        sessions = UserSession.objects.select_related('user').all()
        context = {
            'sessions': sessions
        }
        return render(request, 'admin_analytics/sessions.html', context)


class AdminIPActivityView(APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdmin]

    def get(self, request):
        logs = IPActivity.objects.all().order_by('-last_seen')
        context = {
            'logs': logs
        }
        return render(request, 'admin_analytics/ip_activity.html', context)


class AdminBlacklistView(APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdmin]

    def get(self, request):
        ips = BlacklistedIP.objects.all()
        context = {
            'ips': ips
        }
        return render(request, 'admin_analytics/blacklist.html', context)

    def post(self, request):
        ip = request.POST.get('ip_address')
        reason = request.POST.get('reason', 'Manual admin action')

        BlacklistedIP.objects.get_or_create(
            ip_address=ip,
            defaults={'reason': reason}
        )

        return redirect('admin-blacklist')


def testing(request):
    context = {
        'title' : 'QELA - Testing function for templates file',
    }
    return render(request, 'emails/password_reset_email.html', context)