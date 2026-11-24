import numpy as np

MARKERS = np.array([[0., -60., -100.], [0., 0., -100.], [0., -10., -20.]])
MARKERS.setflags(write=False)


def mri_to_robot(markers_mri):
    """Fit the proper rigid MRI -> current end-effector map given M1,M2,M3."""
    source = np.asarray(markers_mri, dtype=float)
    if source.shape != (3, 3) or not np.isfinite(source).all():
        raise ValueError("Expected finite xyz coordinates for M1, M2 and M3")
    centered = source - source.mean(axis=0)
    if np.linalg.matrix_rank(centered) < 2:
        raise ValueError("Marker centres must form a noncollinear triangle")
    u, _, vt = np.linalg.svd(centered.T @ (MARKERS - MARKERS.mean(axis=0)))
    v = vt.T
    correction = np.diag([1., 1., np.sign(np.linalg.det(v @ u.T))])
    rotation = v @ correction @ u.T
    frame = np.eye(4)
    frame[:3, :3] = rotation
    frame[:3, 3] = MARKERS.mean(axis=0) - rotation @ source.mean(axis=0)
    return frame


def transform_points(frame, points):
    """Apply a homogeneous matrix to one xyz point or an array of xyz rows."""
    return np.asarray(points) @ frame[:3, :3].T + frame[:3, 3]
