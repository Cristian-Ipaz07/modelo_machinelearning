import os
import json
import requests
import time
from datetime import datetime

# Configuración
API_KEY = "24bd3cf8-ae40-44c3-beb1-6fbf324f41f0"  # Tu API key
API_BASE = "https://api.balldontlie.io/v1"
OUTPUT_DIR = "data/json"
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "players_by_team.json")
os.makedirs(OUTPUT_DIR, exist_ok=True)

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

def obtener_equipos():
    """Obtiene todos los equipos con manejo de errores"""
    print("📋 Obteniendo lista de equipos...")
    try:
        response = requests.get(f"{API_BASE}/teams", headers=headers, timeout=10)
        response.raise_for_status()  # Lanza error para códigos HTTP 4XX/5XX
        return response.json()["data"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener equipos: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"Código HTTP: {e.response.status_code}")
            print(f"Respuesta: {e.response.text[:200]}...")  # Muestra solo parte del error
        exit()

def obtener_jugadores_equipo(team_id, team_name):
    """Obtiene todos los jugadores de un equipo con paginación"""
    jugadores = []
    page = 1
    total_pages = 1
    
    while page <= total_pages:
        try:
            url = f"{API_BASE}/players?team_ids[]={team_id}&per_page=100&page={page}"
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            jugadores.extend(data["data"])
            
            # Actualizar total de páginas
            meta = data.get("meta", {})
            total_pages = meta.get("total_pages", 1)
            
            print(f"   → Página {page}/{total_pages} - {len(data['data'])} jugadores")
            page += 1
            time.sleep(1.2)  # Respeta el rate limiting (1.2 segundos entre requests)
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error en página {page}: {str(e)}")
            if page < total_pages:
                print("Reintentando en 5 segundos...")
                time.sleep(5)
            else:
                break
    
    return jugadores

def generar_json():
    equipos = obtener_equipos()
    all_teams_data = []
    
    print(f"\n🏀 Procesando {len(equipos)} equipos:")
    for i, team in enumerate(equipos, 1):
        print(f"\n[{i}/{len(equipos)}] 🔍 {team['full_name']} (ID: {team['id']})")
        
        team_data = {
            "id": team["id"],
            "name": team["full_name"],
            "abbreviation": team["abbreviation"],
            "players": []
        }
        
        jugadores = obtener_jugadores_equipo(team["id"], team["full_name"])
        for player in jugadores:
            team_data["players"].append({
                "id": player["id"],
                "first_name": player["first_name"],
                "last_name": player["last_name"]
            })
        
        print(f"   ✅ {len(jugadores)} jugadores encontrados")
        all_teams_data.append(team_data)
    
    # Guardar con metadatos
    resultado = {
        "fecha_actualizacion": datetime.now().isoformat(),
        "total_equipos": len(all_teams_data),
        "total_jugadores": sum(len(t["players"]) for t in all_teams_data),
        "data": all_teams_data
    }
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ JSON generado en: {OUTPUT_PATH}")
    print(f"   Equipos: {len(all_teams_data)}")
    print(f"   Jugadores totales: {resultado['total_jugadores']}")

if __name__ == "__main__":
    generar_json()