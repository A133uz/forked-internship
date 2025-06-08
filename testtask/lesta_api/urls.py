from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'documents', views.DocumentViewSet, basename='documents')
router.register(r'collections', views.CollectionViewSet, basename='collections')
router.register(r'user', views.UserViewSet, basename='user')


urlpatterns = [
    path('upload/', views.DocumentUploadAPI.as_view(), name='upload_api'),
    path('version/', views.get_version),
    path('metrics/', views.MetricsAPIView.as_view()),
    path('status/', views.get_status),
    path('', include(router.urls)),
    path('login/', views.LoginView.as_view()),
    path('register/', views.RegisterView.as_view()),
    path('logout/', views.LogoutView.as_view()),
]
