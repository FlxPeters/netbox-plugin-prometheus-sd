from django.test import TestCase

from ipam.models import Service
from tenancy.models import Tenant
from utilities.testing import ChangeLoggedFilterSetTests

from . import utils
from ..filtersets import ServiceFilterSet


class ServiceTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = Service.objects.all()
    filterset = ServiceFilterSet

    @classmethod
    def setUpTestData(cls):
        """Netbox requires us to define test data in this method, otherwise the ORM won't pick them."""
        for i in range(1, 4):
            utils.build_device_full(f"firewall-full-0{i}", i)
            utils.build_vm_full(f"vm-full-0{i}.example.com", i)

    def test_device_tenant(self):
        tenant = Tenant.objects.all()[0]

        params = {"tenant_id": [tenant.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)
        params = {"tenant": [tenant.slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)

    def test_vm_tenant(self):
        tenant = Tenant.objects.all()[0]

        params = {"tenant_id": [tenant.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)
        params = {"tenant": [tenant.slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)
