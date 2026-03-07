from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WBSItemViewSet

router = DefaultRouter()
router.register(r'wbs', WBSItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
