from django.shortcuts import render
from rest_framework import viewsets, generics
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate

from users.serializers import UserLoginSerializer, UserSerializer
from users.models import User

# from django.contrib.auth import get_user_model
# User = get_user_model()

# Create your views here.
class UserRegisterationViewSet(viewsets.ModelViewSet):
  serializer_class = UserSerializer
  queryset = User.objects.all()

class UserLoginViewSet(generics.GenericAPIView):
  serializer_class = UserSerializer
  queryset = User.objects.all()

  def post(self, request):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    password = serializer.data.get('password')
    user = User.objects.get(email=email, password=password)
    if user is not None:
      token = Token.objects.get(user=user)
      return Response({'token': token.key}, status=status.HTTP_200_OK)
    else:
      return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)

    
    # if user is not None:
