from django.shortcuts import render
from rest_framework import viewsets, generics
from tasks.serializers import TaskSerializer, DomainSerializer
from tasks.models import Task, Domain
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status

from users.models import User
# from django.contrib.auth.models import User

# Create your views here.
class TaskViewSet(generics.ListCreateAPIView):
  serializer_class = TaskSerializer
  queryset= Task.objects.all()

  def post(self, request, *args, **kwargs):
    authHeader = request.headers['Authorization']
    # user id from token
    token = Token.objects.get(key=authHeader)
    user = User.objects.get(user_name = token.user)

    request.data['user'] = user.id
    # task = self.create(request, *args, **kwargs)
    #print("/////////////////////////////////")
    # print(task.data.id)
    # for d in request.data['domains']:
    #   Domain.objects.create(task=task, domain_name=d)
    return self.create(request, *args, **kwargs)
  
  def get(self, request):
    authHeader = request.headers['Authorization']
    # user id from token
    token = Token.objects.get(key=authHeader)
    user = User.objects.get(user_name = token.user)
    tasks = Task.objects.filter(user=user)
    serializer = self.get_serializer(tasks, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

class DomainViewSet(generics.ListCreateAPIView):
  serializer_class = DomainSerializer
  queryset= Domain.objects.all()

  def post(self, request, *args, **kwargs):
    return self.create(request, *args, **kwargs)
  
  def get(self, request, pk):
    # task = Task.objects.get(id=pk)
    domains = Domain.objects.filter(task=pk)
    serializer = self.get_serializer(domains, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

class TaskDetailViewSet(generics.RetrieveUpdateDestroyAPIView):
  serializer_class = DomainSerializer
  queryset= Domain.objects.all()

  def retrieve(self, request, pk):
    domains = Domain.objects.filter(task=pk)

    task_detail = {
      "contact_pages": len(domains.exclude(contact_page=None)),
      "contact_forms": len(domains.filter(contact_form=True)),
      "forms_sent": len(domains.filter(form_sent=True)),
      "went_manually": len(domains.filter(went_over_manually=True)),
      "sent_manually": len(domains.filter(sent_manually=True)),
      "domains": len(domains)
    }
    # serializer = self.get_serializer(task_detail, many=True)

    return Response(task_detail, status=status.HTTP_200_OK)