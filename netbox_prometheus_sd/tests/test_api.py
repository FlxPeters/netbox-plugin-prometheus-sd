from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from tenancy.models import Tenant
from virtualization.models import Cluster, ClusterType
from dcim.models import Site

from . import utils


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

        utils.create_vm("Instance-01", "10.10.10.10/24", cluster=cluster, tenant=tenant)
        utils.create_vm("Instance-02", "10.10.10.11/24", cluster=cluster, tenant=tenant)

    def test_endpoint(self):
        """Ensure the endpoint is working properly and is not protected by authentication."""
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
