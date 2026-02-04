from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.serializers import SocialLoginSerializer

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils import timezone

from accounts.models import User, UserProfile
from accounts.tokens import account_activation_token, password_reset_token
from accounts.tasks import send_account_activation_email, send_password_reset_email, send_email_change_verification
from accounts.utils import check_resend_limit, blacklist_all_user_tokens, can_update_account


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'country', 'phone_number', 'gender', 'skills', 'location']


class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'username', 'email']

    def validate(self, attrs):
        user = self.instance

        if not can_update_account(user):
            raise serializers.ValidationError('You can only update your account details once every 90 days.')
        
        return attrs

    def update(self, instance, validated_data):
        new_email = validated_data.get('email', instance.email)

        # If email change, mark pending verification
        if new_email != instance.email:
            instance._new_email = new_email
            instance.email_verification_pending = True

            # Send verification email to new email
            send_email_change_verification.delay(instance.id, email=new_email)

        # Update other fields
        instance.name = validated_data.get('name', instance.name)
        instance.username = validated_data.get('username', instance.username)
        instance.save(update_fields=['name', 'username', '_new_email', 'email_verification_pending', 'account_updated_at'])
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, validators=[validate_password], label='Password')
    password2 = serializers.CharField(write_only=True, label='Confirm Password')

    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']

    def validate_username(self, value):
        value = value.lower()
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('Username already taken.')
        return value

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Email already in use.')
        return value

    def validate(self, attrs):
        '''Ensure both passwords match.'''
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password1')
        validated_data.pop('password2', None)

        user = User.objects.create_user(password=password, **validated_data)

        # Async email sending
        send_account_activation_email.delay(user.id)

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError('Both username/email and password are required.')

        user = authenticate(request=self.context.get('request'), username=username, password=password)

        if not user:
            raise serializers.ValidationError('Invalid login credentials.')

        if not user.is_active:
            raise serializers.ValidationError('Account is not active. Please verify your email.')
        if not user.is_verified:
            raise serializers.ValidationError('Account is not verified. Check your email.')

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        attrs['access'] = str(refresh.access_token)
        attrs['refresh'] = str(refresh)
        attrs['user'] = user

        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self):
        try:
            token = RefreshToken(self.validated_data['refresh'])
            token.blacklist()
        except TokenError:
            pass


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        try:
            self.user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            self.user = None
        return email

    def save(self):
        if self.user:
            send_password_reset_email.delay(self.user.id)


class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    password1 = serializers.CharField(write_only=True, validators = [validate_password])
    password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})

        try:
            uid = force_str(urlsafe_base64_decode(attrs['uidb64']))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            raise serializers.ValidationError('Invalid reset link.')

        if not password_reset_token.check_token(user, attrs['token']):
            raise serializers.ValidationError('Reset link is invalid or expired.')

        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['password1'])
        user.save(update_fields=['password'])
        blacklist_all_user_tokens(user)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password1 = serializers.CharField(write_only=True, validators=[validate_password], label='New password')
    new_password2 = serializers.CharField(write_only=True, label='Confirm new password')

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value
    
    def validate(self, attrs):
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password2': 'Passwords do not match.'})
        
        if attrs['old_password'] == attrs['new_password1']:
            raise serializers.ValidationError({'new_password1': 'New password must be different from the old password.'})
        
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password1'])
        user.save(update_fields=['password'])
        blacklist_all_user_tokens(user)
        return user


class EmailVerificationSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uidb64']))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            raise serializers.ValidationError('Invalid activation link.')

        if not account_activation_token.check_token(user, attrs['token']):
            raise serializers.ValidationError('Activation link is invalid or expired.')

        if user.is_verified and not user.email_verification_pending:
            raise serializers.ValidationError('Account already verified.')

        attrs['user'] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user']

        # Handle email verification for pending email updates
        if user.email_verification_pending and user._new_email:
            user.email = user._new_email
            user._new_email = None
            user.email_verification_pending = False

        user.is_verified = True
        user.is_active = True
        user.save(update_fields=['email', '_new_email', 'email_verification_pending', 'is_verified', 'is_active'])
        return user


class ResendEmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('User with this email does not exist.')

        if user.is_verified:
            raise serializers.ValidationError('Account is already verified.')

        allowed, ttl = check_resend_limit(user.id)
        if not allowed:
            minutes = max(1, ttl // 60)
            raise serializers.ValidationError(
                f'Too many requests. Try again in {minutes} minute(s).'
            )

        self.user = user
        return email

    def save(self):
        send_account_activation_email.delay(self.user.id)
    

class GoogleLoginSerializer(serializers.Serializer):
    access_token = serializers.CharField(write_only=True)
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)
    user = serializers.DictField(read_only=True)

    def validate(self, attrs):
        request = self.context['request']
        access_token = attrs.get('access_token')

        if not access_token:
            raise serializers.ValidationError('Access token is required.')
        
        try:
            # Initialize allauth adapter
            adapter = GoogleOAuth2Adapter()
            app = adapter.get_provider().get_app(request)

            # Parse and validate token
            token = adapter.parse_token({'access_token': access_token})
            token.app = app

            # Complete social login
            login = adapter.complete_login(
                request,
                app,
                token,
                response={'access_token': access_token}
            )
            login.token = token
            login.save(request)
        except Exception:
            raise serializers.ValidationError('Invalid or expired Google token.')

        user = login.account.user

        # Auto-verify and activate Google users
        if not user.is_verified:
            user.is_verified = True
            user.is_active = True
            user.save(update_fields=['is_verified', 'is_active'])

        # Issue JWT tokens
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'username': user.username,
                'is_verified': user.is_verified,
                'is_active': user.is_active,
            },
        }


class DeactivateAccountSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if value is not True:
            raise serializers.ValidationError('You must confirm deactivation.')
        return value
    
    def save(self, **kwargs):
        user = self.context['request'].user
        user.is_deactivated = True
        user.deactivated_at =timezone.now()
        user.is_active = False
        user.save(update_fields=['is_deactivated', 'deactivated_at', 'is_active'])
        return user