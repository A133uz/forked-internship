from django.urls import path
from . import views
from lesta_api import views as api_views

urlpatterns = [
    path('', views.upload_and_show, name='upload_html'),
]