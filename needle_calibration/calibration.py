"""Synthetic MRI acquisition and an estimator using only depths and measured markers."""
from dataclasses import dataclass

import numpy as np

from forward_kinematics.forward import shaft_pose
from mri_to_robot_transform.registration import MARKERS, mri_to_robot, transform_points


@dataclass
class CalibrationResult:
    angle_deg: float
    deflections_mm: np.ndarray
    quadratic_per_mm: float


def simulate(angle_deg=45., bend_per_mm=0.001):
    """Return encoder rows (t, theta, d) and MRI markers (pose, M1..M4, xyz)."""
    alpha = np.deg2rad(angle_deg)
    direction = np.array([0., -np.sin(alpha), np.cos(alpha)])
    lateral_x = np.array([1., 0., 0.])
    lateral_y = np.cross(direction, lateral_x)
    joints, observations = [], []
    for translation, rotation in [(0., 0.), (5., 15.), (10., 30.)]:
        pose = shaft_pose(translation, rotation)
        # Each sweep begins retracted at the same needle spin phase.
        for depth in np.linspace(0., 50., 41):
            phase = 2. * np.pi * depth / 5.
            lateral = np.cos(phase) * lateral_x + np.sin(phase) * lateral_y
            tip = depth * direction + bend_per_mm * depth**2 * lateral
            observations.append(transform_points(pose, np.vstack([MARKERS, tip])))
            joints.append((translation, rotation, depth))
    return np.array(joints), np.array(observations)


def estimate(depths_mm, markers_mri):
    """Recover the axis from axial projections, then measure perpendicular offsets."""
    depth = np.asarray(depths_mm, dtype=float)
    scans = np.asarray(markers_mri, dtype=float)
    if depth.ndim != 1 or scans.shape != (depth.size, 4, 3):
        raise ValueError("Supply one depth and four ordered xyz markers per scan")
    if not np.isfinite(scans).all() or not np.isfinite(depth).all() or np.any(depth < 0):
        raise ValueError("Depths must be nonnegative and observations finite")
    if depth.size < 3 or not np.any(depth > 0):
        raise ValueError("Multiple insertions at positive depth are required")
    tips = np.array([transform_points(mri_to_robot(scan[:3]), scan[3]) for scan in scans])
    # For a unit axis u and a lateral offset e, q = d*u + e gives q dot u = d.
    axis, _, rank, _ = np.linalg.lstsq(tips, depth, rcond=None)
    length = np.linalg.norm(axis)
    if length < 1e-12 or (rank < 3 and not np.isclose(length, 1.)):
        raise ValueError("Scans do not uniquely determine a unit insertion axis")
    axis /= length
    deflections = np.linalg.norm(tips - np.outer(tips @ axis, axis), axis=1)
    squared_depth = depth**2
    coefficient = (squared_depth @ deflections) / (squared_depth @ squared_depth)
    angle = np.rad2deg(np.arctan2(np.linalg.norm(axis[:2]), axis[2]))
    return CalibrationResult(float(angle), deflections, float(coefficient))
