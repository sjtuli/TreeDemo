"""TreeDemo URL Configuration

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
from . import views
from django.conf.urls import include

urlpatterns = [
    path('', views.tree),
    path('create/', views.create, name='create-tree-url'),
    path('delete/', views.delete, name='delete-tree-url'),
    path('mdeditor_upload_img/', views.upload_img, name='upload_img'),
    path('node/<department_id>/', views.node_detail,name='node'),
    path('node/<int:department_id>/modify/', views.modify_post, name='modify'),
    path('node/<int:department_id>/modify/uploadFile/', views.upload_file, name='uploadFile'),
    path('node/<int:department_id>/modify/deleteFile/<int:pk>', views.delete_file, name='delete_file'),
    path('node/<int:department_id>/download_file/<int:pk>/',views.download_file,name='download_file'),

]
