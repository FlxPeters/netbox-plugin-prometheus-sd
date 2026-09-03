from django.db.models import Q
from django.utils.translation import gettext as _

from utilities.filters import (
    MultiValueCharFilter,
    MultiValueNumberFilter,
    NumericArrayFilter,
)

from ipam.filtersets import ServiceFilterSet as NetboxServiceFilterSet
from ipam.models import Service

# Netbox 4.7 replaced the Service.ports ArrayField with `port_mappings`, and
# its filterset metaclass rejects a filter on a field that no longer exists.
SERVICE_HAS_PORTS_FIELD = any(f.name == "ports" for f in Service._meta.get_fields())


class ServiceFilterSet(NetboxServiceFilterSet):
    """Filter set to support tenancy over the device/VM foreign key.

    Tenancy in Netbox is very incosistent and the relationship on its own is defined across many different models. This
    means that supporting all layers is nearly impossible without a stronger upstream support. For this reason only the
    "first level" tenancy is supported by this filter set.
    """

    tenant_id = MultiValueNumberFilter(
        method="filter_by_tenant_id",
        label=_("Tenant (ID)"),
    )

    tenant = MultiValueCharFilter(
        method="filter_by_tenant_slug",
        label=_("Tenant (slug)"),
    )

    # Netbox < 4.7 only exposes the ports array as `port`, but Netbox's
    # test_missing_filters wants a filter named after the model field.
    # see: https://github.com/netbox-community/netbox/blob/master/netbox/utilities/testing/filtersets.py#L98
    if SERVICE_HAS_PORTS_FIELD:
        ports = NumericArrayFilter(field_name="ports", lookup_expr="contains")

    def filter_by_cluster_tenant_id(self, queryset, name, value):
        return queryset.filter(
            Q(device__cluster__tenant_id__in=value)
            | Q(virtual_machine__cluster__tenant_id__in=value)
        )

    def filter_by_cluster_tenant_slug(self, queryset, name, value):
        return queryset.filter(
            Q(device__cluster__tenant__slug__in=value)
            | Q(virtual_machine__cluster__tenant__slug__in=value)
        )

    def filter_by_tenant_id(self, queryset, name, value):
        return queryset.filter(
            Q(device__tenant_id__in=value) | Q(virtual_machine__tenant_id__in=value)
        )

    def filter_by_tenant_slug(self, queryset, name, value):
        return queryset.filter(
            Q(device__tenant__slug__in=value)
            | Q(virtual_machine__tenant__slug__in=value)
        )
