from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status


from ipam.models import IPAddress
from tenancy.models import Tenant
from virtualization.models import Cluster, ClusterType, VirtualMachine, VMInterface
from dcim.models import Site
from django.contrib.contenttypes.models import ContentType


class AppMetricEndpointTests(TestCase):
    """Test cases for ensuring API endpoint is working properly."""

    def setUp(self):

        # Base URL.
        self.url = "/api/plugins/prometheus-sd/targets/"
        self.client = APIClient()

        # Seed Data
        tenant = Tenant.objects.create(name="Starfleet", slug="starfleet")

        site = Site.objects.create(name="DS9", slug="ds9")

        cluster_type = ClusterType.objects.create(name="Datacenter", slug="datacenter")
        cluster = Cluster.objects.create(
            name="Default Cluster", type=cluster_type, site=site
        )

        vm = VirtualMachine.objects.create(
            name="Instance-01", cluster=cluster, tenant=tenant
        )

        ip = IPAddress.objects.create(address="10.10.10.10/24")
        interface = VMInterface.objects.create(virtual_machine=vm, name="default")

        vm_interface_ct = ContentType.objects.get_for_model(VMInterface)

        ip.assigned_object_id = interface.id
        ip.assigned_object_type = vm_interface_ct
        ip.save()

        vm.primary_ip4 = ip
        vm.save()

    def test_endpoint(self):
        """Ensure the endpoint is working properly and is not protected by authentication."""
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
