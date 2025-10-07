from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, BugViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'bugs', BugViewSet, basename='bug')

urlpatterns = [
    path('', include(router.urls)),
]
