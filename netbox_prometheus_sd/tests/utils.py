from dcim.models.devices import DeviceType, Manufacturer
from dcim.models.sites import Site
from dcim.models import Device, DeviceRole, Platform

from ipam.models import IPAddress
from tenancy.models import Tenant, TenantGroup

from virtualization.models import (
    Cluster,
    ClusterGroup,
    ClusterType,
    VirtualMachine,
)


def build_cluster():

    return Cluster.objects.create(
        name="DC1",
        group=ClusterGroup.objects.create(name="VMware"),
        type=ClusterType.objects.create(name="On Prem"),
        site=Site.objects.create(name="Campus A", slug="campus-a"),
    )


def build_tenant():
    return Tenant.objects.create(name="Acme Corp.", slug="acme")


def build_device_role():
    return DeviceRole.objects.create(name="Core Switch", slug="core-switch")


def build_minimal_vm():
    return VirtualMachine.objects.create(
        name="vm-01.example.com", cluster=build_cluster()
    )


def build_vm_full():
    vm = VirtualMachine.objects.create(
        name="vm-full-01.example.com",
        cluster=build_cluster(),
        tenant=build_tenant(),
        role=DeviceRole.objects.create(name="VM", slug="vm", vm_role=True),
        platform=Platform.objects.create(name="Ubuntu 20.04", slug="ubuntu-20.04"),
        primary_ip4=IPAddress.objects.create(address="192.168.0.1/24"),
    )
    vm.tags.add("Tag1")
    vm.tags.add("Tag 2")
    return vm


def build_minimal_device():
    return Device.objects.create(
        name="core-switch-01",
        device_role=build_device_role(),
        device_type=DeviceType.objects.create(
            model="Firewall Device",
            slug="firewall",
            manufacturer=Manufacturer.objects.create(name="Cisco", slug="cisco"),
        ),
        site=Site.objects.create(name="Site Device", slug="site-device"),
    )


def build_device_full():
    device = Device.objects.create(
        name="core-switch-full-01",
        tenant=build_tenant(),
        device_role=build_device_role(),
        platform=Platform.objects.create(name="Junos", slug="junos"),
        site=Site.objects.create(name="Campus B", slug="campus-b"),
        device_type=DeviceType.objects.create(
            model="SRX",
            slug="srx",
            manufacturer=Manufacturer.objects.create(name="Juniper", slug="juniper"),
        ),
        primary_ip6=IPAddress.objects.create(address="2001:db8:1701::2/64"),
    )
    device.tags.add("Tag1")
    device.tags.add("Tag 2")
    return device


def build_minimal_ip():
    return IPAddress.objects.create(address="10.10.10.10/24")


def build_full_ip():
    ip = IPAddress.objects.create(
        address="10.10.10.10/24",
        tenant=Tenant.objects.create(
            name="Starfleet",
            slug="starfleet",
            group=TenantGroup.objects.create(name="Federation", slug="federation"),
        ),
        dns_name="foo.example.com",
    )
    ip.tags.add("Tag1")
    ip.tags.add("Tag 2")
    return ip
