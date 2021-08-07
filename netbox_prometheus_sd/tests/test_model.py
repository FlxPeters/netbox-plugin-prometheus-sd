from django.test import TestCase
from netbox_prometheus_sd.api.models import Target


class ModelTests(TestCase):
    def test_target_add_label(self):

        target = Target("10.10.10.10")
        target.add_label("foo", "bar")

        self.assertDictContainsSubset({"__meta_netbox_foo": "bar"}, target.labels)

    def test_target_add_label_invalid_character(self):

        target = Target("10.10.10.10")
        target.add_label("foo-baz", "bar")
        target.add_label("baz foo", "bar")

        self.assertDictContainsSubset({"__meta_netbox_foo_baz": "bar"}, target.labels)
        self.assertDictContainsSubset({"__meta_netbox_baz_foo": "bar"}, target.labels)
