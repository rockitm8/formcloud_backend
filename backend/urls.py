"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from rest_framework.authtoken import views
from rest_framework import routers

from users.views import UserLoginViewSet, UserRegisterationViewSet
from tasks.views import DomainViewSet, TaskDetailViewSet, TaskViewSet

router = routers.DefaultRouter()
router.register('', UserRegisterationViewSet, basename='user_register')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    # path('api/users/login/', views.obtain_auth_token),
    path('api/users/login/', UserLoginViewSet.as_view()),
    path('api/users/register/', include(router.urls)),
    path("api/tasks/", TaskViewSet.as_view()),
    path("api/domains/<int:pk>/", DomainViewSet.as_view()),
    path("api/taskdetail/<int:pk>/", TaskDetailViewSet.as_view())
]
