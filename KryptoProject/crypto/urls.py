from django.urls import path
from rest_framework.authtoken import views as rest_framework_views
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('api-token-auth/', rest_framework_views.obtain_auth_token),
    path('index/', views.crypto, name='login')
]
