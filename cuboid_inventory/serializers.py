from rest_framework import serializers
from .models import *


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, max_length=128, style={'input_type': 'password'})

class NonStaffBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = ['length', 'breadth', 'height', 'area', 'volume']

        
class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = fields = '__all__'