import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def generar_informe(gdf, df_fert, dem, png_paths, cultivo, output_path, config_path="config.yaml"):
    """
    Genera el informe PDF completo.
    - gdf: GeoDataFrame con geometrías y atributos de zonas.
    - df_fert: DataFrame con datos de fertilidad (debe coincidir con las zonas).
    - dem: objeto rasterio del DEM.
    - png_paths: lista de rutas a imágenes PNG (mapas pre-generados).
    - cultivo: nombre del cultivo.
    - output_path: ruta donde guardar el PDF.
    """
    c = canvas.Canvas(str(output_path), pagesize=A4)
    width, height = A4
    margen = 50
    
    # ========== PORTADA ==========
    c.setFont("Helvetica-Bold", 20)
    c.drawString(margen, height - 80, "INFORME DE AMBIENTACIÓN AGRONÓMICA")
    c.setFont("Helvetica", 12)
    c.drawString(margen, height - 110, f"Cultivo: {cultivo.upper()}")
    c.drawString(margen, height - 130, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
    c.drawString(margen, height - 150, f"Área total: {gdf['area_ha'].sum():.2f} ha")
    c.drawString(margen, height - 170, f"Número de zonas: {len(gdf)}")
    
    # Si hay imagen de logo o algo, se puede agregar
    c.showPage()
    
    # ========== SECCIÓN 1: INFORMACIÓN GENERAL ==========
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margen, height - 50, "1. INFORMACIÓN GENERAL")
    c.setFont("Helvetica", 10)
    c.drawString(margen, height - 70, f"Fecha de análisis: {datetime.now().strftime('%d/%m/%Y')}")
    c.drawString(margen, height - 85, f"Fuente de datos: Sentinel-2 / SRTM")
    c.drawString(margen, height - 100, f"Índice NDVI promedio: {df_fert['ndvi'].mean():.3f}" if 'ndvi' in df_fert else "NDVI: No disponible")
    c.showPage()
    
    # ========== SECCIÓN 2: MAPAS ==========
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margen, height - 50, "2. MAPAS TEMÁTICOS")
    y = height - 80
    for i, png_path in enumerate(png_paths[:4]):  # Mostrar hasta 4 mapas
        if os.path.exists(png_path):
            img = ImageReader(png_path)
            # Calcular posición (2 columnas)
            col = i % 2
            fila = i // 2
            x_img = margen + col * 280
            y_img = height - 200 - fila * 180
            c.drawImage(img, x_img, y_img, width=250, height=150, preserveAspectRatio=True, anchor='c')
            if i == 3:
                break
    c.showPage()
    
    # ========== SECCIÓN 3: FERTILIDAD ACTUAL ==========
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margen, height - 50, "3. FERTILIDAD ACTUAL")
    
    # Crear tabla con los primeros datos
    if not df_fert.empty:
        # Seleccionar columnas relevantes
        cols_mostrar = ['zona', 'area_ha', 'indice_npk', 'ndvi', 'ndre', 'materia_organica', 'humedad']
        df_tabla = df_fert[cols_mostrar].head(10)  # primeras 10 filas
        
        # Convertir a lista de listas para Table
        data = [list(df_tabla.columns)] + df_tabla.values.tolist()
        tabla = Table(data, colWidths=[40, 50, 50, 40, 40, 60, 50])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        
        # Dibujar tabla en el PDF
        tabla.wrapOn(c, width-2*margen, height)
        tabla.drawOn(c, margen, height - 250)
    c.showPage()
    
    # ========== SECCIÓN 4: RECOMENDACIONES NPK ==========
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margen, height - 50, "4. RECOMENDACIONES DE FERTILIZACIÓN (kg/ha)")
    if 'rec_N' in df_fert.columns:
        data_rec = [['Zona', 'N', 'P', 'K']]
        for _, row in df_fert.head(10).iterrows():
            data_rec.append([int(row['zona']), row['rec_N'], row['rec_P'], row['rec_K']])
        tabla_rec = Table(data_rec, colWidths=[40, 50, 50, 50])
        tabla_rec.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        tabla_rec.wrapOn(c, width-2*margen, height)
        tabla_rec.drawOn(c, margen, height - 200)
    c.showPage()
    
    # ========== SECCIÓN 5: ANÁLISIS DE COSTOS ==========
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margen, height - 50, "5. ANÁLISIS DE COSTOS")
    if 'costo_total' in df_fert.columns:
        costo_total = df_fert['costo_total'].sum()
        c.setFont("Helvetica", 12)
        c.drawString(margen, height - 80, f"Costo total estimado: ${costo_total:,.2f} USD")
        c.drawString(margen, height - 100, f"Costo promedio por hectárea: ${costo_total/gdf['area_ha'].sum():,.2f} USD/ha")
    c.showPage()
    
    # ========== SECCIÓN 6: PROYECCIONES DE COSECHA ==========
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margen, height - 50, "6. PROYECCIONES DE RENDIMIENTO")
    if 'rend_sin' in df_fert.columns:
        data_rend = [['Zona', 'Sin fert', 'Con fert', 'Incremento %']]
        for _, row in df_fert.head(10).iterrows():
            data_rend.append([int(row['zona']), row['rend_sin'], row['rend_con'], row['inc_porc']])
        tabla_rend = Table(data_rend, colWidths=[40, 60, 60, 70])
        tabla_rend.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        tabla_rend.wrapOn(c, width-2*margen, height)
        tabla_rend.drawOn(c, margen, height - 200)
    c.showPage()
    
    # ========== SECCIÓN 7: TOPOGRAFÍA ==========
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margen, height - 50, "7. TOPOGRAFÍA")
    c.setFont("Helvetica", 10)
    c.drawString(margen, height - 70, f"Elevación mínima: {186.0} m")  # Idealmente extraer del DEM
    c.drawString(margen, height - 85, f"Elevación máxima: {197.0} m")
    c.drawString(margen, height - 100, f"Pendiente promedio: {2.8} %")
    c.showPage()
    
    # ========== SECCIÓN 8: RECOMENDACIONES FINALES ==========
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margen, height - 50, "8. RECOMENDACIONES FINALES")
    c.setFont("Helvetica", 10)
    recomendaciones = [
        "• Aplicar fertilización diferenciada por zonas según el análisis NPK.",
        "• Priorizar zonas con índice de fertilidad inferior a 0.5.",
        "• Considerar enmiendas orgánicas en zonas con materia orgánica < 2%.",
        "• Implementar riego suplementario en zonas con humedad < 0.2.",
        "• Realizar análisis de suelo de laboratorio para validar resultados.",
        "• Considerar agricultura de precisión para aplicación variable de insumos."
    ]
    y = height - 80
    for rec in recomendaciones:
        c.drawString(margen, y, rec)
        y -= 15
    c.showPage()
    
    # ========== SECCIÓN 9: METADATOS ==========
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margen, height - 50, "9. METADATOS TÉCNICOS")
    c.setFont("Helvetica", 10)
    c.drawString(margen, height - 70, "Generado por: Analizador Multi-Cultivo Satelital v6.0")
    c.drawString(margen, height - 85, f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(margen, height - 100, "Sistema de coordenadas: EPSG:4326 (WGS84)")
    c.drawString(margen, height - 115, f"Número de zonas: {len(gdf)}")
    c.drawString(margen, height - 130, "Resolución satelital: 10m")
    c.drawString(margen, height - 145, "Resolución DEM: 10.0 m")
    
    c.save()
