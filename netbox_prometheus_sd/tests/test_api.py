import json

from users.models import ObjectPermission, User
from core.models import ObjectType

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from rest_framework.test import APIClient
from rest_framework import status

from . import utils


class AuthenticatedApiTestCase(TestCase):
    """Base class providing an API client authenticated with view permissions."""

    def setUp(self):

        self.client = APIClient()

        # Create test user and view permissions
        user = User.objects.create_user("username", "Pas$w0rd")
        obj_perm = ObjectPermission(name="test", actions=["view"])
        obj_perm.save()
        obj_perm.users.add(user)
        obj_perm.object_types.add(
            ObjectType.objects.get(app_label="dcim", model="device")
        )
        obj_perm.object_types.add(
            ObjectType.objects.get(app_label="ipam", model="ipaddress")
        )
        obj_perm.object_types.add(
            ObjectType.objects.get(app_label="ipam", model="service")
        )
        obj_perm.object_types.add(
            ObjectType.objects.get(app_label="virtualization", model="virtualmachine")
        )
        self.client.force_authenticate(user)


class ApiEndpointTests(AuthenticatedApiTestCase):
    """Test cases for ensuring API endpoint is working properly."""

    def test_endpoint_device(self):
        """Ensure device endpoint returns a valid response"""

        for i in range(1, 61):
            utils.build_device_full(f"api-test-{i}.example.com", i)

        resp = self.client.get("/api/plugins/prometheus-sd/devices/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.content)

        self.assertIsNotNone(data[0]["targets"])
        self.assertIsNotNone(data[0]["labels"])
        self.assertEqual(len(data), 60)

    def test_endpoint_virtual_machine(self):
        """Ensure virtual machine endpoint returns a valid response"""

        for i in range(1, 61):
            utils.build_vm_full(f"api-test-vm-{i}.example.com", i)

        resp = self.client.get("/api/plugins/prometheus-sd/virtual-machines/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.content)

        self.assertIsNotNone(data[0]["targets"])
        self.assertIsNotNone(data[0]["labels"])
        # Full vm contains two entry in the config context so we have to double the number of vm
        self.assertEqual(len(data), 120)

    def test_endpoint_ip_address(self):
        """Ensure ip address endpoint returns a valid response"""

        for i in range(1, 61):
            utils.build_full_ip(address=f"10.10.10.{i}/24")

        resp = self.client.get("/api/plugins/prometheus-sd/ip-addresses/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.content)

        self.assertIsNotNone(data[0]["targets"])
        self.assertIsNotNone(data[0]["labels"])
        self.assertEqual(len(data), 60)

    def test_endpoint_service(self):
        """Ensure service endpoint returns a valid response"""

        for i in range(1, 61):
            utils.build_vm_full(f"api-test-vm-{i}.example.com", i)

        resp = self.client.get("/api/plugins/prometheus-sd/services/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.content)

        self.assertIsNotNone(data[0]["targets"])
        self.assertIsNotNone(data[0]["labels"])
        self.assertEqual(len(data), 60)


class ApiQueryCountTests(AuthenticatedApiTestCase):
    """Regression tests for the N+1 queries reported in issue #265.

    These endpoints are unpaginated, so a relation that is read by a serializer
    but not prefetched costs one query per row. Rather than assert an exact
    query count (which legitimately shifts between Netbox releases), assert that
    the count does not grow when the number of objects grows -- that is the
    property an N+1 breaks.
    """

    def assertQueryCountDoesNotScale(self, url, build, first=5, second=15):
        for i in range(1, first + 1):
            build(i)

        # Warm up caches (content types, permissions) that are populated on the
        # first request and would otherwise be counted only in the small run.
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

        with CaptureQueriesContext(connection) as few_objects:
            self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

        for i in range(first + 1, second + 1):
            build(i)

        with CaptureQueriesContext(connection) as many_objects:
            self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

        self.assertEqual(
            len(few_objects),
            len(many_objects),
            f"Query count for {url} grew from {len(few_objects)} queries with "
            f"{first} objects to {len(many_objects)} with {second}. A relation "
            f"used by the serializer is likely missing from the queryset in "
            f"api/views.py.",
        )

    def test_device_endpoint_query_count_does_not_scale(self):
        self.assertQueryCountDoesNotScale(
            "/api/plugins/prometheus-sd/devices/",
            lambda i: utils.build_device_full(f"query-count-{i}.example.com", i),
        )

    def test_virtual_machine_endpoint_query_count_does_not_scale(self):
        self.assertQueryCountDoesNotScale(
            "/api/plugins/prometheus-sd/virtual-machines/",
            lambda i: utils.build_vm_full(f"query-count-vm-{i}.example.com", i),
        )

    def test_service_endpoint_query_count_does_not_scale(self):
        self.assertQueryCountDoesNotScale(
            "/api/plugins/prometheus-sd/services/",
            lambda i: utils.build_vm_full(f"query-count-svc-{i}.example.com", i),
        )

    def test_ip_address_endpoint_query_count_does_not_scale(self):
        self.assertQueryCountDoesNotScale(
            "/api/plugins/prometheus-sd/ip-addresses/",
            lambda i: utils.build_full_ip(address=f"10.10.20.{i}/24"),
        )
