from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.interfaces.api.views import UserViewSet, GroupViewSet, ProfileViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'profiles', ProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
