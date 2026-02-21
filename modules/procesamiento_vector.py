# modules/procesamiento_vector.py
import geopandas as gpd

def cargar_geojson(path):
    gdf = gpd.read_file(path)
    # Validar que sea polígono
    if not gdf.geometry.type.isin(['Polygon', 'MultiPolygon']).all():
        raise ValueError("El archivo debe contener polígonos o multipolígonos.")
    return gdf
