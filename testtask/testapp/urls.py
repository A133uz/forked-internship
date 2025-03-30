from django.urls import path
from . import views

urlpatterns = [path('', views.upload_file, name='upload_form'), 
               path('words/', views.upload_file, name='words_list'),
            ]