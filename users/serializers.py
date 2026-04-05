from rest_framework import serializers
from .models import User

# Domain: users | Purpose: Serialization and validation for User create and update


class UserSerializer(serializers.ModelSerializer):
    # Handles restricted onboarding and secure profile modifications across the system
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        required=True,
    )

    class Meta:
        model = User
        fields = ("id", "username", "email", "role", "is_active", "password", "date_joined")
        read_only_fields = ("id", "date_joined")

    def create(self, validated_data):
        # create_user hashes the password; plain create() would store it raw
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
            role=validated_data.get("role", User.UserRole.VIEWER),
            is_active=validated_data.get("is_active", True),
        )

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # None means the field was absent from the request; empty string is an invalid password
        if password is not None:
            instance.set_password(password)

        instance.save()
        return instance
