# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

# Data
x = np.array([30, 50, 70, 90, 110, 130, 150])
y = np.array([0.4187211906890128, 0.6235379600248296, 0.9110614824332695,
              1.0448045477963992, 0.9917414752741963, 1.3247919083798896, 1.5325760757914344])

# Generate new x values for a smooth curve
x_new = np.linspace(x.min(), x.max(), 300)

# Perform spline interpolation
spl = make_interp_spline(x, y, k=3)  # Cubic spline
y_smooth = spl(x_new)

# 寻找 y = 0.48 对应的 x 值
y_target = 0.48
x_target = x_new[np.argmin(np.abs(y_smooth - y_target))]
# 打印结果
print(f"y = 0.48 对应的 x 值为: {x_target}")
# Plot the data and the spline interpolation curve
plt.figure(figsize=(8, 6))
plt.scatter(x, y, label='Data')
plt.plot(x_new, y_smooth, color='red', label='Spline Interpolation')
plt.xlabel('Extrusion Rate/%')
plt.ylabel('Width/mm')
plt.legend()
plt.show()
