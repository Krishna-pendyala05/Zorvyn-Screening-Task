from rest_framework import serializers
from .models import User

# Domain: users | Purpose: Serialization of user records for RBAC and identity management

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the Custom User model.
    Handles account creation and listing while keeping passwords secure.
    """
    password = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'},
        required=True
    )

    class Meta:
        model = User
        fields = (
            "id", 
            "username", 
            "email", 
            "role", 
            "is_active", 
            "password",
            "date_joined",
        )
        read_only_fields = ("id", "date_joined")

    def create(self, validated_data):
        """
        Create and return a new User with a hashed password.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', User.UserRole.VIEWER),
            is_active=validated_data.get('is_active', True)
        )
        return user

    def update(self, instance, validated_data):
        """
        Update and return an existing User, correctly hashing the password if provided.
        """
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance
