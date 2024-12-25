from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import UserViewSet, login, logout

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/login/', login, name='login'),
    path('api/auth/token/logout/', logout, name='logout'),
    path('api/', include(router_v1.urls)),
]
