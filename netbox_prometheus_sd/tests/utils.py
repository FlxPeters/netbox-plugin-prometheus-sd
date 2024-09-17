from dcim.models.devices import DeviceType, Manufacturer
from dcim.models.sites import Site, Location
from dcim.models import Device, DeviceRole, Platform, Rack
from extras.models import ConfigContext, Tag

from ipam.models import IPAddress, Service
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


def build_location():
    return Location.objects.get_or_create(
        name="First Floor", slug="first-floor",
        site=Site.objects.get_or_create(name="Site", slug="site")[0]
    )[0]


def build_tenant():
    return Tenant.objects.get_or_create(name="Acme Corp.", slug="acme")[0]


def build_custom_fields():
    """Build custom field definition with different kinds of custom values"""
    return {
        "contact": [
            {
                "id": 1,
                "url": "http://localhost:8000/api/tenancy/contacts/1/",
                "display": "Foo",
                "name": "Foo"
            }
        ],
        "json": {
            "foo": [
                "bar",
                "baz"
            ]
        },
        "multi_selection": [
            "foo",
            "baz"
        ],
        "simple": "Foobar 123",
        "int": "42",
        "text_long": "This is\r\na  pretty\r\nlog\r\nText",
        "bool": "True"
    }

def build_minimal_vm(name):
    return VirtualMachine.objects.get_or_create(name=name, cluster=build_cluster())[0]


def build_vm_full(name, ip_octet=1):
    # Create the confix context beforehand
    config_context, created = ConfigContext.objects.get_or_create(name="context 1",
        weight=100, data={"prometheus-plugin-prometheus-sd": [
            {"metrics_path": "/not/metrics", "port": 4242, "scheme": "https"},
            {"port": 4243},
        ]
    })
    if created:
        platform = Platform.objects.get_or_create(
            name="Ubuntu 20.04", slug="ubuntu-20.04"
        )[0]
        config_context.platforms.add(platform)

    vm = build_minimal_vm(name=name)
    vm.platform = Platform.objects.get_or_create(
        name="Ubuntu 20.04", slug="ubuntu-20.04"
    )[0]

    vm.tenant = build_tenant()
    vm.custom_field_data = build_custom_fields()
    vm.role = DeviceRole.objects.get_or_create(name="VM", slug="vm", vm_role=True)[0]
    vm.primary_ip4 = IPAddress.objects.get_or_create(address=f"192.168.0.{ip_octet}/24")[0]
    vm.primary_ip6 = IPAddress.objects.get_or_create(address=f"2001:db8:1701::{ip_octet+1}/64")[0]

    vm.tags.add("Tag1")
    vm.tags.add("Tag 2")
    vm.save()

    Service.objects.create(virtual_machine=vm, name="ssh", protocol='tcp', ports=[22])
    return vm


def build_minimal_device(name):
    role_attr = "role" if hasattr(Device, "role") else "device_role"
    return Device.objects.get_or_create(
        name=name,
        device_type=DeviceType.objects.get_or_create(
            model="SRX",
            slug="srx",
            manufacturer=Manufacturer.objects.get_or_create(
                name="Juniper", slug="juniper"
            )[0],
        )[0],
        site=Site.objects.get_or_create(name="Site", slug="site")[0],
        **{
            role_attr: DeviceRole.objects.get_or_create(name="Firewall", slug="firewall")[0],
        }
    )[0]

def build_device_config_context_no_array(name):
    device = build_minimal_device(name)
    config_context, created = ConfigContext.objects.get_or_create(
        name="context no array", weight=100,
        data={"prometheus-plugin-prometheus-sd": {"port": 4242}},
    )
    if not created:
        tag = Tag.objects.create(name='no array config context', slug='no-array-cc')
        config_context.platforms.add(tag)
        device.tags.add(tag)
    device.save()

    return device

def build_device_config_context_invalid_1(name):
    device = build_minimal_device(name)
    config_context, created = ConfigContext.objects.get_or_create(
        name="invalid 1", weight=100,
        data={"prometheus-plugin-prometheus-sd": "foo"},
    )
    if not created:
        tag = Tag.objects.create(name='invalid 1', slug='invalid-1')
        config_context.platforms.add(tag)
        device.tags.add(tag)
    device.save()

    return device

def build_device_config_context_invalid_2(name):
    device = build_minimal_device(name)
    config_context, created = ConfigContext.objects.get_or_create(
        name="invalid 2", weight=100,
        data={"prometheus-plugin-prometheus-sd": [{"not": "", "standard": ""}]},
    )
    if not created:
        tag = Tag.objects.create(name='invalid 2', slug='invalid-2')
        config_context.platforms.add(tag)
        device.tags.add(tag)
    device.save()

    return device

def build_device_config_context_mix_invalid_valid(name):
    device = build_minimal_device(name)
    config_context, created = ConfigContext.objects.get_or_create(
        name="mix valid invalid", weight=100,
        data={"prometheus-plugin-prometheus-sd": [
            {"not": "", "standard": ""},
            {"port": 4242, "ignored": ""},
        ]},
    )
    if not created:
        tag = Tag.objects.create(name='mix valid invalid', slug='mix-valid-invalid')
        config_context.platforms.add(tag)
        device.tags.add(tag)
    device.save()

    return device

def build_device_full(name, ip_octet=1):
    device = build_minimal_device(name)
    device.location = build_location()
    device.tenant = build_tenant()
    device.description = "Device Description"
    device.custom_field_data = build_custom_fields()
    device.platform = Platform.objects.get_or_create(name="Junos", slug="junos")[0]
    device.primary_ip4 = IPAddress.objects.get_or_create(address=f"192.168.0.{ip_octet}/24")[0]
    device.primary_ip6 = IPAddress.objects.get_or_create(address=f"2001:db8:1701::{ip_octet+1}/64")[0]
    device.oob_ip = IPAddress.objects.get_or_create(address=f"10.0.0.{ip_octet}/24")[0]
    device.rack = Rack.objects.get_or_create(
        name="R01B01", site=Site.objects.get_or_create(name="Site", slug="site")[0]
    )[0]
    device.site = Site.objects.get_or_create(name="Site", slug="site")[0]
    device.tags.add("Tag1")
    device.tags.add("Tag 2")
    device.save()
    device.position = 1.0
    Service.objects.create(device=device, name="ssh", protocol='tcp', ports=[22])
    return device


def build_minimal_ip(address):
    return IPAddress.objects.get_or_create(address=address)[0]


def build_full_ip(address, dns_name=""):
    ip = build_minimal_ip(address=address)
    ip.custom_field_data = build_custom_fields()
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
    ip.save()

    return ip
