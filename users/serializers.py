from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['id', 'username', 'role_management', 'email', 'phone_number', 'password']
        extra_kwargs={
            'password': {'write_only': True}
        }
    