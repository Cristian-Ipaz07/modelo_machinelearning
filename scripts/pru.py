import os
import json
import requests
import time
from pathlib import Path
from datetime import datetime

# Configuración de rutas (mantén tus rutas actuales)
BASE_DIR = Path("F:/Programacion/DESARROLLADOR PROFESIONAL/Modelo_Predictor")
LOGOS_JSON = BASE_DIR / "data" / "json" / "logos.json"
LOGOS_DIR = BASE_DIR / "images" / "logos"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "download_log.txt"

# Configuración de descarga
DELAY_BETWEEN_DOWNLOADS = 1.5
MAX_RETRIES = 3
TIMEOUT = 15

# URLs que proporcionan logos en formato JPG/PNG directamente
LOGO_URLS = [
    # Primera opción - NBA CDN (PNG)
    "https://cdn.nba.com/logos/nba/{team_id}/primary/D/logo.png",
    
    # Segunda opción - ESPN (PNG)
    "https://a.espncdn.com/i/teamlogos/nba/500/{team_code}.png",
    
    # Tercera opción - NBA CDN alternativa (PNG)
    "https://cdn.nba.com/logos/nba/{team_id}/global/D/logo.png"
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
}

def setup_directories():
    """Crea las carpetas necesarias"""
    for directory in [LOGOS_DIR, LOG_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

def log_message(message):
    """Escribe en log y consola"""
    print(message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def download_logo(team_code, team_id):
    """Descarga el logo directamente en formato JPG/PNG"""
    for url_template in LOGO_URLS:
        try:
            url = url_template.format(team_id=team_id, team_code=team_code)
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            
            if response.status_code == 200:
                # Determinar extensión basada en Content-Type
                content_type = response.headers.get('Content-Type', '')
                extension = 'jpg' if 'jpeg' in content_type else 'png'
                
                # Guardar como JPG siempre (aunque la fuente sea PNG)
                file_path = LOGOS_DIR / f"{team_code}.jpg"
                
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                # Verificar que la imagen no esté corrupta
                if os.path.getsize(file_path) > 1024:  # Al menos 1KB
                    log_message(f"✅ {team_code}: Descargado correctamente (de {url.split('/')[2]})")
                    return True
                else:
                    os.remove(file_path)
                    log_message(f"⚠ {team_code}: Archivo vacío o corrupto")
            
        except Exception as e:
            log_message(f"⚠ {team_code}: Error con {url.split('/')[2]} - {str(e)}")
            continue
    
    log_message(f"❌ {team_code}: Todos los intentos fallaron")
    return False

def main():
    setup_directories()
    log_message("\nIniciando descarga de logos...")
    
    try:
        with open(LOGOS_JSON, 'r', encoding='utf-8') as f:
            teams_data = json.load(f)
    except Exception as e:
        log_message(f"ERROR: No se pudo cargar logos.json ({str(e)})")
        return
    
    success_count = 0
    total_teams = len(teams_data)
    
    for team_code, team_info in teams_data.items():
        if download_logo(team_code, team_info["id"]):
            success_count += 1
        time.sleep(DELAY_BETWEEN_DOWNLOADS)
    
    # Resumen final
    log_message("\n" + "="*50)
    log_message(f"Logos descargados: {success_count}/{total_teams}")
    log_message("="*50)

if __name__ == "__main__":
    main()