import pandas as pd
import numpy as np
import plotly.graph_objects as go
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

# Crear gráfica lineal (primera gráfica)
fig1 = go.Figure()
fig1.add_trace(
    go.Scatter(
        x=V, 
        y=I, 
        mode='markers',
        marker=dict(color='blue', size=3, opacity=0.7),
        name='Data'
    )
)

fig1.update_layout(
    title="Semiconductor I-V (Escala Linear)",
    xaxis_title="Voltage (V)",
    yaxis_title="Current (mA)",
    template="plotly_white",
    width=600,
    height=500,
    showlegend=False
)
fig1.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
fig1.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

# Crear gráfica semilog (segunda gráfica)
fig2 = go.Figure()

# Datos experimentales
fig2.add_trace(
    go.Scatter(
        x=V, 
        y=I, 
        mode='markers',
        marker=dict(color='red', size=3, opacity=0.7),
        name='Data'
    )
)

# Línea de ajuste exponencial
V_fit = np.linspace(V_pos.min(), V_pos.max(), 100)
I_fit = I0 * np.exp(slope * V_fit)
fig2.add_trace(
    go.Scatter(
        x=V_fit, 
        y=I_fit, 
        mode='lines',
        line=dict(color='black', width=3, dash='dash'),
        name=f'I = {I0:.1e}×exp({slope:.2f}V)'
    )
)

fig2.update_layout(
    title="Semiconductor I-V (Escala Log)",
    xaxis_title="Voltage (V)",
    yaxis_title="Current (mA) - Log Scale",
    yaxis_type="log",
    template="plotly_white",
    width=600,
    height=500,
    legend=dict(x=0.02, y=0.98)
)
fig2.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
fig2.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

# Guardar las gráficas como PNG
fig1.write_image("semiconductor_iv_linear.png", width=600, height=500, scale=2)
fig2.write_image("semiconductor_iv_log.png", width=600, height=500, scale=2)

print("Gráficas guardadas como:")
print("- semiconductor_iv_linear.png")
print("- semiconductor_iv_log.png")