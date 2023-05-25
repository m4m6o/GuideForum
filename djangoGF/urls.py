"""
URL configuration for djangoGF project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf.urls.static import static, serve
from django.conf import settings
import users
from GuideForum import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('', views.index, name='homepage'),
    path('topics/', views.topics, name='topics'),
    path('my_topics/', views.my_topics, name='my_topics'),
    path('topics/<int:topic_id>/', views.topic, name='topic'),
    path('topic/<int:topic_id>/like/', views.like_topic, name='like_topic'),
    path("select2/", include("django_select2.urls")),
    path('new_topic/', views.new_topic, name='new_topic'),
    path('new_entry/<int:topic_id>/', views.new_entry, name='new_entry'),
    path('edit_entry/<int:entry_id>/', views.edit_entry, name='edit_entry'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT, view=serve)
