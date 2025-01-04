from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import UserViewSet, login, logout

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')

auth_patterns = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
]

urlpatterns = [
    path('auth/token/', include(auth_patterns)),
    path('', include(router_v1.urls)),
]
