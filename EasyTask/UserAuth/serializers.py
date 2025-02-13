from rest_framework import serializers
from .models import Auth
import re
from django.contrib.auth.password_validation import validate_password

regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')


class AuthModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auth
        fields = '__all__'

    def get_user_by_email(self, email):
        try:
            user = Auth.objects.get(email=email)
            return user
        except Exception as e:
            raise serializers.ValidationError('Invalid email')

    def validate_password(self, password):
        try:
            validate_password(password)
            return password
        except Exception as e:
            raise serializers.ValidationError(e.__cause__)

    def validate_email(self, email):
        return email

    def validate_mobile_number(self, mobile_number):
        return mobile_number

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Auth(**validated_data)
        user.set_password(password)
        user.save()
        return user
