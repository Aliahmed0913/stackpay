from rest_framework import serializers
from django.contrib.auth import get_user_model
from .validators import validate_password, validate_phone_number
from users.services.verifying_code import VerificationCodeService
from Restaurant.settings import CODE_LENGTH
import logging
logger = logging.getLogger(__name__)



user = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta():
        model = user
        fields = ['id', 'username', 'role_management', 'email', 'phone_number', 'password' , 'is_active']
        extra_kwargs={
            'password': {'write_only': True},
            'is_active':{'read_only': True}
        }
    
    def update(self, instance, validated_data):
        request = self.context['request']
        if 'role_management' in validated_data:
            user_role = validated_data['role_management']
            if user_role == 'ADMIN' and request.user.role_management != 'ADMIN':
                validated_data.pop('role_management')
                logger.warning(f'{request.user.username} can\'t upgrade herself to admin')
            
        if 'password' in validated_data:
            validated_data.pop('password')
            logger.warning('This endpoint can\'t update passwords')
            
        return super().update(instance, validated_data)
    
    def validate_password(self, value):    
        return validate_password(value)
   
    def validate_phone_number(self, value):    
        return validate_phone_number(value)
        
    def create(self, validated_data):
        c_user = user.objects.create_user(**validated_data)
        service = VerificationCodeService(c_user)
        service.create_code()
        return c_user

class EmailCodeVerificationSerializer(serializers.Serializer):
        email = serializers.EmailField()
        code = serializers.CharField(required=False,max_length=CODE_LENGTH,min_length=CODE_LENGTH)