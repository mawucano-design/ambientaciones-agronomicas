# modules/procesamiento_raster.py
import rasterio
import numpy as np
from rasterio.mask import mask
from shapely.geometry import mapping

def calcular_indices(tiff_path, geojson_path):
    """
    Calcula NDVI y NDWI promedio dentro del polígono.
    Asume:
        Banda 1: Rojo
        Banda 2: NIR
        Banda 3: Verde
    """
    import geopandas as gpd
    gdf = gpd.read_file(geojson_path)
    # Asegurar que el CRS del raster y el polígono coincidan
    with rasterio.open(tiff_path) as src:
        # Reproyectar polígono al CRS del raster si es necesario
        if gdf.crs != src.crs:
            gdf = gdf.to_crs(src.crs)
        geom = [mapping(gdf.geometry.iloc[0])]

        # Recortar raster al polígono
        out_image, out_transform = mask(src, geom, crop=True)
        # out_image tiene forma (bandas, filas, columnas)

        # Extraer bandas (asumimos orden: 1=Rojo, 2=NIR, 3=Verde)
        red = out_image[0].astype(float)
        nir = out_image[1].astype(float)
        green = out_image[2].astype(float)

        # Enmascarar valores nulos o cero
        mask_val = (red > 0) & (nir > 0) & (green > 0)

        # NDVI = (NIR - Rojo) / (NIR + Rojo)
        ndvi = np.where(mask_val, (nir - red) / (nir + red + 1e-10), np.nan)
        ndvi_mean = np.nanmean(ndvi)

        # NDWI = (Verde - NIR) / (Verde + NIR) (versión común)
        ndwi = np.where(mask_val, (green - nir) / (green + nir + 1e-10), np.nan)
        ndwi_mean = np.nanmean(ndwi)

    return {"ndvi_mean": ndvi_mean, "ndwi_mean": ndwi_mean, "ndvi_array": ndvi, "ndwi_array": ndwi}
