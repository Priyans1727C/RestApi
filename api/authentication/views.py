from rest_framework import generics
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

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