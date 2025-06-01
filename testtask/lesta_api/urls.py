from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.UploadFileAPIView.as_view(), name='upload_api'),
    path('version/', views.display_version),
]
