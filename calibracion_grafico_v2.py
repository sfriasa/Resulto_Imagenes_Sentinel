import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import rasterio
import os
import matplotlib.pyplot as plt

# --- 1. CONFIGURACIÓN DE LA RUTA Y ARCHIVOS ---
ruta_excel = r'D:\INFORMES-PECH\2025\AGOSTO\EXCEL\Datos_CE.xlsx'
# Columna por posición (índice 0-basado)
idx_x = 0
idx_y = 1
idx_conductividad = 2
idx_ubicacion = 3

ruta_ssi_mapa = r'D:\INFORMES-PECH\2025\AGOSTO\IMAGENES\L2A_T17LQL_A004571_20250721T153200\IMG_DATA\R10m\SSI_final.tiff'
ruta_calibrado_salida = os.path.join(os.path.dirname(ruta_ssi_mapa), 'SSI_calibrado_uScm.tiff')

# --- 2. LEER DATOS DE CAMPO Y EXTRAER VALORES SSI ---
print("Leyendo datos de campo desde el archivo de Excel...")
try:
    df_calibracion = pd.read_excel(ruta_excel)
    
    # Extraemos los datos por su índice de columna
    df_calibracion.dropna(subset=[df_calibracion.columns[idx_x], 
                                  df_calibracion.columns[idx_y], 
                                  df_calibracion.columns[idx_conductividad], 
                                  df_calibracion.columns[idx_ubicacion]], inplace=True)
    
    x_coords = df_calibracion.iloc[:, idx_x].tolist()
    y_coords = df_calibracion.iloc[:, idx_y].tolist()
    conductividad_medida = df_calibracion.iloc[:, idx_conductividad].tolist()
    ubicacion_data = df_calibracion.iloc[:, idx_ubicacion].tolist()
    
    with rasterio.open(ruta_ssi_mapa) as src:
        coordenadas_muestreo = list(zip(x_coords, y_coords))
        valores_ssi_muestra = [value[0] for value in src.sample(coordenadas_muestreo)]
    
    df_calibracion['SSI_Valor'] = valores_ssi_muestra
    df_calibracion['ubicacion'] = ubicacion_data
    
    print(f"Datos de Excel y valores de SSI extraídos correctamente. Se encontraron {len(df_calibracion)} puntos válidos.")

except Exception as e:
    print(f"Error al preparar los datos: {e}")
    exit()

# --- 3. DIVIDIR DATOS Y CONSTRUIR MODELOS ---
df_tierra_adentro = df_calibracion[df_calibracion['ubicacion'] == 'tierra_adentro']
df_costa = df_calibracion[df_calibracion['ubicacion'] == 'costa']

# Modelo para "tierra_adentro"
X_inland = df_tierra_adentro[['SSI_Valor']].values
y_inland = df_tierra_adentro.iloc[:, idx_conductividad].values
modelo_inland = LinearRegression().fit(X_inland, y_inland)
pendiente_inland = modelo_inland.coef_[0]
intercepto_inland = modelo_inland.intercept_

# Modelo para "costa"
X_coastal = df_costa[['SSI_Valor']].values
y_coastal = df_costa.iloc[:, idx_conductividad].values
modelo_coastal = LinearRegression().fit(X_coastal, y_coastal)
pendiente_coastal = modelo_coastal.coef_[0]
intercepto_coastal = modelo_coastal.intercept_

print("\n--- Modelos de Calibración ---")
print(f"Modelo TIERRA ADENTRO: µS/cm = {pendiente_inland:.2f} * SSI + {intercepto_inland:.2f}")
print(f"Coeficiente R²: {modelo_inland.score(X_inland, y_inland):.2f}")
print("\n")
print(f"Modelo COSTA: µS/cm = {pendiente_coastal:.2f} * SSI + {intercepto_coastal:.2f}")
print(f"Coeficiente R²: {modelo_coastal.score(X_coastal, y_coastal):.2f}")

plt.figure(figsize=(10, 6))
plt.scatter(X_inland, y_inland, color='blue', label='Puntos Tierra Adentro')
plt.plot(X_inland, modelo_inland.predict(X_inland), color='blue', linewidth=2, linestyle='--', label='Línea de Regresión T.Adentro')

plt.scatter(X_coastal, y_coastal, color='red', label='Puntos Costa')
plt.plot(X_coastal, modelo_coastal.predict(X_coastal), color='red', linewidth=2, linestyle='--', label='Línea de Regresión Costa')

plt.xlabel('Valor del Índice SSI')
plt.ylabel('Conductividad del Suelo (µS/cm)')
plt.title('Calibración de Salinidad por Segmentos')
plt.legend()
plt.grid(True)
plt.show()

print("La calibración se completó y se generó el gráfico.")