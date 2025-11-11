from rest_framework import serializers
from reviews.models import CustomUser


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class VerifySerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()
