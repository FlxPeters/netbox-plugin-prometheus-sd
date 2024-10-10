from rest_framework import routers
from .views import (
    VirtualMachineViewSet,
    DeviceViewSet,
    IPAddressViewSet,
    ServiceViewSet,
)

router = routers.DefaultRouter()
router.register("services", ServiceViewSet)
router.register("virtual-machines", VirtualMachineViewSet)
router.register("devices", DeviceViewSet)
router.register("ip-addresses", IPAddressViewSet)

urlpatterns = router.urls
