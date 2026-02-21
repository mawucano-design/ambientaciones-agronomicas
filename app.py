# app.py
import streamlit as st
from procesamiento import calcular_ndvi, cargar_geojson
from ia import generar_recomendaciones
from reporte import crear_docx
import tempfile
import os

st.title("Plataforma de Informes Agronómicos")

# Subida de archivos
archivo_tiff = st.file_uploader("Sube imagen TIFF (con bandas)", type=['tif', 'tiff'])
archivo_geojson = st.file_uploader("Sube polígono del lote (GeoJSON)", type=['geojson'])
archivo_csv = st.file_uploader("Sube datos de suelo/fertilidad (CSV)", type=['csv'])

if st.button("Generar informe"):
    with st.spinner("Procesando..."):
        # Guardar archivos temporales
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tif') as tmp_tiff:
            tmp_tiff.write(archivo_tiff.read())
            path_tiff = tmp_tiff.name

        # Procesar
        ndvi_mean = calcular_ndvi(path_tiff)
        gdf = cargar_geojson(archivo_geojson)

        # Llamar a IA
        recomendaciones = generar_recomendaciones(ndvi_mean, otros_datos)

        # Crear documento
        doc = crear_docx(ndvi_mean, gdf, recomendaciones)
        doc_path = "informe.docx"
        doc.save(doc_path)

        # Descargar
        with open(doc_path, "rb") as f:
            st.download_button("Descargar informe", f, file_name="informe.docx")

        # Limpiar
        os.unlink(path_tiff)
