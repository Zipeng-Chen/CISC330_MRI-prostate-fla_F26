import unittest

from numpy.testing import assert_allclose
import numpy as np

from .registration import MARKERS, mri_to_robot, transform_points
from .examples import REGISTRATION_CASES


class RegistrationTests(unittest.TestCase):
    def test_three_registration_cases(self):
        for name, observations, prediction in REGISTRATION_CASES:
            with self.subTest(case=name):
                frame = mri_to_robot(observations)
                assert_allclose(frame, prediction, atol=1e-10, rtol=0)
                assert_allclose(transform_points(frame, observations), MARKERS, atol=1e-10)
                self.assertAlmostEqual(np.linalg.det(frame[:3, :3]), 1.)
    
    def test_collinear_markers(self):
        with self.assertRaises(ValueError):
            mri_to_robot([[0,0,0],[1,0,0],[2,0,0]])
