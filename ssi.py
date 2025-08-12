import rasterio
import numpy as np
import matplotlib.pyplot as plt
import os

# --- 1. CONFIGURACIÓN DE LA RUTA Y ARCHIVOS ---

# Define la ruta de la carpeta donde se encuentran tus archivos
ruta_carpeta = r'D:\INFORMES-PECH\2025\AGOSTO\IMAGENES\L2A_T17LQL_A004571_20250721T153200\IMG_DATA\R10m'

# Nombres de los archivos de entrada
nombre_b4 = 'T17LQL_20250721T152721_B04_10m.tif'
nombre_b11 = 'T17LQL_20250721T152721_B11_10m.tif'

# Construye las rutas completas
ruta_b4 = os.path.join(ruta_carpeta, nombre_b4)
ruta_b11 = os.path.join(ruta_carpeta, nombre_b11)
ruta_salida_ssi = os.path.join(ruta_carpeta, 'SSI_final.tiff')

# --- 2. LECTURA, ESCALADO Y CÁLCULO DEL ÍNDICE ---

try:
    with rasterio.open(ruta_b4) as src_b4:
        # Leemos los datos y los convertimos a reflectancia real
        banda_b4 = src_b4.read(1).astype(float) / 10000
        perfil_b4 = src_b4.profile.copy()

    with rasterio.open(ruta_b11) as src_b11:
        # Leemos los datos y los convertimos a reflectancia real
        banda_b11 = src_b11.read(1).astype(float) / 10000
        
    print("Bandas B4 y B11 leídas y escaladas correctamente.")

    # Aplicamos la fórmula del SSI: (B4 * B11) / (B4 + B11)
    denominador_ssi = banda_b4 + banda_b11
    cero_mask_ssi = (denominador_ssi == 0)
    ssi = np.where(cero_mask_ssi, np.nan, (banda_b4 * banda_b11) / denominador_ssi)
    
    print("Cálculo del SSI completado.")

    # --- 3. GUARDAR RESULTADOS ---

    perfil_salida = perfil_b4.copy()
    perfil_salida.update(
        dtype=rasterio.float32,
        count=1,
        driver='GTiff'
    )
    
    with rasterio.open(ruta_salida_ssi, 'w', **perfil_salida) as dst:
        dst.write(ssi.astype(rasterio.float32), 1)
    print(f"El archivo SSI final se ha guardado en: {ruta_salida_ssi}")

    # --- 4. VISUALIZACIÓN ---

    plt.figure(figsize=(10, 10))
    plt.imshow(ssi, cmap='plasma', vmin=0, vmax=0.5) # Ajustamos el rango de visualización
    plt.colorbar(label='Índice de Salinidad del Suelo (SSI)')
    plt.title('Mapa SSI (Salinidad)')
    
    ruta_salida_png = os.path.join(ruta_carpeta, 'SSI_mapa.png')
    plt.savefig(ruta_salida_png)
    print(f"La visualización del mapa se ha guardado en: {ruta_salida_png}")
    plt.show()

except FileNotFoundError:
    print(f"Error: No se encontraron los archivos de banda. Verifica los nombres y la ruta.")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")