from unittest import TestCase
from ..open_oas.open_oas._utils import merge_recursive


class mergeDicts(TestCase):
    def test_flat_simple(self):
        d1 = {1: 11, 2: 22}
        d2 = {3: 33, 4: 44}
        self.assertEqual(
            merge_recursive([d1, d2]), {1: 11, 2: 22, 3: 33, 4: 44}
        )

    def test_flat_override(self):
        d1 = {1: 11, 2: 22}
        d2 = {3: 33, 4: 44, 2: 222}
        self.assertEqual(
            merge_recursive([d1, d2]), {1: 11, 2: 22, 3: 33, 4: 44}
        )

    def test_nested_dicts_simple(self):
        d1 = {
            1: {11: 11},
        }
        d2 = {1: {11: 111, 12: 122}}
        self.assertEqual(merge_recursive([d1, d2]), {1: {11: 11, 12: 122}})

    def test_deep_nested_dicts_simple(self):
        d1 = {
            1: {11: {1000: "1000"}},
        }
        d2 = {1: {11: {}, 12: 122}}
        self.assertEqual(
            merge_recursive([d1, d2]), {1: {11: {1000: "1000"}, 12: 122}}
        )

    def test_nested_lists_simple(self):
        d1 = {1: [4, 5]}
        d2 = {1: [1, 2, 3]}
        self.assertEqual(merge_recursive([d1, d2]), {1: [1, 2, 3, 4, 5]})

    def test_dict_in_list(self):
        d1 = {1: [{1: 1}, 5]}
        d2 = {1: [1, 2, 3]}
        self.assertEqual(merge_recursive([d1, d2]), {1: [1, 2, 3, {1: 1}, 5]})

    def test_list_in_dict(self):
        d1 = {1: {11: [11], 12: [12]}}
        d2 = {1: {11: [111], 12: [122]}}
        self.assertEqual(
            merge_recursive([d1, d2]), {1: {11: [111, 11], 12: [122, 12]}}
        )
