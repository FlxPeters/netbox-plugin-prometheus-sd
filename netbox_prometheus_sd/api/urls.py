from rest_framework import routers
from .views import PrometheusDeviceViewSet, GnmicDeviceViewSet

router = routers.DefaultRouter()
router.register("devices", PrometheusDeviceViewSet)
router.register("gnmic-devices", GnmicDeviceViewSet)

urlpatterns = router.urls
