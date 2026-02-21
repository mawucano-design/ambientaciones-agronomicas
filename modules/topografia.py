# modules/topografia.py
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.mask import mask
from shapely.geometry import mapping
import geopandas as gpd

def generar_curvas_nivel(dem_path, geojson_path, intervalo=10):
    """
    Genera curvas de nivel dentro del polígono y devuelve la ruta de una imagen PNG.
    """
    gdf = gpd.read_file(geojson_path)
    with rasterio.open(dem_path) as src:
        if gdf.crs != src.crs:
            gdf = gdf.to_crs(src.crs)
        geom = [mapping(gdf.geometry.iloc[0])]
        out_image, out_transform = mask(src, geom, crop=True)
        elevacion = out_image[0]  # asumimos una sola banda
        # Enmascarar valores fuera del polígono (ya lo hicimos)
        elevacion = np.ma.masked_where(elevacion <= -9999, elevacion)  # valores nulos comunes

    # Crear figura con curvas de nivel
    fig, ax = plt.subplots(figsize=(10, 8))
    # Mostrar mapa de elevación
    im = ax.imshow(elevacion, cmap='terrain', extent=(
        out_transform[2], out_transform[2] + out_transform[0] * elevacion.shape[1],
        out_transform[5] + out_transform[4] * elevacion.shape[0], out_transform[5]
    ))
    # Agregar curvas de nivel
    niveles = np.arange(np.nanmin(elevacion), np.nanmax(elevacion), intervalo)
    contour = ax.contour(elevacion, levels=niveles, colors='black', linewidths=0.5,
                         extent=(
                             out_transform[2], out_transform[2] + out_transform[0] * elevacion.shape[1],
                             out_transform[5] + out_transform[4] * elevacion.shape[0], out_transform[5]
                         ))
    ax.clabel(contour, inline=True, fontsize=8)
    ax.set_title("Curvas de nivel dentro del lote")
    plt.colorbar(im, ax=ax, label='Elevación (m)')
    # Guardar imagen temporal
    img_path = "/tmp/curvas_nivel.png"  # O usar tempfile
    plt.savefig(img_path, dpi=150, bbox_inches='tight')
    plt.close()
    return img_path
