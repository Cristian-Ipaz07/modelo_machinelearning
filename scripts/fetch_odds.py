### 🎲 Script: fetch_odds.py – Obtener cuotas de apuestas de la NBA (hoy)
import os
import requests
import json
import csv
from datetime import datetime

API_KEY = "Z46Ud2TAfYs4jeaeUZF3cxoggW7ZNuhneOAdtued"
DATE = datetime.now().strftime("%Y/%m/%d")
URL = f"https://api.sportradar.us/oddscomparison/trial/v4/en/sports/basketball/league/nba/schedule/{DATE}/odds.json?api_key={API_KEY}"

OUTPUT_JSON = "../data/json/nba_odds.json"
OUTPUT_CSV = "../data/csv/nba_odds.csv"

os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

def fetch_odds():
    res = requests.get(URL)
    if res.status_code != 200:
        print(f"Error al obtener cuotas: {res.status_code}")
        return None
    return res.json()

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
"""
def save_csv(data, path):
    rows = []
    for event in data.get("sport_events", []):
        event_info = {
            "match": f"{event['competitors'][0]['name']} vs {event['competitors'][1]['name']}",
            "start_time": event.get("start_time"),
        }
        bookmakers = event.get("bookmakers", [])
        for bookmaker in bookmakers:
            event_info[f"{bookmaker['name']}_moneyline_home"] = bookmaker["markets"][0]["outcomes"][0]["odds"]
            event_info[f"{bookmaker['name']}_moneyline_away"] = bookmaker["markets"][0]["outcomes"][1]["odds"]
        rows.append(event_info)

    keys = rows[0].keys() if rows else []
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
"""
def main():
    data = fetch_odds()
    if data:
        save_json(data, OUTPUT_JSON)
        """
        save_csv(data, OUTPUT_CSV)
        """
        print("✅ Cuotas guardadas correctamente.")
        

if __name__ == "__main__":
    main()
