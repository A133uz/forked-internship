from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.UploadFileAPIView.as_view(), name='upload_api'),
    path('version/', views.display_version),
    path('metrics/', views.MetricsAPIView.as_view()),
    path('status/', views.get_status),
]
