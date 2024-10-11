import json

try:
    from users.models import ObjectPermission
    from users.models import User
    from core.models import ObjectType

except ImportError:
    # Fallback for old NetBox versions < 4.0
    from django.contrib.contenttypes.models import ContentType as ObjectType
    from django.contrib.auth.models import User

from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from . import utils


class ApiEndpointTests(TestCase):
    """Test cases for ensuring API endpoint is working properly."""

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
