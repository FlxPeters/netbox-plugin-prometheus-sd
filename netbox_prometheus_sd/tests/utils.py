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
    return Cluster.objects.get_or_create(
        name="DC1",
        group=ClusterGroup.objects.get_or_create(name="VMware")[0],
        type=ClusterType.objects.get_or_create(name="On Prem")[0],
        site=Site.objects.get_or_create(name="Campus A", slug="campus-a")[0],
    )[0]


def build_tenant():
    return Tenant.objects.get_or_create(name="Acme Corp.", slug="acme")[0]


def build_minimal_vm(name):
    return VirtualMachine.objects.get_or_create(name=name, cluster=build_cluster())[0]


def build_vm_full(name):
    vm = build_minimal_vm(name=name)
    vm.tenant = build_tenant()
    vm.role = DeviceRole.objects.get_or_create(name="VM", slug="vm", vm_role=True)[0]
    vm.platform = Platform.objects.get_or_create(
        name="Ubuntu 20.04", slug="ubuntu-20.04"
    )[0]
    vm.primary_ip4 = IPAddress.objects.get_or_create(address="192.168.0.1/24")[0]
    vm.primary_ip6 = IPAddress.objects.get_or_create(address="2001:db8:1701::2/64")[0]

    vm.tags.add("Tag1")
    vm.tags.add("Tag 2")
    return vm


def build_minimal_device(name):
    return Device.objects.get_or_create(
        name=name,
        device_role=DeviceRole.objects.get_or_create(name="Firewall", slug="firewall")[
            0
        ],
        device_type=DeviceType.objects.get_or_create(
            model="SRX",
            slug="srx",
            manufacturer=Manufacturer.objects.get_or_create(
                name="Juniper", slug="juniper"
            )[0],
        )[0],
        site=Site.objects.get_or_create(name="Site", slug="site")[0],
    )[0]


def build_device_full(name):
    device = build_minimal_device(name)
    device.tenant = build_tenant()
    device.platform = Platform.objects.get_or_create(name="Junos", slug="junos")[0]
    device.primary_ip4 = IPAddress.objects.get_or_create(address="192.168.0.1/24")[0]
    device.primary_ip6 = IPAddress.objects.get_or_create(address="2001:db8:1701::2/64")[
        0
    ]
    device.tags.add("Tag1")
    device.tags.add("Tag 2")
    return device


def build_minimal_ip(address):
    return IPAddress.objects.get_or_create(address=address)[0]


def build_full_ip(address, dns_name=""):
    ip = build_minimal_ip(address=address)
    ip.tenant = Tenant.objects.get_or_create(
        name="Starfleet",
        slug="starfleet",
        group=TenantGroup.objects.get_or_create(name="Federation", slug="federation")[
            0
        ],
    )[0]
    ip.dns_name = dns_name
    ip.tags.add("Tag1")
    ip.tags.add("Tag 2")
    return ip
