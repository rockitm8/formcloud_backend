from django.shortcuts import render
from rest_framework import viewsets, generics
from tasks.serializers import PresetSerializer, TaskSerializer, DomainSerializer
from tasks.models import Preset, Task, Domain
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView


from users.models import User
# from django.contrib.auth.models import User


index = never_cache(TemplateView.as_view(template_name='index.html'))
# Create your views here.
class TaskViewSet(generics.ListCreateAPIView):
  serializer_class = TaskSerializer
  queryset= Task.objects.all()

  def post(self, request, *args, **kwargs):
    authHeader = request.headers['Authorization']
    # user id from token
    token = Token.objects.get(key=authHeader)
    user = User.objects.get(email = token.user)

    request.data['user'] = user.id
    return self.create(request, *args, **kwargs)
  
  def get(self, request):
    authHeader = request.headers['Authorization']
    # user id from token
    token = Token.objects.get(key=authHeader)
    user = User.objects.get(email = token.user)
    tasks = Task.objects.filter(user=user)
    serializer = self.get_serializer(tasks, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)
  
def deletetask(request, id):
  task = Task.objects.get(id=id)
  task.delete()
  return HttpResponseRedirect('https://app.formcloud.ai/#/tasks')

class DomainViewSet(generics.ListCreateAPIView):
  serializer_class = DomainSerializer
  queryset= Domain.objects.all()

  def post(self, request, *args, **kwargs):
    return self.create(request, *args, **kwargs)
  
  def get(self, request, pk):
    domains = Domain.objects.filter(task=pk)
    serializer = self.get_serializer(domains, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

class TaskDetailViewSet(generics.RetrieveUpdateDestroyAPIView):
  serializer_class = DomainSerializer
  queryset= Domain.objects.all()

  def retrieve(self, request, pk):
    domains = Domain.objects.filter(task=pk)

    task_detail = {
      "contact_pages": len(domains.exclude(contact_page="None")),
      "contact_forms": len(domains.filter(contact_form=True)),
      "forms_sent": len(domains.filter(form_sent=True)),
      "went_manually": len(domains.filter(went_over_manually=True)),
      "sent_manually": len(domains.filter(sent_manually=True)),
      "domains": len(domains)
    }
    # serializer = self.get_serializer(task_detail, many=True)

    return Response(task_detail, status=status.HTTP_200_OK)

class PresetViewSet(generics.ListCreateAPIView):
  serializer_class = PresetSerializer
  queryset= Preset.objects.all()

  def post(self, request, *args, **kwargs):
    authHeader = request.headers['Authorization']
    # user id from token
    token = Token.objects.get(key=authHeader)
    user = User.objects.get(email = token.user)

    request.data['user'] = user.id
    return self.create(request, *args, **kwargs)
  
  def get(self, request):
    authHeader = request.headers['Authorization']
    # user id from token
    token = Token.objects.get(key=authHeader)
    user = User.objects.get(email = token.user)
    presets = Preset.objects.filter(user=user)
    serializer = self.get_serializer(presets, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)
