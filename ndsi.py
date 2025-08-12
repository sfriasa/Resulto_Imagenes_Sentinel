import rasterio
import numpy as np
import matplotlib.pyplot as plt
import os

# --- 1. CONFIGURACIÓN DE LA RUTA Y ARCHIVOS ---
ruta_carpeta = r'D:\INFORMES-PECH\2025\AGOSTO\IMAGENES\L2A_T17LQL_A004571_20250721T153200\IMG_DATA\R10m'
nombre_b4 = 'T17LQL_20250721T152721_B04_10m.tif'
nombre_b8 = 'T17LQL_20250721T152721_B08_10m.tif'
ruta_b4 = os.path.join(ruta_carpeta, nombre_b4)
ruta_b8 = os.path.join(ruta_carpeta, nombre_b8)
ruta_salida_ndsi = os.path.join(ruta_carpeta, 'NDSI_mapa.tiff')

# --- 2. LECTURA, ESCALADO Y CÁLCULO DEL ÍNDICE ---
try:
    with rasterio.open(ruta_b4) as src_b4:
        banda_b4 = src_b4.read(1).astype(float) / 10000
        perfil_b4 = src_b4.profile.copy()
    with rasterio.open(ruta_b8) as src_b8:
        banda_b8 = src_b8.read(1).astype(float) / 10000
    print("Bandas B4 y B8 leídas y escaladas correctamente.")

    denominador = banda_b8 + banda_b4
    cero_mask = (denominador == 0)
    ndsi = np.where(cero_mask, np.nan, (banda_b8 - banda_b4) / denominador)
    print("Cálculo del NDSI completado.")

    # --- 3. GUARDAR EL RESULTADO ---
    perfil_salida = perfil_b4.copy()
    perfil_salida.update(
        dtype=rasterio.float32,
        count=1,
        driver='GTiff'
    )
    with rasterio.open(ruta_salida_ndsi, 'w', **perfil_salida) as dst:
        dst.write(ndsi.astype(rasterio.float32), 1)
    print(f"El archivo NDSI se ha guardado en: {ruta_salida_ndsi}")

    # --- 4. VISUALIZACIÓN CORREGIDA ---
    plt.figure(figsize=(10, 10))
    # Cambiamos la paleta de colores para que represente mejor la salinidad
    plt.imshow(ndsi, cmap='YlOrRd', vmin=-0.2, vmax=0.4) 
    plt.colorbar(label='Índice de Salinidad Normalizado (NDSI)')
    plt.title('Mapa de NDSI (Salinidad)')
    
    ruta_salida_png = os.path.join(ruta_carpeta, 'NDSI_mapa.png')
    plt.savefig(ruta_salida_png)
    print(f"La visualización del mapa se ha guardado en: {ruta_salida_png}")
    plt.show()

except FileNotFoundError:
    print(f"Error: No se encontraron los archivos de banda. Verifica los nombres y la ruta.")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")