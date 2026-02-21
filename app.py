# app.py
import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
from modules.procesamiento_raster import calcular_indices
from modules.procesamiento_vector import cargar_geojson
from modules.procesamiento_csv import analizar_csv
from modules.topografia import generar_curvas_nivel
from modules.ia_integration import generar_recomendaciones
from modules.generar_reporte import crear_docx

load_dotenv()  # Cargar variables de entorno (ej. DEEPSEEK_API_KEY)

st.set_page_config(page_title="Informes Agronómicos", layout="wide")
st.title("🌱 Plataforma de Informes Agronómicos Automatizados")

# Subida de archivos
col1, col2 = st.columns(2)
with col1:
    tiff_file = st.file_uploader("Imagen TIFF (multiespectral o DEM)", type=["tif", "tiff"])
    geojson_file = st.file_uploader("Polígono del lote (GeoJSON)", type=["geojson"])
with col2:
    csv_file = st.file_uploader("Datos de suelo/fertilidad (CSV)", type=["csv"])
    dem_file = st.file_uploader("Opcional: Modelo Digital de Elevación (DEM)", type=["tif", "tiff"])

if st.button("🚀 Generar Informe"):
    if tiff_file is None or geojson_file is None:
        st.error("Debes subir al menos la imagen TIFF y el GeoJSON.")
    else:
        with st.spinner("Procesando datos..."):
            # Crear carpeta temporal para archivos
            with tempfile.TemporaryDirectory() as tmpdirname:
                # Guardar archivos subidos
                tiff_path = os.path.join(tmpdirname, "image.tif")
                with open(tiff_path, "wb") as f:
                    f.write(tiff_file.getbuffer())

                geojson_path = os.path.join(tmpdirname, "lote.geojson")
                with open(geojson_path, "wb") as f:
                    f.write(geojson_file.getbuffer())

                csv_path = None
                if csv_file:
                    csv_path = os.path.join(tmpdirname, "data.csv")
                    with open(csv_path, "wb") as f:
                        f.write(csv_file.getbuffer())

                dem_path = None
                if dem_file:
                    dem_path = os.path.join(tmpdirname, "dem.tif")
                    with open(dem_path, "wb") as f:
                        f.write(dem_file.getbuffer())

                # 1. Procesar raster (calcular NDVI, NDWI)
                with st.status("📡 Calculando índices espectrales..."):
                    indices = calcular_indices(tiff_path, geojson_path)
                    st.write("NDVI promedio:", indices.get("ndvi_mean"))
                    st.write("NDWI promedio:", indices.get("ndwi_mean"))

                # 2. Cargar GeoJSON (para superficie, etc.)
                gdf = cargar_geojson(geojson_path)
                area_ha = gdf.to_crs("EPSG:32719").area.sum() / 10000  # Área en hectáreas (asumiendo proyección adecuada)
                st.write(f"Área del lote: {area_ha:.2f} ha")

                # 3. Procesar CSV si se subió
                datos_suelo = {}
                if csv_path:
                    with st.status("🧪 Analizando datos de suelo..."):
                        datos_suelo = analizar_csv(csv_path)
                        st.write("pH promedio:", datos_suelo.get("ph_mean"))
                        st.write("Materia orgánica (%):", datos_suelo.get("mo_mean"))

                # 4. Topografía (si hay DEM)
                curvas = None
                if dem_path:
                    with st.status("🗺️ Generando curvas de nivel..."):
                        curvas = generar_curvas_nivel(dem_path, geojson_path)

                # 5. Generar recomendaciones con IA
                with st.status("🤖 Consultando DeepSeek..."):
                    prompt_data = {
                        "area": area_ha,
                        "ndvi_mean": indices.get("ndvi_mean"),
                        "ndwi_mean": indices.get("ndwi_mean"),
                        "datos_suelo": datos_suelo,
                        "tiene_dem": dem_path is not None
                    }
                    recomendaciones = generar_recomendaciones(prompt_data)

                # 6. Crear documento .docx
                with st.status("📄 Generando informe..."):
                    doc_path = os.path.join(tmpdirname, "informe.docx")
                    crear_docx(doc_path, indices, gdf, datos_suelo, curvas, recomendaciones)

                # Ofrecer descarga
                with open(doc_path, "rb") as f:
                    st.download_button("📥 Descargar Informe", f, file_name="informe_agronomico.docx")

        st.success("¡Informe generado con éxito!")
