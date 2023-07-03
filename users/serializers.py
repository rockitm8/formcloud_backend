from rest_framework import serializers

from users.models import User
# from django.contrib.auth import get_user_model
# User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
  # phone_number = serializers.IntegerField(source="userprofile.phone_number")
  class Meta:
    model = User
    fields = ('password', 'email', 'first_name', 'last_name')

  def create(self, validated_data):
    user = User.objects.create(email=validated_data['email'],
       password=validated_data['password'], first_name=validated_data['first_name'], last_name=validated_data['last_name'])

    return user

class UserLoginSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(max_length=255)
  class Meta:
    model = User
    fields = ['email', 'password']