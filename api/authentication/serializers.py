from rest_framework import serializers
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.core.validators import validate_email
from django.core.exceptions import ValidationError



User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'full_name','email','password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            full_name=validated_data.get('full_name', ''),
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user





class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    identifier = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the default 'username' field so it isn't required in input
        self.fields.pop("username")

    def validate(self, attrs):
        identifier = attrs.get("identifier")
        password = attrs.get("password")

        if not identifier or not password:
            raise serializers.ValidationError("Both identifier and password are required.")

        # Try to get the user by email; if not found, try username
        user = User.objects.filter(email=identifier).first()
        if user is None:
            user = User.objects.filter(username=identifier).first()

        if user is None:
            raise serializers.ValidationError("Invalid credentials.")

        # Set the username in attrs for the parent class to process authentication
        attrs["username"] = user.username
        return super().validate(attrs)
    
    
    
