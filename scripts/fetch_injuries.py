import requests
import json
import os
from datetime import datetime

# Configura tu API Key
API_KEY = 'Z46Ud2TAfYs4jeaeUZF3cxoggW7ZNuhneOAdtued'
LANG = 'en'

# Fecha actual para incluir en el nombre del archivo
fecha = datetime.now().strftime('%Y-%m-%d')

# URL para lesiones de NBA
url = f'https://api.sportradar.com/nba/trial/v8/{LANG}/league/injuries.json?api_key={API_KEY}'

# Realiza la solicitud a la API
response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    # Construye ruta de salida basada en la ubicación del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.abspath(os.path.join(script_dir, '..', 'data', 'json'))
    os.makedirs(output_dir, exist_ok=True)

    # Nombre del archivo con la fecha
    file_name = f"nba_injuries_{fecha}.json"
    file_path = os.path.join(output_dir, file_name)

    # Guarda los datos en JSON
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✅ Archivo guardado en: {file_path}")
else:
    print(f"❌ Error al obtener lesiones. Código: {response.status_code}")
    print("Mensaje:", response.text[:500])
