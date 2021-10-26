from rest_framework.response import Response
from ipam.models import IPAddress
from virtualization.models import VirtualMachine
from dcim.models.devices import Device

from .serializers import (
    PrometheusIPAddressSerializer,
    PrometheusDeviceSerializer,
    PrometheusVirtualMachineSerializer,
)

from extras.api.views import CustomFieldModelViewSet
from virtualization import filtersets as vm_filtersets
from dcim import filtersets as dcim_filtersets
from ipam import filtersets as ipam_filtersets


class VirtualMachineViewSet(CustomFieldModelViewSet):
    queryset = VirtualMachine.objects.prefetch_related(
        "cluster__site",
        "role",
        "tenant",
        "platform",
        "primary_ip4",
        "primary_ip6",
        "tags",
        "services",
    )
    filterset_class = vm_filtersets.VirtualMachineFilterSet
    serializer_class = PrometheusVirtualMachineSerializer

    def get_paginated_response(self, data):
        """ Return as plain result without paging """
        return Response(data)


class DeviceViewSet(CustomFieldModelViewSet):
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
    filterset_class = dcim_filtersets.DeviceFilterSet
    serializer_class = PrometheusDeviceSerializer

    def get_paginated_response(self, data):
        """ Return as plain result without paging """
        return Response(data)


class IPAddressViewSet(CustomFieldModelViewSet):
    queryset = IPAddress.objects.prefetch_related("tenant", "tags")
    serializer_class = PrometheusIPAddressSerializer
    filterset_class = ipam_filtersets.IPAddressFilterSet

    def get_paginated_response(self, data):
        """ Return as plain result without paging """
        return Response(data)
