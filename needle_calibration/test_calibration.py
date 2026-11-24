import unittest

from numpy.testing import assert_allclose

from .calibration import simulate, estimate


class CalibrationTests(unittest.TestCase):
    def test_calibration_recovers_measurements(self):
        for angle, bend in [(45.,0.001),(38.,0.0007),(45.,0.)]:
            with self.subTest(angle=angle, bend=bend):
                joints, scans = simulate(angle, bend)
                result = estimate(joints[:,2], scans)
                self.assertAlmostEqual(result.angle_deg, angle, places=8)
                self.assertAlmostEqual(result.quadratic_per_mm, bend, places=10)
                assert_allclose(result.deflections_mm, bend*joints[:,2]**2, atol=1e-9)
