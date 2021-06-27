from django.test import TestCase
from netbox_prometheus_sd.api.models import Target


class ModelTests(TestCase):
    def test_target_add_label(self):

        t = Target("10.10.10.10")
        t.add_label("foo", "bar")

        assert t.labels == {
            "__meta_netbox_foo": "bar",
        }

    def test_target_add_label_invalid_character(self):

        t = Target("10.10.10.10")
        t.add_label("foo-baz", "bar")
        t.add_label("baz foo", "bar")

        assert t.labels == {
            "__meta_netbox_foo_baz": "bar",
            "__meta_netbox_baz_foo": "bar",
        }
