# modules/procesamiento_csv.py
import pandas as pd

def analizar_csv(csv_path):
    df = pd.read_csv(csv_path)
    # Mapeo de nombres de columna comunes a un estándar
    resultados = {}
    if 'pH' in df.columns:
        resultados['ph_mean'] = df['pH'].mean()
    if 'MO' in df.columns or 'Materia_Organica' in df.columns:
        col_mo = 'MO' if 'MO' in df.columns else 'Materia_Organica'
        resultados['mo_mean'] = df[col_mo].mean()
    if 'P' in df.columns:
        resultados['p_mean'] = df['P'].mean()
    if 'K' in df.columns:
        resultados['k_mean'] = df['K'].mean()
    # Agregar más según necesidades
    return resultados
