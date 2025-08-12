import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import rasterio
import os

# --- 1. CONFIGURACIÓN DE LA RUTA Y ARCHIVOS ---
ruta_excel = r'D:\INFORMES-PECH\2025\AGOSTO\EXCEL\Datos_CE.xlsx'
columna_x = 'cooreste'
columna_y = 'coornorte'
columna_conductividad = 'ce'
columna_ubicacion = 'ubicacion'

ruta_ssi_mapa = r'D:\INFORMES-PECH\2025\AGOSTO\IMAGENES\L2A_T17LQL_A004571_20250721T153200\IMG_DATA\R10m\SSI_final.tiff'
ruta_calibrado_salida = os.path.join(os.path.dirname(ruta_ssi_mapa), 'SSI_calibrado_uScm_final.tiff')

# --- 2. LEER DATOS DE CAMPO Y EXTRAER VALORES SSI ---
print("Leyendo datos de campo y extrayendo valores SSI...")
try:
    df_calibracion = pd.read_excel(ruta_excel)
    df_calibracion.columns = df_calibracion.columns.str.strip().str.lower()
    df_calibracion.dropna(subset=[columna_x, columna_y, columna_conductividad, columna_ubicacion], inplace=True)
    
    x_coords = df_calibracion[columna_x].tolist()
    y_coords = df_calibracion[columna_y].tolist()
    
    with rasterio.open(ruta_ssi_mapa) as src:
        coordenadas_muestreo = list(zip(x_coords, y_coords))
        valores_ssi_muestra = [value[0] for value in src.sample(coordenadas_muestreo)]
    
    df_calibracion['SSI_Valor'] = valores_ssi_muestra
    
except Exception as e:
    print(f"Error al preparar los datos de calibración: {e}")
    exit()

# --- 3. CONSTRUIR LOS DOS MODELOS DE CALIBRACIÓN ---
df_tierra_adentro = df_calibracion[df_calibracion[columna_ubicacion] == 'tierra_adentro']
df_costa = df_calibracion[df_calibracion[columna_ubicacion] == 'costa']

# Modelo para "tierra_adentro"
X_inland = df_tierra_adentro[['SSI_Valor']].values
y_inland = df_tierra_adentro[columna_conductividad].values
modelo_inland = LinearRegression().fit(X_inland, y_inland)
pendiente_inland = modelo_inland.coef_[0]
intercepto_inland = modelo_inland.intercept_

# Modelo para "costa"
X_coastal = df_costa[['SSI_Valor']].values
y_coastal = df_costa[columna_conductividad].values
modelo_coastal = LinearRegression().fit(X_coastal, y_coastal)
pendiente_coastal = modelo_coastal.coef_[0]
intercepto_coastal = modelo_coastal.intercept_

print("Modelos de calibración construidos.")

# --- 4. ABRIR MAPA SSI COMPLETO Y APLICAR MODELOS ---
try:
    with rasterio.open(ruta_ssi_mapa) as src:
        mapa_ssi = src.read(1).astype(float)
        perfil_salida = src.profile.copy()
        
        # Obtenemos las coordenadas de cada píxel del mapa
        cols, rows = np.meshgrid(np.arange(src.width), np.arange(src.height))
        xs, ys = src.transform * (cols, rows)
        
        # Aplicamos el modelo de calibración basado en la ubicación
        # Nota: Ajusta este umbral para que corresponda a la división entre tus zonas de costa y tierra adentro
        umbral_costa = 9050000  # Valor de ejemplo para la coordenada Y (coornorte)

        mapa_calibrado = np.zeros_like(mapa_ssi)
        
        # Aplicamos el modelo de la costa a los píxeles que cumplen la condición
        mascara_costa = (ys < umbral_costa) # Se asume que la costa está en coordenadas Y más bajas
        mapa_calibrado[mascara_costa] = pendiente_coastal * mapa_ssi[mascara_costa] + intercepto_coastal

        # Aplicamos el modelo de tierra adentro a los píxeles restantes
        mascara_tierra_adentro = (ys >= umbral_costa)
        mapa_calibrado[mascara_tierra_adentro] = pendiente_inland * mapa_ssi[mascara_tierra_adentro] + intercepto_inland

        # Mantenemos los valores de no-data como NaN
        mapa_calibrado[np.isnan(mapa_ssi)] = np.nan
        mapa_calibrado[mapa_calibrado < 0] = 0
        
    print("Mapa de SSI calibrado a µS/cm.")

    # --- 5. GUARDAR EL NUEVO MAPA CALIBRADO ---
    perfil_salida.update(dtype=rasterio.float32, count=1)

    with rasterio.open(ruta_calibrado_salida, 'w', **perfil_salida) as dst:
        dst.write(mapa_calibrado.astype(rasterio.float32), 1)

    print(f"\nMapa calibrado guardado en: {ruta_calibrado_salida}")

except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")