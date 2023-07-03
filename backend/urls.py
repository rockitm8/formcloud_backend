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
from django.urls import path, re_path
from django.conf.urls import include
from rest_framework import routers
from tasks import views


from users.views import UserLoginViewSet, UserRegisterationViewSet, activate
from tasks.views import DomainViewSet, PresetViewSet, TaskDetailViewSet, TaskViewSet
from django.views.generic import TemplateView
router = routers.DefaultRouter()
router.register('', UserRegisterationViewSet, basename='user_register')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    # path('api/users/login/', views.obtain_auth_token),
    path('api/users/login/', UserLoginViewSet.as_view()),
    path('api/users/register/', include(router.urls)),
    path("api/tasks/", TaskViewSet.as_view()),
    path("api/presets/", PresetViewSet.as_view()),
    path("api/domains/<int:pk>/", DomainViewSet.as_view()),
    path("api/taskdetail/<int:pk>/", TaskDetailViewSet.as_view()),
    path('api/deletetask/<int:id>', views.deletetask, name='delete'),
    path('api/activate/<uidb64>/<token>/', activate, name='activate'),
    #re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
    path('', views.index, name='index'),
]
