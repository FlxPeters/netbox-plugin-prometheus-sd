from ipam.models import IPAddress
from virtualization.models import VirtualMachine
from dcim.models.devices import Device

# The base ViewSet has been renamed, this try-except helps to support
# Both < 3.2 and the newer 3.2+ Versions:
# https://github.com/netbox-community/netbox/commit/bbdeae0ed9bcc06fb96ffa2970272e1a3447448c
try:
    from netbox.api.viewsets import NetBoxModelViewSet
except ImportError:
    from extras.api.views import CustomFieldModelViewSet as NetBoxModelViewSet

# Filtersets have been renamed, we support both
# https://github.com/netbox-community/netbox/commit/1024782b9e0abb48f6da65f8248741227d53dbed#diff-d9224204dab475bbe888868c02235b8ef10f07c9201c45c90804d395dc161c40
# pylint: disable=ungrouped-imports
try:
    from ipam.filtersets import IPAddressFilterSet
    from dcim.filtersets import DeviceFilterSet
    from virtualization.filtersets import VirtualMachineFilterSet
except ImportError:
    from ipam.filters import IPAddressFilterSet
    from dcim.filters import DeviceFilterSet
    from virtualization.filters import VirtualMachineFilterSet
# pylint: enable=ungrouped-imports


from .serializers import (
    PrometheusIPAddressSerializer,
    PrometheusDeviceSerializer,
    PrometheusVirtualMachineSerializer,
)


class VirtualMachineViewSet(
    NetBoxModelViewSet
):  # pylint: disable=too-many-ancestors
    queryset = VirtualMachine.objects.prefetch_related(
        "cluster__site",
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


class DeviceViewSet(NetBoxModelViewSet):  # pylint: disable=too-many-ancestors
    queryset = Device.objects.prefetch_related(
        "device_type__manufacturer",
        "device_role",
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


class IPAddressViewSet(NetBoxModelViewSet):  # pylint: disable=too-many-ancestors
    queryset = IPAddress.objects.prefetch_related("tenant", "tags")
    serializer_class = PrometheusIPAddressSerializer
    filterset_class = IPAddressFilterSet
    pagination_class = None
