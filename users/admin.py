from django.contrib import admin

from users.models import User
# Register your models here.

class SettingUser(admin.ModelAdmin):
  list_display = ('id', 'email', 'first_name', 'last_name')

admin.site.register(User, SettingUser)