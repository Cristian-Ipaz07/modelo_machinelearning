import requests
import json
import os
from datetime import datetime

# Configura tu API Key
API_KEY = 'Z46Ud2TAfYs4jeaeUZF3cxoggW7ZNuhneOAdtued'  # Reemplaza con tu key real
DATE = datetime.now().strftime('%Y/%m/%d')  # Fecha actual en formato requerido por Sportradar
LANG = 'en'  # Idioma: en o es

# URL base de Sportradar para la agenda
url = f'https://api.sportradar.com/nba/trial/v8/{LANG}/games/{DATE}/schedule.json?api_key={API_KEY}'

# Solicitud a la API
response = requests.get(url)

# Verifica el código de estado
if response.status_code == 200:
    data = response.json()
    os.makedirs('../data/json', exist_ok=True)
    # Guarda los datos en JSON
    with open('../data/json/nba_schedule.json', 'w', encoding='utf-8') as f:    
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    # Imprime resumen
    games = data.get('games', [])
    print(f"Se encontraron {len(games)} partidos para el día {DATE}.\n")
    
    for game in games:
        home = game.get('home', {}).get('name', 'N/A')
        away = game.get('away', {}).get('name', 'N/A')
        scheduled = game.get('scheduled', 'N/A')
        print(f"{away} vs {home} - Hora programada: {scheduled}")
else:
    print(f"Error al obtener la agenda. Código de estado: {response.status_code}")
    print("Mensaje:", response.text)
