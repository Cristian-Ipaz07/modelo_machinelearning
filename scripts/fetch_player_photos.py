import os
import requests
import time  # Por si necesitas limitar las peticiones

API_KEY = "Z46Ud2TAfYs4jeaeUZF3cxoggW7ZNuhneOAdtued"
TEAM_ID = "583ec825-fb46-11e1-82cb-f4ce4684ea4c"  # Lakers
TEAM_PROFILE_URL = f"https://api.sportradar.us/nba/trial/v8/en/teams/{TEAM_ID}/profile.json?api_key={API_KEY}"

PHOTO_DIR = "../images/players"
os.makedirs(PHOTO_DIR, exist_ok=True)

def fetch_team_players():
    response = requests.get(TEAM_PROFILE_URL)
    if response.status_code != 200:
        print("Error al obtener jugadores:", response.status_code)
        return []

    data = response.json()
    return data.get("players", [])

def fetch_player_profile(player_id):
    url = f"https://api.sportradar.us/nba/trial/v8/en/players/{player_id}/profile.json?api_key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al obtener perfil de jugador {player_id}: {response.status_code}")
        return None

def download_image(url, filename):
    try:
        img_data = requests.get(url).content
        with open(filename, 'wb') as handler:
            handler.write(img_data)
    except Exception as e:
        print(f"Error al descargar {url}: {e}")

def main():
    players = fetch_team_players()
    print(f"Total jugadores encontrados: {len(players)}")

    count = 0
    for player in players:
        if count >= 10:
            break

        name = player.get("full_name", "unknown").replace(" ", "_")
        player_id = player.get("id")

        profile = fetch_player_profile(player_id)
        time.sleep(1)  # Retraso para evitar rate limits

        photo_url = profile.get("player", {}).get("photo_url") if profile else None

        if photo_url:
            filename = os.path.join(PHOTO_DIR, f"{name}_{player_id}.jpg")
            download_image(photo_url, filename)
            print(f"Descargada: {name}")
            count += 1
        else:
            print(f"Sin foto: {name}")

if __name__ == "__main__":
    main()
