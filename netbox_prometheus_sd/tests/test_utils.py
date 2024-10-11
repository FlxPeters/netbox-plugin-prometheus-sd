from . import utils
from django.test import TestCase


class UtilsTests(TestCase):

    def test_dictContainsSubset(self):
        subset = {"name": "Foo", "age": 25}
        fullset = {"name": "Foo", "age": 25, "city": "Bar"}

        self.assertTrue(utils.dictContainsSubset(subset, fullset))

        subset = {"name": "Foo", "age": 25, "city": "Bar"}
        fullset = {"name": "Foo", "age": 25}

        self.assertFalse(utils.dictContainsSubset(subset, fullset))

        subset = {"name": "Foo", "age": 25}
        fullset = {"name": "Foo", "age": 30, "city": "Bar"}

        self.assertFalse(utils.dictContainsSubset(subset, fullset))
