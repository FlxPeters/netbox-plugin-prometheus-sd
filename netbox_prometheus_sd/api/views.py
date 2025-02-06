from ipam.models import IPAddress, Service
from virtualization.models import VirtualMachine
from dcim.models.devices import Device


try:  # Netbox >= 3.5
    from netbox.api.viewsets import BaseViewSet
    from netbox.api.viewsets.mixins import CustomFieldsMixin
    from rest_framework.mixins import ListModelMixin

    # Netbox MosdelViewSet with list only
    class NetboxPrometheusSDModelViewSet(
        CustomFieldsMixin, ListModelMixin, BaseViewSet
    ):
        pass

except ImportError:
    try:  # 3.2 >= Netbox < 3.5
        from netbox.api.viewsets import (
            NetBoxModelViewSet as NetboxPrometheusSDModelViewSet,
        )
    except ImportError:  # Netbox < 3.2
        from extras.api.views import (
            CustomFieldModelViewSet as NetboxPrometheusSDModelViewSet,
        )

# Filtersets have been renamed, we support both
# https://github.com/netbox-community/netbox/commit/1024782b9e0abb48f6da65f8248741227d53dbed#diff-d9224204dab475bbe888868c02235b8ef10f07c9201c45c90804d395dc161c40
try:
    from ipam.filtersets import IPAddressFilterSet
    from dcim.filtersets import DeviceFilterSet
    from virtualization.filtersets import VirtualMachineFilterSet
except ImportError:
    from ipam.filters import IPAddressFilterSet
    from dcim.filters import DeviceFilterSet
    from virtualization.filters import VirtualMachineFilterSet


from ..filtersets import ServiceFilterSet
from .serializers import (
    PrometheusIPAddressSerializer,
    PrometheusDeviceSerializer,
    PrometheusVirtualMachineSerializer,
    PrometheusServiceSerializer,
)


class ServiceViewSet(NetboxPrometheusSDModelViewSet):
    queryset = Service.objects.prefetch_related(
        "device",
        "virtual_machine",
        "ipaddresses",
        "tags",
    )
    filterset_class = ServiceFilterSet
    serializer_class = PrometheusServiceSerializer
    pagination_class = None


class VirtualMachineViewSet(NetboxPrometheusSDModelViewSet):
    queryset = VirtualMachine.objects.prefetch_related(
        "cluster__scope",
        "role",
        "tenant",
        "platform",
        "primary_ip4",
        "primary_ip6",
        "tags",
        "services",
        "contacts",
    )
    filterset_class = VirtualMachineFilterSet
    serializer_class = PrometheusVirtualMachineSerializer
    pagination_class = None


class DeviceViewSet(NetboxPrometheusSDModelViewSet):
    queryset = Device.objects.prefetch_related(
        "device_type__manufacturer",
        "role" if hasattr(Device, "role") else "device_role",
        "tenant",
        "platform",
        "site",
        "location",
        "rack",
        "parent_bay",
        "virtual_chassis__master",
        "primary_ip4__nat_outside",
        "primary_ip6__nat_outside",
        "tags",
    )
    filterset_class = DeviceFilterSet
    serializer_class = PrometheusDeviceSerializer
    pagination_class = None


class IPAddressViewSet(NetboxPrometheusSDModelViewSet):
    queryset = IPAddress.objects.prefetch_related("tenant", "tags")
    serializer_class = PrometheusIPAddressSerializer
    filterset_class = IPAddressFilterSet
    pagination_class = None
