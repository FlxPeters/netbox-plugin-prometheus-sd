from rest_framework import routers
from .views import DeviceViewSet

router = routers.DefaultRouter()
router.register("devices", DeviceViewSet)

urlpatterns = router.urls
