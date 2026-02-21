# modules/ia_integration.py
import os
import requests
import json

def generar_recomendaciones(datos):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return "Error: No se encontró la clave de API de DeepSeek."

    # Construir prompt
    prompt = f"""
    Eres un asesor agronómico experto. Basado en los siguientes datos de un lote agrícola, genera un análisis y recomendaciones para el manejo del cultivo o sistema ganadero más adecuado.

    Datos del lote:
    - Área: {datos['area']:.2f} hectáreas.
    - NDVI promedio: {datos['ndvi_mean']:.3f} (indica vigor vegetativo; valores altos >0.6 son buenos).
    - NDWI promedio: {datos['ndwi_mean']:.3f} (indica contenido de agua; valores >0 suelen indicar humedad).
    - Datos de suelo: pH promedio = {datos['datos_suelo'].get('ph_mean', 'N/A')}, Materia orgánica (%) = {datos['datos_suelo'].get('mo_mean', 'N/A')}, Fósforo = {datos['datos_suelo'].get('p_mean', 'N/A')}, Potasio = {datos['datos_suelo'].get('k_mean', 'N/A')}.
    - ¿Se tiene topografía? {'Sí' if datos['tiene_dem'] else 'No'}. (Si hay topografía, considerar pendiente para recomendaciones de conservación de suelo).

    Con base en estos datos, responde lo siguiente:
    1. Interpretación de los índices espectrales y su relación con el estado del cultivo/vegetación.
    2. Recomendaciones de cultivos agrícolas que se adaptarían mejor a estas condiciones (considerando clima templado, si no hay datos asumir templado).
    3. Si se trata de ganadería, ¿qué sistema sería el más adecuado? (pastoreo rotativo, silvopastoril, estabulado, etc.) y por qué.
    4. Prácticas agroecológicas recomendadas (manejo de suelo, fertilización, riego, conservación).
    5. Cualquier otra observación relevante.

    Por favor, estructura la respuesta en párrafos claros y evita lenguaje técnico excesivo, pero sin perder precisión.
    """

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",  # o el modelo que uses
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        return f"Error al consultar la IA: {str(e)}"
