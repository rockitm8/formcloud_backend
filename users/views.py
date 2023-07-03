from django.shortcuts import render
from rest_framework import viewsets, generics
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string, get_template
from django.utils.encoding import force_bytes

from users.serializers import UserLoginSerializer, UserSerializer
from users.models import User
from users.utils import Util


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        print(user.email)
        body = 'Your account has been activated!'
        data = {
          'subject':'Formcloud Registration Completed',
          'body':body,
          'to_email': user.email
        }
        Util.send_email(data)
        print('noob')
        return Response({'success': "Otp is correct!"})
    else:
        return Response({'error': "Otp is wrong!"})

# Create your views here.
class UserRegisterationViewSet(viewsets.ModelViewSet):
  serializer_class = UserSerializer
  queryset = User.objects.all()

  def create(self, request, *args, **kwargs):
    body = request.data
    try:
      user = User.objects.create_user(body['email'], body['password'], body['first_name'], body['last_name'])
      user.is_active = False
      user.save()


      #current_site = get_current_site(request)
      #current_domain = current_site.domain
      uid = urlsafe_base64_encode(force_bytes(user.pk))
      token = default_token_generator.make_token(user)
      # mail_subject = 'Activate your account.'
      # message = render_to_string('account_activation.html', {
      #   'user': user,
      #   'domain': current_site.domain,
      #   'uid': urlsafe_base64_encode(force_bytes(user.pk)),
      #   'token': default_token_generator.make_token(user),
      # })

      link = f'https://app.formcloud.ai/activateAccount?uidb64={uid}&token={token}'
      body = f'Please click on the link to confirm your registration, {link}. If you think, it\'s not you, then just ignore this email.'
      data = {
        'subject':'Registeration link for Formcloud',
        'body':body,
        'to_email': request.data['email']
      }
      Util.send_email(data)
      return Response({'success': "Otp link sent."})
    except:
        return Response({'error': "Email already exists"})


class UserLoginViewSet(generics.GenericAPIView):
  serializer_class = UserSerializer
  queryset = User.objects.all()

  def post(self, request):
    try:
      serializer = UserLoginSerializer(data=request.data)
      serializer.is_valid()
      #print(t)
      email = serializer.data.get('email')
      password = serializer.data.get('password')
      #user = User.objects.get(email=email)
      user = authenticate(request, email=email, password=password)
      if user is not None:
        token = Token.objects.get(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
      else:
        print(User.objects.get(email=email).is_active)
        if User.objects.get(email=email).is_active:
          return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)
        else:
          return Response({'errors':{'non_field_errors':['Email is not activated. Please check your email!']}}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
       return Response({'errors':e.message})
    # if user is not None:
