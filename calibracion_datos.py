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
ruta_ssi_mapa = r'D:\INFORMES-PECH\2025\AGOSTO\IMAGENES\L2A_T17LQL_A004571_20250721T153200\IMG_DATA\R10m\SSI_final.tiff'
ruta_calibrado_salida = os.path.join(os.path.dirname(ruta_ssi_mapa), 'SSI_calibrado_uScm.tiff')

# --- 2. LEER Y PREPARAR DATOS DE CAMPO ---
print("Leyendo datos de campo desde el archivo de Excel...")
try:
    df_calibracion = pd.read_excel(ruta_excel)
    
    # 2.1. Limpiamos cualquier fila con valores faltantes
    df_calibracion.dropna(subset=[columna_x, columna_y, columna_conductividad], inplace=True)
    
    x_coords = df_calibracion[columna_x].tolist()
    y_coords = df_calibracion[columna_y].tolist()
    conductividad_medida = df_calibracion[columna_conductividad].tolist()
    
    print(f"Datos de Excel leídos y limpiados. {len(x_coords)} puntos de muestra válidos.")

except FileNotFoundError:
    print(f"Error: No se encontró el archivo de Excel en la ruta '{ruta_excel}'.")
    exit()
except KeyError as e:
    print(f"Error: No se encontró la columna {e} en el archivo de Excel.")
    exit()

# --- 3. EXTRAER VALORES DEL MAPA SSI EN CADA PUNTO ---
try:
    with rasterio.open(ruta_ssi_mapa) as src:
        # Creamos una lista de tuplas con las coordenadas (x, y)
        coordenadas_muestreo = list(zip(x_coords, y_coords))
        
        # Extraemos los valores de píxeles
        valores_ssi_muestra = [value[0] for value in src.sample(coordenadas_muestreo)]
        
    # Aseguramos que los valores sean un array de numpy
    valores_ssi_muestra = np.array(valores_ssi_muestra)
    print(f"Se extrajeron {len(valores_ssi_muestra)} valores del mapa SSI.")

except FileNotFoundError:
    print(f"Error: No se encontró el mapa SSI en la ruta '{ruta_ssi_mapa}'.")
    exit()
except Exception as e:
    print(f"Ocurrió un error al extraer los valores del mapa SSI: {e}")
    exit()

# --- 4. CONSTRUIR Y ENTRENAR EL MODELO ---
X = valores_ssi_muestra.reshape(-1, 1)
y = np.array(conductividad_medida)

# Filtramos los valores que no sean válidos para el modelo (como NaN)
mascara_valida = ~np.isnan(X).flatten()
X_limpio = X[mascara_valida]
y_limpio = y[mascara_valida]

modelo = LinearRegression()
modelo.fit(X_limpio, y_limpio)

pendiente = modelo.coef_[0]
intercepto = modelo.intercept_

print("\n--- Modelo de Calibración ---")
print(f"Ecuación del modelo: Conductividad = {pendiente:.2f} * SSI + {intercepto:.2f}")
print(f"Coeficiente de determinación (R²): {modelo.score(X_limpio, y_limpio):.2f}")

# --- 5. ABRIR EL MAPA SSI Y APLICAR EL MODELO ---
try:
    with rasterio.open(ruta_ssi_mapa) as src:
        mapa_ssi = src.read(1).astype(float)
        perfil_salida = src.profile.copy()
        
    mapa_calibrado = np.where(np.isnan(mapa_ssi), np.nan, pendiente * mapa_ssi + intercepto)
    
    mapa_calibrado[mapa_calibrado < 0] = 0
    print("Mapa de SSI calibrado a µS/cm.")

    # --- 6. GUARDAR EL NUEVO MAPA CALIBRADO ---
    perfil_salida.update(dtype=rasterio.float32, count=1)

    with rasterio.open(ruta_calibrado_salida, 'w', **perfil_salida) as dst:
        dst.write(mapa_calibrado.astype(rasterio.float32), 1)

    print(f"\nMapa calibrado guardado en: {ruta_calibrado_salida}")

except FileNotFoundError:
    print(f"Error: No se encontró el mapa SSI en la ruta '{ruta_ssi_mapa}'.")
    exit()
except Exception as e:
    print(f"Ocurrió un error inesperado al guardar el mapa calibrado: {e}")