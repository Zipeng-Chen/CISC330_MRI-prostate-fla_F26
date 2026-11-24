# MRI-to-robot transform (13 points)

The scanner measures three corresponding marker centres. In the moving end-effector frame $E$, their known positions in mm are $M_1=(0,-60,-100)$, $M_2=(0,0,-100)$, and $M_3=(0,-10,-20)$. The origin is the intersection of the shaft centreline and nominal needle line. The frame is right-handed with $+z$ along the shaft. The shared home-position sketch in the repository README defines the other axes and joint signs. In ideal aligned home, the scanner frame, fixed robot home frame $H$, and $E$ coincide. After shaft motion, $E$ moves relative to $H$.

Let $a_i$ be the ordered MRI observations and $b_i$ the corresponding known points in $E$. Choose $R,t$ to minimize $\sum_i\|Ra_i+t-b_i\|^2$ subject to $R^TR=I$ and $\det R=1$. Centring the two point sets removes the translation. Construct $C=\sum_i(a_i-\bar a)(b_i-\bar b)^T$ and compute its singular value decomposition $C=U\Sigma V^T$. Then

$$
R=V\,\mathrm{diag}(1,1,\det(VU^T))\,U^T,\qquad t=\bar b-R\bar a.
$$

The sign correction enforces a proper rotation. The three markers lie in one plane but form a triangle with nonzero area. Its two independent edge directions and their cross product fix the orientation. Collinear input is rejected because the twist about the marker line would be undetermined.

$$
p_E=F_{E\leftarrow MRI}\,p_{MRI},\qquad
F_{E\leftarrow MRI}=\begin{bmatrix}R&t\\0&1\end{bmatrix}.
$$

**Hand predictions.** Let $(x,y,z)$ denote robot coordinates and $(X,Y,Z)$ MRI coordinates. Each row defines an independent hypothetical scanner pose. Substituting the known markers into the forward rule gives the inputs. Reversing the rule gives the expected output matrix row by row, with homogeneous bottom row $(0,0,0,1)$.

| Test | Robot → MRI rule used on paper | Input MRI points M1, M2, M3 (mm) | Expected MRI → robot output $(x,y,z)$ |
|---|---|---|---|
| Translation | $(x+10,y-5,z+7)$ | $(10,-65,-93)$, $(10,-5,-93)$, $(10,-15,-13)$ | $(X-10,Y+5,Z-7)$ |
| Rotation | $(x,-z,y)$ | $(0,100,-60)$, $(0,100,0)$, $(0,20,-10)$ | $(X,Z,-Y)$ |
| Combined | $(z+8,x-6,y+4)$ | $(-92,-6,-56)$, $(-92,-6,4)$, $(-12,-6,-6)$ | $(Y+6,Z-4,X-8)$ |

The first case isolates the translation signs. The second checks a right-handed quarter turn around $x$. The third cyclically permutes all three axes and translates the origin, so reversing the operation order produces the wrong offset. For example, the combined-case map sends MRI point $(-92,-6,-56)$ to robot point $(0,-60,-100)$, exactly M1. The test compares **every matrix entry** against the paper prediction. The largest measured marker residual across the three cases was $2.14\times10^{-14}$ mm.

[Registration code](registration.py) · [Numerical validation](results/validation.txt)


## Reproduce the checks

From the repository root with NumPy installed, run

```powershell
python -m unittest mri_to_robot_transform.test_registration -v
```

[Task tests](test_registration.py) · [Validation results](results/validation.txt)
