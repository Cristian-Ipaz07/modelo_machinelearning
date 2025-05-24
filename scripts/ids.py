import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

def obtener_ids_jugadores():
    print("🔍 Iniciando extracción de datos...")
    url = "https://www.nba.com/players"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar el script que contiene los datos JSON
        script_tag = soup.find('script', id='__NEXT_DATA__')
        if not script_tag:
            print("❌ No se encontraron datos en la página")
            return
            
        data = json.loads(script_tag.string)
        players = data['props']['pageProps']['players']
        
        # Procesar datos
        jugadores = []
        for player in players:
            jugadores.append({
                "id": player['playerId'],
                "nombre": f"{player['playerFirstName']} {player['playerLastName']}",
                "equipo": player['teamCity'] + " " + player['teamName']
            })
        
        # Guardar en CSV
        df = pd.DataFrame(jugadores)
        df.to_csv("nba_players_2024.csv", index=False)
        print(f"✅ Datos guardados para {len(jugadores)} jugadores")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    obtener_ids_jugadores()