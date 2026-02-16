from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.timezone import now, timedelta
from django.utils import timezone
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django_countries import countries

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from accounts.serializers import UserProfileSerializer, UserAccountSerializer, RegisterSerializer, LoginSerializer, LogoutSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer, ChangePasswordSerializer, EmailVerificationSerializer, ResendEmailVerificationSerializer, GoogleLoginSerializer, DeactivateAccountSerializer
from accounts.throttles import AccountUpdateThrottle, RegisterThrottle, LoginThrottle, PasswordResetThrottle, ChangePasswordThrottle, EmailVerificationThrottle, ResendEmailVerificationThrottle, GoogleLoginThrottle, AccountDeactivationThrottle
from accounts.models import User, UserProfile, UserSession, IPActivity, BlacklistedIP
from accounts.utils import IsPlatformAdmin
from accounts.country import COUNTRY_COORDS


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
    permission_classes = [IsAuthenticated, IsPlatformAdmin]

    def get(self, request):
        total_users = User.objects.count()
        now = timezone.now()
        last_7_days = now - timedelta(days=7)
        fourteen_days_ago = now - timedelta(days=14)

        # Real per-day signup data
        daily_signups = (
            User.objects.filter(date_joined__gte=last_7_days)
            .annotate(day=TruncDate('date_joined'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )

        # Convert queryset to list for JSON
        signup_data = [
            {'day': str(item['day']), 'count': item['count']}
            for item in daily_signups
        ]

        country_stats = (
            UserProfile.objects.values('country')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        formatted_countries = []

        for item in country_stats:
            country_code = item['country']
            #if not country_code:
                #continue

            country_name = dict(countries).get(country_code, 'Unknown') if country_code else 'Unknown'

            percent = round((item['total'] / total_users) * 100, 1) if total_users else 0

            formatted_countries.append({
                'code': country_code,
                'name': country_name,
                'percent': percent,
                'coords': COUNTRY_COORDS.get(country_code, [0, 0])
            })
        top_countries = formatted_countries[:5]

        new_users_this_week = User.objects.filter(date_joined__gte=last_7_days).count()
        
        new_users_prev_week = User.objects.filter(date_joined__gte=fourteen_days_ago, date_joined__lt=last_7_days).count()

        if new_users_prev_week > 0:
            growth_pct = round(((new_users_this_week - new_users_prev_week) / new_users_prev_week) * 100, 1)
        elif new_users_this_week > 0:
            growth_pct = 100.0
        else:
            growth_pct = 0

        context = {
            # User metrics
            'total_users': total_users,
            'active_users': User.objects.filter(is_active=True, last_activity__gte=last_7_days).count(),
            'verified_users': User.objects.filter(is_verified=True).count(),
            'platform_admins': User.objects.filter(is_platform_admin=True).count(),
            'deactivated_users': User.objects.filter(is_deactivated=True).count(),
            'new_users_this_week': new_users_this_week,

            # Session metrics
            'total_sessions': UserSession.objects.count(),
            'active_sessions': UserSession.objects.filter(is_active=True).count(),
            'inactive_sessions': UserSession.objects.filter(is_active=False).count(),
            'unique_devices': UserSession.objects.values('ip_address').distinct().count(),

            # Security metrics
            'suspicious_ips': IPActivity.objects.filter(is_suspicious=True).count(),
            'blacklisted_ips': BlacklistedIP.objects.filter(is_active=True).count(),

            'top_active_ips': (
                IPActivity.objects
                .values('ip_address')
                .annotate(total=Count('id'))
                .order_by('-total')[:10]
            ),
            
            'top_active_users': (
                IPActivity.objects
                .exclude(user__isnull=True)
                .values('user__email')
                .annotate(total_requests=Count('id'))
                .order_by('-total_requests')[:10]
            ),

            'all_countries': formatted_countries,
            'top_countries': top_countries,

            'signup_data_last_7_days': signup_data,

            'user_growth_percent': growth_pct,

            'title': 'QELA | Admin Dashboard',
        }

        return render(request, 'admin-analytics/dashboard.html', context)


class AdminUserListView(APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdmin]

    def get(self, request):
        # Handle Filtration
        query = User.objects.select_related('profile').all().order_by('-date_joined')
        
        # Search functionality
        search = request.GET.get('search')
        if search:
            query = query.filter(
                Q(username__icontains=search) | 
                Q(name__icontains=search) | 
                Q(email__icontains=search)
            )

        # Status Filtration
        status = request.GET.get('status')
        if status == 'active':
            query = query.filter(is_active=True, is_deactivated=False)
        elif status == 'unverified':
            query = query.filter(is_verified=False)
        elif status == 'suspended':
            # Account is disabled by admin but not deleted by user
            query = query.filter(is_active=False, is_deactivated=False)
        elif status == 'deactivated':
            # User-initiated account closure
            query = query.filter(is_deactivated=True)

        # Role Filtration
        role = request.GET.get('role')
        if role == 'admin':
            query = query.filter(is_platform_admin=True)
        elif role == 'member':
            query = query.filter(is_platform_admin=False)

        # 2. Analytics Calculations
        total_users = User.objects.count()
        total_active = User.objects.filter(is_active=True, is_deactivated=False).count()
        total_deactivated = User.objects.filter(is_deactivated=True).count()
        total_inactive = User.objects.filter(is_active=False, is_deactivated=False).count()
        total_verified = User.objects.filter(is_verified=True).count()
        
        top_country_query = (
            UserProfile.objects.values('country')
            .annotate(total=Count('id'))
            .order_by('-total')[:5]
        )

        formatted_countries = []
        for item in top_country_query:
            country_code = item['country']
            country_name = dict(countries).get(country_code, 'Unknown') if country_code else 'Unknown'
            percent = round((item['total'] / total_users) * 100, 1) if total_users else 0

            formatted_countries.append({
                'name': country_name,
                'percent': percent,
            })

        context = {
            'users': query,
            'top_countries': formatted_countries,
            'stats': {
                'total': total_users,
                'active': total_active,
                'deactivated': total_deactivated,
                'inactive': total_inactive,
                'verified': total_verified,
            },
            'title': 'QELA | Admin User Registry',
        }
        
        return render(request, 'admin-analytics/users.html', context)
    
    def post(self, request):
        '''Handle status toggling'''
        user_id = request.data.get('user_id')
        action = request.data.get('action')
        user_to_mod = get_object_or_404(User, id=user_id)

        if action == 'toggle_active':
            # Prevent self-suspension
            if user_to_mod == request.user:
                messages.error(request, 'Security Alert: You cannot suspend your own administrative account.')
            else:
                user_to_mod.is_active = not user_to_mod.is_active
                user_to_mod.save()
                status = 'activated' if user_to_mod.is_active else 'suspended'
                messages.success(request, f'User {user_to_mod.username} successfully {status}.')
        
        return redirect('admin-users')
    

class AdminProfileListView(APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdmin]

    def get(self, request, username):
        # Fetch user or 404
        user_obj = get_object_or_404(User.objects.select_related('profile'), username__iexact=username)
        
        # Calculate account age
        account_age = (timezone.now() - user_obj.date_joined).days

        context = {
            'user': user_obj,
            'profile': user_obj.profile,
            'account_age': account_age,
            'title': f'Qela | User Profile -  {user_obj.username}'
        }
        return render(request, 'admin-analytics/profiles.html', context)


class AdminSessionListView(APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdmin]

    def get(self, request):
        sessions = UserSession.objects.select_related('user').all()
        
        status = request.GET.get('status')
        if status == 'active':
            sessions = sessions.filter(is_active=True)

        search = request.GET.get('search')
        if search:
            sessions = sessions.filter(
                Q(user__email__icontains=search) | 
                Q(ip_address__icontains=search) |
                Q(browser__icontains=search)
            )

        context = {
            'sessions': sessions
        }
        return render(request, 'admin-analytics/sessions.html', context)


class AdminIPActivityView(APIView):
    permission_classes = [IsAuthenticated, IsPlatformAdmin]

    def get(self, request):
        logs = IPActivity.objects.select_related('user').all().order_by('-last_seen')
        
        # Quick filter for security threats
        if request.GET.get('filter') == 'suspicious':
            logs = logs.filter(is_suspicious=True)

        context = {
            'logs': logs
        }
        return render(request, 'admin-analytics/ip_activity.html', context)


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

    def delete(self, request, ip_id):
        ip_entry = get_object_or_404(BlacklistedIP, id=ip_id)
        ip_entry.delete()
        messages.success(request,f'IP {ip_entry.ip_address} has been whitelisted')
        return redirect('admin-blacklist')


def testing(request):
    context = {
        'title' : 'QELA - Testing function for templates file',
    }
    return render(request, 'emails/password_reset_email.html', context)