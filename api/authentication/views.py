from rest_framework import generics
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            refresh_token = response.data.get('refresh')
            if refresh_token:
                # For local development, use samesite 'Lax' with secure set to False.
                response.set_cookie(
                    key='refresh_token',
                    value=refresh_token,
                    httponly=True,        # Prevents JavaScript access
                    secure=True,          # Use False in development if not on HTTPS
                    samesite='None',        # 'Lax' works better with secure=False for local testing
                    path='/',
                    max_age=3600,          # Expiration time in seconds
                   
                    
                )
                # Optionally remove the refresh token from the response body.
                response.data.pop('refresh', None)
        return response


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # If the client hasn't supplied the refresh token in the request data,
        # attempt to get it from the cookies.
        if 'refresh' not in request.data:
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                request.data['refresh'] = refresh_token
        return super().post(request, *args, **kwargs)
    
    
    


 
#Passwrod reset

class ForgotPasswordView(APIView):
    # No authentication required for password reset
    permission_classes = []

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        User = get_user_model()
        user = User.objects.filter(email=email).first()
        if user:
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            # Construct your reset URL (this should point to your frontend reset page)
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"
            # Send the email with the reset link
            send_mail(
                subject="Reset Your Password",
                message=f"Click the link below to reset your password:\n{reset_url}\n\nuid: {uid} \ntoken: {token}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        # Always respond with success to avoid email enumeration.
        return Response(
            {"detail": "If an account with that email exists, a password reset link has been sent."},
            status=status.HTTP_200_OK,
        )

class ResetPasswordView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Debugging: Print user details after password reset
        # print(f"Password reset for: {user.email}, New password: {user.password}")

        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )