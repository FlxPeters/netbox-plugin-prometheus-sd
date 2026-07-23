from django.contrib.contenttypes.prefetch import GenericPrefetch

from ipam.models import IPAddress, Service
from virtualization.models import VirtualMachine
from dcim.models.devices import Device

from netbox.api.viewsets import BaseViewSet
from netbox.api.viewsets.mixins import CustomFieldsMixin
from rest_framework.mixins import ListModelMixin

from .utils import NETBOX_RELEASE_CURRENT, NETBOX_RELEASE_41

from ipam.filtersets import IPAddressFilterSet
from dcim.filtersets import DeviceFilterSet
from virtualization.filtersets import VirtualMachineFilterSet

from ..filtersets import ServiceFilterSet
from .serializers import (
    PrometheusIPAddressSerializer,
    PrometheusDeviceSerializer,
    PrometheusVirtualMachineSerializer,
    PrometheusServiceSerializer,
)


# Netbox MosdelViewSet with list only
class NetboxPrometheusSDModelViewSet(CustomFieldsMixin, ListModelMixin, BaseViewSet):
    pass


# Netbox 4.2 replaced the direct Cluster.site FK with a generic `scope` relation.
# It stays in prefetch_related either way: a GenericForeignKey cannot be JOINed
# via select_related.
if NETBOX_RELEASE_CURRENT > NETBOX_RELEASE_41:
    CLUSTER_SCOPE = "cluster__scope"
else:
    CLUSTER_SCOPE = "cluster__site"

# Netbox 4.3 replaced Service.device/Service.virtual_machine with a single
# generic `parent` relation, exposed via parent_object_type/parent_object_id.
# Note: hasattr(Service, "device") is NOT a usable check — Device and
# VirtualMachine declare `services = GenericRelation(..., related_query_name=...)`,
# which makes Service.device resolve to a read-only reverse accessor on every
# Netbox version, including 4.3+.
SERVICE_HAS_GENERIC_PARENT = hasattr(Service, "parent_object_type")

# Relations read off `obj.cluster` by utils.extract_cluster(), and off
# `obj.contacts` by utils.extract_contacts(). Shared by the device and VM
# querysets, which run the same extractors.
CLUSTER_RELATED = ("cluster", "cluster__group", "cluster__type")
CONTACTS_RELATED = ("contacts__contact", "contacts__role")


class ServiceViewSet(NetboxPrometheusSDModelViewSet):
    # utils.extract_parent() walks the service's parent device/VM and pulls its
    # name, IPs, tenant, cluster and contacts, so the parent's own relations have
    # to be fetched too or every service row re-queries them.
    _parent_related = (
        "tenant__group",
        "primary_ip4",
        "primary_ip6",
        "site",
        *CLUSTER_RELATED,
        CLUSTER_SCOPE,
        *CONTACTS_RELATED,
    )

    if SERVICE_HAS_GENERIC_PARENT:  # Netbox >= 4.3
        queryset = Service.objects.prefetch_related(
            GenericPrefetch(
                "parent",
                [
                    Device.objects.prefetch_related(*_parent_related, "oob_ip"),
                    VirtualMachine.objects.prefetch_related(*_parent_related),
                ],
            ),
            "ipaddresses",
            "tags",
        )
    else:  # Netbox < 4.3
        queryset = Service.objects.prefetch_related(
            *(f"device__{rel}" for rel in _parent_related),
            "device__oob_ip",
            *(f"virtual_machine__{rel}" for rel in _parent_related),
            "device",
            "virtual_machine",
            "ipaddresses",
            "tags",
        )
    filterset_class = ServiceFilterSet
    serializer_class = PrometheusServiceSerializer
    pagination_class = None


class VirtualMachineViewSet(NetboxPrometheusSDModelViewSet):
    queryset = (
        VirtualMachine.objects.select_related(
            "role",
            "tenant__group",
            "platform",
            "primary_ip4",
            "primary_ip6",
            # utils.extract_cluster() falls through to obj.site for anything that
            # has one, and VMs do on every supported Netbox release.
            "site",
        )
        .prefetch_related(
            CLUSTER_SCOPE,
            *CLUSTER_RELATED,
            *CONTACTS_RELATED,
            "tags",
            "services",
        )
        .annotate_config_context_data()
    )
    filterset_class = VirtualMachineFilterSet
    serializer_class = PrometheusVirtualMachineSerializer
    pagination_class = None


class DeviceViewSet(NetboxPrometheusSDModelViewSet):
    queryset = (
        Device.objects.select_related(
            "device_type",
            "role",
            "tenant__group",
            "platform",
            "site",
            "location",
            "rack",
            "primary_ip4",
            "primary_ip6",
            "oob_ip",
        )
        .prefetch_related(
            CLUSTER_SCOPE,
            *CLUSTER_RELATED,
            *CONTACTS_RELATED,
            "tags",
            "services",
        )
        .annotate_config_context_data()
    )
    filterset_class = DeviceFilterSet
    serializer_class = PrometheusDeviceSerializer
    pagination_class = None


class IPAddressViewSet(NetboxPrometheusSDModelViewSet):
    queryset = IPAddress.objects.select_related("tenant__group").prefetch_related("tags")
    serializer_class = PrometheusIPAddressSerializer
    filterset_class = IPAddressFilterSet
    pagination_class = None
