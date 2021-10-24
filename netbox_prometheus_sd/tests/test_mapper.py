from os import name
import re
from django.test import TestCase
from django.test.utils import tag
from dcim.models.devices import DeviceType, Manufacturer
from dcim.models.sites import Site
from netbox_prometheus_sd.api.models import Target, TargetType

from ..api import mapper

from ipam.models import IPAddress
from dcim.models import Device, DeviceRole, Platform
from tenancy.models import Tenant, TenantGroup

from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine


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
    return VirtualMachine.objects.create(
        name="vm-full-01.example.com",
        cluster=build_cluster(),
        tenant=build_tenant(),
        role=DeviceRole.objects.create(name="VM", slug="vm", vm_role=True),
        platform=Platform.objects.create(name="Ubuntu 20.04", slug="ubuntu-20.04"),
        primary_ip4=IPAddress.objects.create(address="192.168.0.1/24"),
    )


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
    return Device.objects.create(
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


def build_minimal_ip():
    return IPAddress.objects.create(address="10.10.10.10/24")


def build_full_ip():
    return IPAddress.objects.create(
        address="10.10.10.10/24",
        tenant=Tenant.objects.create(
            name="Starfleet",
            slug="starfleet",
            group=TenantGroup.objects.create(name="Federation", slug="federation"),
        ),
        dns_name="foo.example.com",
    )


class MapperTests(TestCase):
    def test_vm_minimal_to_target(self):
        target = mapper.vm_to_target(build_minimal_vm())
        self.assertEquals(target.targets, ["vm-01.example.com"])
        self.assertDictContainsSubset({"__meta_netbox_type": "vm"}, target.labels)
        self.assertDictContainsSubset({"__meta_netbox_status": "active"}, target.labels)

    def test_vm_full_to_target(self):
        target = mapper.vm_to_target(build_vm_full())
        self.assertEquals(target.targets, ["vm-full-01.example.com"])
        self.assertDictContainsSubset({"__meta_netbox_type": "vm"}, target.labels)
        self.assertDictContainsSubset({"__meta_netbox_status": "active"}, target.labels)
        self.assertDictContainsSubset({"__meta_netbox_cluster": "DC1"}, target.labels)
        self.assertDictContainsSubset(
            {"__meta_netbox_cluster_group": "VMware"}, target.labels
        )
        self.assertDictContainsSubset(
            {"__meta_netbox_cluster_type": "On Prem"}, target.labels
        )
        self.assertDictContainsSubset(
            {"__meta_netbox_tenant": "Acme Corp."}, target.labels
        )
        self.assertDictContainsSubset(
            {"__meta_netbox_tenant_slug": "acme"}, target.labels
        )
        self.assertDictContainsSubset({"__meta_netbox_site": "Campus A"}, target.labels)
        self.assertDictContainsSubset(
            {"__meta_netbox_site_slug": "campus-a"}, target.labels
        )
        self.assertDictContainsSubset({"__meta_netbox_role": "VM"}, target.labels)
        self.assertDictContainsSubset({"__meta_netbox_role_slug": "vm"}, target.labels)
        self.assertDictContainsSubset(
            {"__meta_netbox_platform": "Ubuntu 20.04"}, target.labels
        )
        self.assertDictContainsSubset(
            {"__meta_netbox_platform_slug": "ubuntu-20.04"}, target.labels
        )
        self.assertDictContainsSubset(
            {"__meta_netbox_ip": "192.168.0.1"}, target.labels
        )

    def test_device_minimal_to_target(self):
        target = mapper.device_to_target(build_minimal_device())
        self.assertEquals(target.targets, ["core-switch-01"])
        self.assertDictContainsSubset({"__meta_netbox_type": "device"}, target.labels)

    def test_device_full_to_target(self):
        target = mapper.device_to_target(build_device_full())
        self.assertEquals(target.targets, ["core-switch-full-01"])
        self.assertDictContainsSubset({"__meta_netbox_type": "device"}, target.labels)
        self.assertDictContainsSubset(
            {"__meta_netbox_role": "Core Switch"}, target.labels
        )
        self.assertDictContainsSubset(
            {"__meta_netbox_role_slug": "core-switch"}, target.labels
        )
        self.assertDictContainsSubset(
            {"__meta_netbox_device_type": "SRX"}, target.labels
        )
        self.assertDictContainsSubset(
            {"__meta_netbox_device_type_slug": "srx"}, target.labels
        )
        self.assertDictContainsSubset(
            {"__meta_netbox_platform": "Junos"}, target.labels
        )
        self.assertDictContainsSubset(
            {"__meta_netbox_platform_slug": "junos"}, target.labels
        )
        self.assertDictContainsSubset({"__meta_netbox_site": "Campus B"}, target.labels)
        self.assertDictContainsSubset(
            {"__meta_netbox_site_slug": "campus-b"}, target.labels
        )
        self.assertDictContainsSubset(
            {"__meta_netbox_ip": "2001:db8:1701::2"}, target.labels
        )

    def test_ip_minimal_to_target(self):
        target = mapper.ip_to_target(build_minimal_ip())
        self.assertEquals(target.targets, ["10.10.10.10"])
        self.assertDictContainsSubset({"__meta_netbox_status": "active"}, target.labels)
        self.assertDictContainsSubset(
            {"__meta_netbox_type": "ip_address"}, target.labels
        )

    def test_ip_full_to_target(self):
        target = mapper.ip_to_target(build_full_ip())
        self.assertEquals(
            target.targets,
            ["foo.example.com"],
            "IP with DNS name should use DNS name as target",
        )
        self.assertDictContainsSubset({"__meta_netbox_status": "active"}, target.labels)
        self.assertDictContainsSubset(
            {"__meta_netbox_type": "ip_address"}, target.labels
        )
        self.assertDictContainsSubset(
            {"__meta_netbox_ip": "10.10.10.10"},
            target.labels,
            "IP should not have an subnet",
        )
        self.assertDictContainsSubset(
            {"__meta_netbox_tenant": "Starfleet"}, target.labels
        )
        self.assertDictContainsSubset(
            {"__meta_netbox_tenant_slug": "starfleet"}, target.labels
        )
        self.assertDictContainsSubset(
            {"__meta_netbox_tenant_group": "Federation"}, target.labels
        )
        self.assertDictContainsSubset(
            {"__meta_netbox_tenant_group_slug": "federation"}, target.labels
        )
