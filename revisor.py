import rasterio
import os
import glob

# --- CONFIGURACIÓN DE LA RUTA ---
ruta_carpeta = r'D:\INFORMES-PECH\2025\AGOSTO\IMAGENES\L2A_T17LQL_A004571_20250721T153200\IMG_DATA\R10m'

# --- PROCESO DE VERIFICACIÓN ---
archivos_tiff = glob.glob(os.path.join(ruta_carpeta, '*.tif'))

if not archivos_tiff:
    print("Error: No se encontraron archivos .tiff en la ruta especificada.")
    exit()

print(f"Se encontraron {len(archivos_tiff)} archivos GeoTIFF para verificar.")
print("---")

for archivo in archivos_tiff:
    try:
        with rasterio.open(archivo) as src:
            nombre_archivo = os.path.basename(archivo)
            
            # --- LÍNEAS CORREGIDAS ---
            crs = src.crs.to_string() if src.crs else "CRS no encontrado"
            resolucion_x = src.transform.a  # Forma correcta de obtener la resolución en X
            resolucion_y = -src.transform.e # Forma correcta de obtener la resolución en Y
            # --- FIN DE LÍNEAS CORREGIDAS ---
            
            ancho = src.width
            alto = src.height
            tipo_dato = src.profile['dtype']
            
            print(f"Archivo: {nombre_archivo}")
            print(f"  - Sistema de Referencia de Coordenadas (CRS): {crs}")
            print(f"  - Resolución Espacial (Tamaño del píxel): {resolucion_x} x {resolucion_y} metros")
            print(f"  - Dimensiones (ancho x alto): {ancho} x {alto} píxeles")
            print(f"  - Tipo de Dato (dtype): {tipo_dato}")
            print("---")

    except rasterio.errors.RasterioIOError as e:
        print(f"Error al leer el archivo '{os.path.basename(archivo)}': {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado con el archivo '{os.path.basename(archivo)}': {e}")