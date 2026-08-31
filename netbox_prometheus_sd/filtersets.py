from django.db.models import Q
from django.utils.translation import gettext as _

from utilities.filters import (
    MultiValueCharFilter,
    MultiValueNumberFilter,
    NumericArrayFilter,
)

from ipam.filtersets import ServiceFilterSet as NetboxServiceFilterSet


class ServiceFilterSet(NetboxServiceFilterSet):
    """Filter set to support tenancy and site filtering over the device/VM foreign key.

    Tenancy in Netbox is very inconsistent and the relationship on its own is defined across many different models. This
    means that supporting all layers is nearly impossible without a stronger upstream support. For this reason only the
    "first level" tenancy is supported by the tenant filter set.
    """

    tenant_id = MultiValueNumberFilter(
        method="filter_by_tenant_id",
        label=_("Tenant (ID)"),
    )

    tenant = MultiValueCharFilter(
        method="filter_by_tenant_slug",
        label=_("Tenant (slug)"),
    )

    site_id = MultiValueNumberFilter(
        method="filter_by_site_id",
        label=_("Site (ID)"),
    )

    site = MultiValueCharFilter(
        method="filter_by_site_slug",
        label=_("Site (slug)"),
    )

    # fix to make the test_missing_filters pass
    # see: https://github.com/netbox-community/netbox/blob/master/netbox/utilities/testing/filtersets.py#L98
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

    def filter_by_site_id(self, queryset, name, value):
        return queryset.filter(
            Q(device__site_id__in=value) | Q(virtual_machine__site_id__in=value)
        )

    def filter_by_site_slug(self, queryset, name, value):
        return queryset.filter(
            Q(device__site__slug__in=value)
            | Q(virtual_machine__site__slug__in=value)
        )
