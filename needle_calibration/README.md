# Needle calibration (19 points)

**Acquisition.** Start with the robot retracted in the ideal aligned MRI home frame. Perform three sweeps at shaft settings $(t,\theta)=(0,0^\circ),(5,15^\circ),(10,30^\circ)$. Retract and reset the needle spin phase before each new sweep. For each sweep advance $d=0,1.25,\ldots,50$ mm, recording encoder depth and all four MRI marker positions at every setting. This gives 41 depths per pose and 123 observations. The needle spins one turn per 5 mm of insertion. The 1.25 mm step samples all four quarter-turn phases. Sampling only at multiples of 5 mm would repeatedly observe bending in the same direction.

**Generate the observations.** In $E$, let the true guide direction be $u=(0,-\sin\alpha,\cos\alpha)$, choose $a=(1,0,0)$ and $b=u\times a$. The synthetic needle tip is

$$
q(d)=d\,u+0.001d^2\,[a\cos(2\pi d/5)+b\sin(2\pi d/5)].
$$

The spin term is perpendicular to the central line and has magnitude $0.001d^2$ mm. For each configuration, apply the shaft rotation and translation to M1–M3 and to $q(d)$ to obtain the four MRI measurements. Only M4 follows the spinning needle. The synthetic acquisition assumes ideal localization and a straight central axis through the origin.

**Estimate from observed markers.** Use the measured M1–M3 to register each individual scan into $E$. Apply that scan's transform to its measured M4 to obtain $q_i$. The estimator receives just the marker coordinates and encoder depths. It does not receive the simulated angle, spin phase, or bending coefficient.

1. Stack $q_i^T$ as rows of $Q$. Since each lateral offset is perpendicular to the unit axis, $q_i^Tu=d_i$. Fit $Qu\simeq d$ by least squares and normalize the recovered direction. Sampling different depths and spin phases supplies independent directions.
2. With the resulting unit vector $\hat u$, estimate the angle to the $+z$ shaft axis as $\hat\alpha=\operatorname{atan2}(\sqrt{\hat u_x^2+\hat u_y^2},\hat u_z)$. Measure each lateral deflection as the perpendicular distance $\delta_i=\|q_i-(q_i^T\hat u)\hat u\|$.
3. Compare these measured distances to the prescribed law. Fitting $\delta_i=k d_i^2$ through zero gives $\hat k=\sum_i d_i^2\delta_i/\sum_i d_i^4$. The origin constraint represents zero bending at zero insertion.

| Insertion (mm) | Ground-truth deflection (mm) | Estimated deflection (mm) |
|---:|---:|---:|
| 0 | 0.000 | 0.000 |
| 10 | 0.100 | 0.100 |
| 20 | 0.400 | 0.400 |
| 30 | 0.900 | 0.900 |
| 40 | 1.600 | 1.600 |
| 50 | 2.500 | 2.500 |

The recovered axis angle was **45.000000°** and the coefficient was **0.001000 mm⁻¹**. The maximum absolute discrepancy over all 123 deflection estimates was $1.15\times10^{-13}$ mm. The plotted observations from all three shaft poses overlap after registration. This accuracy reflects noiseless synthetic measurements. A separate automated case uses a 38° guide and a different coefficient to check that the estimator tracks the data.

![Recovered needle deflection and central angle against simulation ground truth](results/calibration.png)

[All simulated MRI observations and recovered deflections](results/calibration.csv) · [Calibration summary](results/validation.txt)

[Simulation and estimator](calibration.py) · [Plot and CSV generator](demo.py)


## Reproduce the checks

From the repository root with NumPy installed and Matplotlib installed, run

```powershell
python -m unittest needle_calibration.test_calibration -v
python -m needle_calibration.demo
```

[Task tests](test_calibration.py) · [Validation results](results/validation.txt)
