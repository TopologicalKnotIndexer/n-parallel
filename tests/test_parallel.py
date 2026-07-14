from collections import Counter
import unittest

from n_parallel import arc_index_checker, n_parallel


TREFOIL = [[1, 5, 2, 4], [3, 1, 4, 6], [5, 3, 6, 2]]
POSITIVE_TYPE = [[1, 3, 2, 4], [3, 1, 4, 2]]


class ParallelTests(unittest.TestCase):
    def assert_valid_pd(self, pd_code):
        self.assertTrue(arc_index_checker(pd_code), pd_code)
        counts = Counter(label for crossing in pd_code for label in crossing)
        self.assertEqual(set(counts), set(range(1, 2 * len(pd_code) + 1)))
        self.assertTrue(all(count == 2 for count in counts.values()))

    def test_one_cable_is_identity(self):
        self.assertEqual(n_parallel(TREFOIL, 1), TREFOIL)
        self.assertEqual(n_parallel(POSITIVE_TYPE, 1), POSITIVE_TYPE)

    def test_two_cable_expands_every_crossing_to_four(self):
        result = n_parallel(TREFOIL, 2)
        self.assertEqual(len(result), 4 * len(TREFOIL))
        self.assert_valid_pd(result)

    def test_both_crossing_orientations_are_supported(self):
        result = n_parallel(POSITIVE_TYPE, 2)
        self.assertEqual(len(result), 8)
        self.assert_valid_pd(result)

    def test_explicit_r1_kinks_are_normalized_before_parallelization(self):
        trefoil_with_r1 = [
            [1, 5, 2, 4],
            [3, 7, 4, 6],
            [5, 3, 6, 2],
            [1, 8, 7, 8],
        ]
        self.assertEqual(
            n_parallel(trefoil_with_r1, 2),
            n_parallel(TREFOIL, 2),
        )
        self.assertEqual(n_parallel([[1, 1, 2, 2]], 2), [])

    def test_invalid_inputs_are_rejected(self):
        for value in (0, -1, True):
            with self.assertRaises(ValueError):
                n_parallel(TREFOIL, value)
        with self.assertRaises(ValueError):
            n_parallel([[1, 2, 3, 4]], 2)
        with self.assertRaises(ValueError):
            n_parallel([[1, 3, 2, 5], [3, 1, 4, 2]], 2)


if __name__ == "__main__":
    unittest.main()
