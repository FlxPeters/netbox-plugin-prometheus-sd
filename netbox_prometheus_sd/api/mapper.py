from netbox_prometheus_sd.api.models import Target, TargetType

from ipam.models import IPAddress
from virtualization.models import (
    VirtualMachine,
    Device,
)
from netaddr import IPNetwork


def vm_to_target(vm: VirtualMachine):
    """ Map a Netbox VirtualMachine to a Prometheus target """
    target = Target(vm.name)
    target.add_label("type", TargetType.VIRTUAL_MACHINE.value)
    target.add_label("status", vm.status)
    extract_tenant(vm, target)

    if hasattr(vm, "primary_ip") and vm.primary_ip is not None:
        target.add_label("ip", str(IPNetwork(vm.primary_ip.address).ip))

    if hasattr(vm, "cluster") and vm.cluster is not None:
        target.add_label("cluster", vm.cluster.name)
        if vm.cluster.group:
            target.add_label("cluster_group", vm.cluster.group.name)
        if vm.cluster.type:
            target.add_label("cluster_type", vm.cluster.type.name)
        if vm.cluster.site:
            target.add_label("site", vm.cluster.site.name)
            target.add_label("site_slug", vm.cluster.site.slug)

    if hasattr(vm, "role") and vm.role is not None:
        target.add_label("role", vm.role.name)
        target.add_label("role_slug", vm.role.slug)

    if hasattr(vm, "platform") and vm.platform is not None:
        target.add_label("platform", vm.platform.name)
        target.add_label("platform_slug", vm.platform.slug)

    # todo: Add more fields
    # device_type
    # services
    # tags?

    return target


def device_to_target(device: Device):
    """ Map a Netbox VirtualMachine to a Prometheus target """
    target = Target(device.name)
    target.add_label("type", TargetType.DEVICE.value)
    target.add_label("status", device.status)
    extract_tenant(device, target)

    if hasattr(device, "primary_ip") and device.primary_ip is not None:
        target.add_label("ip", str(IPNetwork(device.primary_ip.address).ip))

    if hasattr(device, "device_role") and device.device_role is not None:
        target.add_label("role", device.device_role.name)
        target.add_label("role_slug", device.device_role.slug)

    if hasattr(device, "device_type") and device.device_type is not None:
        target.add_label("device_type", device.device_type.model)
        target.add_label("device_type_slug", device.device_type.slug)

    if hasattr(device, "platform") and device.platform is not None:
        target.add_label("platform", device.platform.name)
        target.add_label("platform_slug", device.platform.slug)

    if hasattr(device, "site") and device.site is not None:
        target.add_label("site", device.site.name)
        target.add_label("site_slug", device.site.slug)

    # todo: Add more fields
    # services
    # tags

    return target


def ip_to_target(ip: IPAddress):
    """ Map a Netbox IPAddress to a Prometheus target """

    # Use dns name if set, otherwise IP without netmask
    addr = str(IPNetwork(ip.address).ip)
    if ip.dns_name:
        target = Target(ip.dns_name)
    else:
        target = Target(addr)

    target.add_label("status", ip.status)
    target.add_label("type", TargetType.IP_ADDRESS.value)
    target.add_label("ip", addr)
    extract_tenant(ip, target)

    return target


def extract_tenant(obj, target: Target):
    if hasattr(obj, "tenant") and obj.tenant:
        target.add_label("tenant", obj.tenant.name)
        target.add_label("tenant_slug", obj.tenant.slug)

        if obj.tenant.group:
            target.add_label("tenant_group", obj.tenant.group.name)
            target.add_label("tenant_group_slug", obj.tenant.group.slug)
