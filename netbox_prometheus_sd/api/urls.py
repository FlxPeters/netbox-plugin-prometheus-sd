from rest_framework import routers
from .views import VirtualMachineViewSet, DeviceViewSet, IPAddressViewSet

router = routers.DefaultRouter()
router.register("virtual-machines", VirtualMachineViewSet)
router.register("devices", DeviceViewSet)
router.register("ip-addresses", IPAddressViewSet)

urlpatterns = router.urls
