import os
os.environ['PROJ_DATA'] = r'C:\Users\Sfriasa.CHAVIMOCHIC\AppData\Local\Programs\Python\Python313\Lib\site-packages\rasterio\proj_data'

import folium
import rasterio
from rasterio.warp import transform
import numpy as np
import base64
from io import BytesIO
from PIL import Image

# --- 1. CONFIGURACIÓN DE LA RUTA Y ARCHIVOS ---
ruta_carpeta = r'D:\INFORMES-PECH\2025\AGOSTO\IMAGENES\L2A_T17LQL_A004571_20250721T153200\IMG_DATA\R10m'
nombre_ssi_mapa_utm = 'SSI_final.tiff'
ruta_ssi_mapa_utm = os.path.join(ruta_carpeta, nombre_ssi_mapa_utm)

ruta_salida_mapa = os.path.join(ruta_carpeta, 'mapa_interactivo_SSI_final.html')

# --- 2. PREPARACIÓN DE DATOS Y CONVERSIÓN DE COORDENADAS ---
try:
    with rasterio.open(ruta_ssi_mapa_utm) as src:
        data = src.read(1)
        
        # --- LÍNEAS CORREGIDAS ---
        # Definimos las proyecciones usando el nuevo formato
        src_proj_crs = src.crs
        dst_proj_crs = 'EPSG:4326' # WGS84
        
        # Transformamos las coordenadas de las esquinas. Ahora pasamos las coordenadas como listas
        xs = [src.bounds.left, src.bounds.right]
        ys = [src.bounds.bottom, src.bounds.top]
        
        lon, lat = transform(src_proj_crs, dst_proj_crs, xs, ys)
        
        lon_min, lon_max = lon[0], lon[1]
        lat_min, lat_max = lat[0], lat[1]

        # --- FIN DE LÍNEAS CORREGIDAS ---
        
        bounds_wgs84 = [[lat_min, lon_min], [lat_max, lon_max]]
        
        centro_lat = (lat_min + lat_max) / 2
        centro_lon = (lon_min + lon_max) / 2

        min_val, max_val = np.nanmin(data), np.nanmax(data)
        normalized_data = (data - min_val) / (max_val - min_val) * 255
        img = Image.fromarray(normalized_data.astype(np.uint8), mode='L')
        
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        encoded_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
        image_uri = f'data:image/png;base64,{encoded_img}'

    # --- 3. CREACIÓN Y GUARDADO DEL MAPA ---
    mapa_folium = folium.Map(
        location=[centro_lat, centro_lon],
        zoom_start=6,
        control_scale=True
    )
    
    folium.raster_layers.ImageOverlay(
        image=image_uri,
        bounds=bounds_wgs84,
        opacity=0.8,
        name='Mapa de SSI'
    ).add_to(mapa_folium)
    
    folium.LayerControl().add_to(mapa_folium)

    mapa_folium.save(ruta_salida_mapa)
    
    print(f"El mapa interactivo se ha creado correctamente en: {ruta_salida_mapa}")

except FileNotFoundError:
    print(f"Error: No se encontró el archivo '{nombre_ssi_mapa_utm}'.")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")