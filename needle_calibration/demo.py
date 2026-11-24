import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .calibration import estimate, simulate


def run_calibration():
    output = Path(__file__).resolve().parent / "results"
    output.mkdir(exist_ok=True)
    lines = []
    joints, scans = simulate()
    depth = joints[:, 2]
    truth = 0.001 * depth**2
    result = estimate(depth, scans)
    lines.extend([f"Calibration: {depth.size} MRI observations",
                  f"Central angle: {result.angle_deg:.8f} deg (truth 45 deg)",
                  f"Quadratic coefficient: {result.quadratic_per_mm:.9f} /mm (truth 0.001 /mm)",
                  f"Max deflection error: {max(abs(result.deflections_mm-truth)):.3e} mm"])
    with (output / "calibration.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        labels = [f"M{i}_{axis}_MRI_mm" for i in range(1,5) for axis in "xyz"]
        writer.writerow(["t_mm","theta_deg","d_mm",*labels,"estimated_mm","truth_mm"])
        for joint, scan, measured, nominal in zip(joints, scans, result.deflections_mm, truth):
            writer.writerow([*joint,*scan.ravel(),measured,nominal])

    fig, (ax, angle_ax) = plt.subplots(1, 2, figsize=(8.5, 3.6),
                                       gridspec_kw={"width_ratios":[2.4, 1]}, layout="constrained")
    depths = np.unique(depth)
    ax.plot(depths, 0.001 * depths**2, color="#194f74", label="Simulation truth")
    ax.scatter(depth, result.deflections_mm, s=19, facecolors="none",
               edgecolors="#c45516", label="Recovered (all poses)", zorder=3)
    ax.set(xlabel="Insertion depth (mm)", ylabel="Lateral deflection (mm)",
           title="Needle deflection")
    ax.legend(frameon=False)
    angle_ax.bar(["Truth","Estimate"], [45.,result.angle_deg], color=["#194f74","#c45516"])
    angle_ax.set(ylabel="Angle to shaft (degrees)", ylim=(0,55), title="Central axis")
    for x, value in enumerate([45.,result.angle_deg]):
        angle_ax.text(x, value+1, f"{value:.2f}°", ha="center")
    fig.savefig(output / "calibration.png", dpi=160)
    plt.close(fig)
    (output / "validation.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return lines


if __name__ == "__main__":
    print("\n".join(run_calibration()))
