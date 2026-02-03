from django.shortcuts import render

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from accounts.serializers import UserProfileSerializer, UserAccountSerializer, RegisterSerializer, LoginSerializer, LogoutSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer, ChangePasswordSerializer, EmailVerificationSerializer, ResendEmailVerificationSerializer, DeactivateAccountSerializer
from accounts.throttles import AccountUpdateThrottle, RegisterThrottle, LoginThrottle, PasswordResetThrottle, ChangePasswordThrottle, EmailVerificationThrottle, ResendEmailVerificationThrottle, AccountDeactivationThrottle


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


class DeactivateAccountView(generics.GenericAPIView):
    serializer_class = DeactivateAccountSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [AccountDeactivationThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Account deactivated. You can reactivate by logging in within 30 days.'}, status=status.HTTP_200_OK,)


def testing(request):
    context = {
        'title' : 'QELA - Testing function for templates file',
    }
    return render(request, 'emails/email_change_verification.html', context)