from rest_framework import serializers
from tasks.models import Task, Domain

class TaskSerializer(serializers.ModelSerializer):
  class Meta:
    model = Task
    fields = ['id', 'user', 'task_name', 'first_name', 'last_name', 'email', 'subject', 'phone_number', 
              'company', 'department', 'address']
  
  def create(self, validated_data):
    task = Task.objects.create(**validated_data)
    for d in self.context['request'].data['domains']:
      Domain.objects.create(task=task, domain_name=d)
    return task

class DomainSerializer(serializers.ModelSerializer):
  class Meta:
    model = Domain
    fields = ['task', 'domain_name', 'reached_at', 'status', 'contact_page', 'emails_found', 
              'contact_form', 'form_sent', 'went_over_manually', 'sent_manually']

