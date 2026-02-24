import streamlit as st
import tempfile
import os
from pathlib import Path
from modules import data_loader, analyzer, report_generator

st.set_page_config(page_title="Ambientación Agronómica", layout="wide")
st.title("🌱 Generador de Informes de Ambientación Agronómica")
st.markdown("Sube los archivos generados por tu plataforma para producir el informe completo.")

with st.sidebar:
    st.header("1. Archivos de entrada")
    geojson_file = st.file_uploader("GeoJSON de zonas", type=["geojson"])
    dem_file = st.file_uploader("DEM (TIFF)", type=["tif", "tiff"])
    csv_file = st.file_uploader("Tabla de fertilidad (CSV)", type=["csv"])
    png_files = st.file_uploader("Mapas adicionales (PNG)", type=["png"], accept_multiple_files=True)
    
    st.header("2. Configuración")
    cultivo = st.selectbox("Cultivo", ["maíz", "soja", "trigo"])
    
    generar_btn = st.button("Generar Informe", type="primary")

if generar_btn:
    if not geojson_file or not dem_file or not csv_file:
        st.error("Debes subir al menos el GeoJSON, el DEM y el CSV.")
    else:
        with st.spinner("Procesando información y generando informe..."):
            # Crear carpeta temporal para archivos
            with tempfile.TemporaryDirectory() as tmpdir:
                # Guardar archivos subidos
                geojson_path = Path(tmpdir) / "zonas.geojson"
                dem_path = Path(tmpdir) / "dem.tif"
                csv_path = Path(tmpdir) / "datos.csv"
                
                with open(geojson_path, "wb") as f:
                    f.write(geojson_file.getbuffer())
                with open(dem_path, "wb") as f:
                    f.write(dem_file.getbuffer())
                with open(csv_path, "wb") as f:
                    f.write(csv_file.getbuffer())
                
                # Guardar imágenes PNG
                png_paths = []
                for i, png in enumerate(png_files):
                    png_path = Path(tmpdir) / f"mapa_{i}.png"
                    with open(png_path, "wb") as f:
                        f.write(png.getbuffer())
                    png_paths.append(png_path)
                
                # Cargar datos
                gdf = data_loader.cargar_geojson(geojson_path)
                df_fert = data_loader.cargar_csv(csv_path)
                dem = data_loader.cargar_dem(dem_path)
                
                # Realizar análisis adicionales (pendientes, etc.) si es necesario
                # O simplemente usar los datos ya presentes en los archivos
                
                # Generar informe PDF
                output_pdf = Path(tmpdir) / "informe.pdf"
                report_generator.generar_informe(
                    gdf=gdf,
                    df_fert=df_fert,
                    dem=dem,
                    png_paths=png_paths,
                    cultivo=cultivo,
                    output_path=output_pdf,
                    config_path="config.yaml"
                )
                
                # Leer el PDF generado para ofrecer descarga
                with open(output_pdf, "rb") as f:
                    pdf_data = f.read()
                
                st.success("¡Informe generado con éxito!")
                st.download_button(
                    label="📥 Descargar informe PDF",
                    data=pdf_data,
                    file_name="Ambientacion_Agronomica.pdf",
                    mime="application/pdf"
                )
