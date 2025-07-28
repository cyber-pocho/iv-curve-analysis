import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fs import clean

# Cargar datos del semiconductor
pth2 = r"C:\Users\Famil\Desktop\DATA ANALYSIS\experimental data\data\IV_semiconductor.dat"
df2 = clean(pth2)

# Extraer datos
V = df2['i-v_voltage_ch1_v'].values
I = df2['i-v_current_ch1_ma'].values

# Filtrar solo corrientes positivas para análisis semilog
mask_positive = I > 0
V_pos = V[mask_positive]
I_pos = I[mask_positive]

# Calcular slope de la gráfica semilog (ln(I) vs V)
ln_I = np.log(I_pos)
slope = np.polyfit(V_pos, ln_I, 1)[0]  # Pendiente
intercept = np.polyfit(V_pos, ln_I, 1)[1]  # Intercepto

I0 = np.exp(intercept)  # Corriente de saturación

print(f"ECUACIÓN I-V DEL SEMICONDUCTOR:")
print(f"I = {I0:.2e} × exp({slope:.2f} × V)")
print(f"Slope (pendiente semilog) = {slope:.4f}")

# Gráficas
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Gráfica normal (lineal)
ax1.plot(V, I, 'bo', markersize=3, alpha=0.7)
ax1.set_xlabel('Voltage (V)')
ax1.set_ylabel('Current (mA)')
ax1.set_title('Semiconductor I-V (Escala Linear)')
ax1.grid(True, alpha=0.3)

# Gráfica semilog
ax2.semilogy(V, I, 'ro', markersize=3, alpha=0.7, label='Data')
# Línea de ajuste exponencial
V_fit = np.linspace(V_pos.min(), V_pos.max(), 100)
I_fit = I0 * np.exp(slope * V_fit)
ax2.semilogy(V_fit, I_fit, 'k--', linewidth=2, label=f'I = {I0:.1e}×exp({slope:.2f}V)')
ax2.set_xlabel('Voltage (V)')
ax2.set_ylabel('Current (mA) - Log Scale')
ax2.set_title('Semiconductor I-V (Escala Log)')
ax2.grid(True, which='both', alpha=0.3)
ax2.legend()

plt.tight_layout()
plt.show()