import rasterio
import numpy as np
import matplotlib.pyplot as plt
import os

# --- 1. CONFIGURACIÓN DE LA RUTA Y ARCHIVOS ---
ruta_carpeta = r'D:\INFORMES-PECH\2025\AGOSTO\IMAGENES\L2A_T17LQL_A004571_20250721T153200\IMG_DATA\R10m'

# Nombres de los archivos de entrada
nombre_b4 = 'T17LQL_20250721T152721_B04_10m.tif'  # Banda Roja
nombre_b8 = 'T17LQL_20250721T152721_B08_10m.tif'  # Banda Infrarroja Cercana (NIR)

# Construye las rutas completas
ruta_b4 = os.path.join(ruta_carpeta, nombre_b4)
ruta_b8 = os.path.join(ruta_carpeta, nombre_b8)
ruta_salida_ndvi = os.path.join(ruta_carpeta, 'NDVI_mapa.tiff')

# --- 2. LECTURA, ESCALADO Y CÁLCULO DEL ÍNDICE ---
try:
    with rasterio.open(ruta_b4) as src_b4:
        banda_b4 = src_b4.read(1).astype(float) / 10000
        perfil_b4 = src_b4.profile.copy()

    with rasterio.open(ruta_b8) as src_b8:
        banda_b8 = src_b8.read(1).astype(float) / 10000
        
    print("Bandas B4 y B8 leídas y escaladas correctamente.")

    # Aplica la fórmula del NDVI: (NIR - Rojo) / (NIR + Rojo)
    denominador_ndvi = banda_b8 + banda_b4
    cero_mask = (denominador_ndvi == 0)
    ndvi = np.where(cero_mask, np.nan, (banda_b8 - banda_b4) / denominador_ndvi)
    
    print("Cálculo del NDVI completado.")

    # --- 3. GUARDAR RESULTADO ---
    perfil_salida = perfil_b4.copy()
    perfil_salida.update(
        dtype=rasterio.float32,
        count=1,
        driver='GTiff'
    )
    
    with rasterio.open(ruta_salida_ndvi, 'w', **perfil_salida) as dst:
        dst.write(ndvi.astype(rasterio.float32), 1)
    print(f"El archivo NDVI se ha guardado en: {ruta_salida_ndvi}")

    # --- 4. VISUALIZACIÓN ---
    plt.figure(figsize=(10, 10))
    plt.imshow(ndvi, cmap='YlGn', vmin=-0.2, vmax=1.0)
    plt.colorbar(label='Índice de Vegetación (NDVI)')
    plt.title('Mapa de NDVI')
    
    ruta_salida_png = os.path.join(ruta_carpeta, 'NDVI_mapa.png')
    plt.savefig(ruta_salida_png)
    print(f"La visualización del mapa se ha guardado en: {ruta_salida_png}")
    plt.show()

except FileNotFoundError:
    print(f"Error: No se encontraron los archivos de banda. Verifica los nombres y la ruta.")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")