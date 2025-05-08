import os
import requests
import json
from datetime import datetime

API_KEY = "Z46Ud2TAfYs4jeaeUZF3cxoggW7ZNuhneOAdtued"
TODAY = datetime.now()
DATE_STR = TODAY.strftime("%Y/%m/%d")
PRETTY_DATE = TODAY.strftime("%d/%m/%Y")

SCHEDULE_URL = f"https://api.sportradar.us/nba/trial/v8/en/games/{DATE_STR}/schedule.json?api_key={API_KEY}"

# Ruta única de salida (no múltiples archivos)
OUTPUT_JSON = "../data/json/nba_lineups.json"
os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)

def fetch_schedule():
    res = requests.get(SCHEDULE_URL)
    if res.status_code != 200:
        print(f"❌ Error al obtener calendario: {res.status_code}")
        return []
    return res.json().get("games", [])

def save_json(data, path):
    """Guarda los datos en un archivo JSON (sobrescribe)"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def main():
    games = fetch_schedule()
    if not games:
        print("⚠️ No hay partidos programados hoy.")
        return

    # Guardar en un solo archivo que se sobrescribe
    save_json(games, OUTPUT_JSON)

    print(f"\n✅ Alineaciones de hoy ({PRETTY_DATE}) - Guardado en {OUTPUT_JSON}")
    print("-" * 40)

    for game in games:
        home = game['home']['name']
        away = game['away']['name']
        print(f"{away} vs {home}")

if __name__ == "__main__":
    main()
