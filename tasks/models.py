from django.db import models
# from django.contrib.auth.models import User
from users.models import User

# Create your models here.
class Task(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  task_name = models.CharField("Name", max_length=30)
  first_name = models.CharField("First Name", max_length=30)
  last_name = models.CharField("Last Name", max_length=30)
  email = models.CharField("Email", max_length=100)
  subject = models.CharField("Subject", max_length=100)
  phone_number = models.IntegerField('Phone Number', blank=True, default=0)
  company = models.CharField("Company", max_length=50)
  department = models.CharField("Department", max_length=50)
  address = models.CharField("Address", max_length=100)
  status = models.CharField("Status", max_length=30, default='In progress')
  finished_date = models.DateTimeField("Reached at", null=True)

  def __str__(self):
    return str(self.id)

class Preset(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  preset_name = models.CharField("Name", max_length=30)
  first_name = models.CharField("First Name", max_length=30)
  last_name = models.CharField("Last Name", max_length=30)
  email = models.CharField("Email", max_length=100)
  subject = models.CharField("Subject", max_length=100)
  phone_number = models.IntegerField('Phone Number', blank=True, default=0)
  company = models.CharField("Company", max_length=50)
  department = models.CharField("Department", max_length=50)
  address = models.CharField("Address", max_length=100)

  def __str__(self):
    return str(self.id)

class Domain(models.Model):
  task = models.ForeignKey(Task, on_delete=models.CASCADE)
  domain_name = models.CharField("Domain Name", max_length=100)
  reached_at = models.DateTimeField("Reached at", auto_now=True, null=True)
  status = models.CharField("Status", max_length=30, default='Pending')
  contact_page = models.CharField("Contact Page", max_length=150, default='', null=True)
  contact_form = models.BooleanField("Contact Form", default=False, null=True)
  form_sent = models.BooleanField("Form Sent", default=False, null=True)
  went_over_manually = models.BooleanField("Went Over Manually", default=False, null=True)
  sent_manually = models.BooleanField("Sent Manually", default=False, null=True)
  emails_found = models.IntegerField('Emails Found', blank=True, default=0, null=True)

  def __str__(self):
    return self.domain_name


  