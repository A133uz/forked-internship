from django.urls import path
from . import views
from lesta_api import views as api_views

urlpatterns = [
    path('', views.upload_and_show, name='upload_html'),
    path('api/upload/', api_views.UploadFileAPIView.as_view(), name='upload_api'),
]