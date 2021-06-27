from django.test import TestCase
from django.test.utils import tag
from dcim.models.devices import DeviceType
from dcim.models.sites import Site
from netbox_prometheus_sd.api.models import Target, TargetType

from ..api import mapper

from ipam.models import IPAddress
from dcim.models import Device, DeviceRole, Platform
from tenancy.models import Tenant, TenantGroup

from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine


def build_minimal_vm():
    return VirtualMachine(name="vm-01.example.com")


def build_vm_full():
    return VirtualMachine(
        name="vm-full-01.example.com",
        cluster=Cluster(
            name="DC1",
            group=ClusterGroup(name="VMware"),
            type=ClusterType(name="On Prem"),
            site=Site(name="Campus A", slug="campus-a"),
        ),
        tenant=Tenant(name="Acme Corp.", slug="acme"),
        role=DeviceRole(name="VM", slug="vm", vm_role=True),
        platform=Platform(name="Ubuntu 20.04", slug="ubuntu-20.04"),
        primary_ip4=IPAddress(address="192.168.0.1/24"),
    )


def build_minimal_device():
    return Device(name="core-switch-01")


def build_device_full():
    return Device(
        name="core-switch-full-01",
        tenant=Tenant(name="Acme Corp.", slug="acme"),
        device_role=DeviceRole(name="Core Switch", slug="core-switch"),
        platform=Platform(name="Junos", slug="junos"),
        site=Site(name="Campus A", slug="campus-a"),
        device_type=DeviceType(model="SRX", slug="srx"),
        primary_ip6=IPAddress(address="2001:db8:1701::2/64"),
    )


def build_minimal_ip():
    return IPAddress(address="10.10.10.10/24")


def build_full_ip():
    return IPAddress(
        address="10.10.10.10/24",
        tenant=Tenant(
            name="Starfleet",
            slug="starfleet",
            group=TenantGroup(name="Federation", slug="federation"),
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
        self.assertDictContainsSubset({"__meta_netbox_site": "Campus A"}, target.labels)
        self.assertDictContainsSubset(
            {"__meta_netbox_site_slug": "campus-a"}, target.labels
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
