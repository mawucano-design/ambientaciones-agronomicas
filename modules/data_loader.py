import geopandas as gpd
import pandas as pd
import rasterio

def cargar_geojson(path):
    """Carga el GeoJSON de zonas."""
    return gpd.read_file(path)

def cargar_csv(path):
    """Carga la tabla de fertilidad (debe incluir columnas como zona, npk, etc.)."""
    return pd.read_csv(path)

def cargar_dem(path):
    """Carga el modelo digital de elevación."""
    return rasterio.open(path)
