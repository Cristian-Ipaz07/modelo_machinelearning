import os
import json
import requests
import time
from unidecode import unidecode
from datetime import datetime
from pathlib import Path

# Configuración de rutas
BASE_DIR = Path("F:/Programacion/DESARROLLADOR PROFESIONAL/Modelo_Predictor")
PLAYERS_JSON = BASE_DIR / "data" / "json" / "json.json"
LOGOS_JSON = BASE_DIR / "data" / "json" / "logos.json"
IMAGES_DIR = BASE_DIR / "images"
PLAYERS_DIR = IMAGES_DIR / "players"
LOGOS_DIR = IMAGES_DIR / "logos"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "download_log.txt"

# Configuración de descarga
DELAY_BETWEEN_PLAYERS = 1.5
DELAY_BETWEEN_TEAMS = 3
MAX_RETRIES = 3
TIMEOUT = 15

# URLs para logos (mejoradas con múltiples fuentes)
LOGO_URLS = [
    # Primera opción - NBA CDN (PNG)
    "https://cdn.nba.com/logos/nba/{team_id}/primary/D/logo.png",
    
    # Segunda opción - ESPN (PNG)
    "https://a.espncdn.com/i/teamlogos/nba/500/{team_code}.png",
    
    # Tercera opción - NBA CDN alternativa (PNG)
    "https://cdn.nba.com/logos/nba/{team_id}/global/D/logo.png",
    
    # URL especial para New Orleans Pelicans (NOP)
    "https://cdn.nba.com/logos/nba/{team_id}/global/L/logo.svg"
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    'Referer': 'https://www.nba.com/'
}

# Configuración de filtros
EQUIPOS_A_DESCARGAR = ["DEN"]  # Ejemplo: ["LAL", "GSW"]
EQUIPOS_A_EXCLUIR = []    # Equipos a omitir

DESCARGAR_SOLO_LOGOS = False  # Cambiar a False para descargar jugadores también
EXCLUIR_TODOS_EQUIPOS = False # Cambiar a True para excluir todos los equipos inicialmente

# Contadores globales
total_jugadores = 0
jugadores_descargados = 0
jugadores_fallidos = 0
equipos_procesados = 0
logos_descargados = 0

def setup_directories():
    """Crea las carpetas necesarias"""
    for directory in [PLAYERS_DIR, LOGOS_DIR, LOG_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

def setup_logging():
    """Configura el sistema de logging"""
    try:
        if not LOG_FILE.exists():
            LOG_FILE.touch()
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n\n=== Nueva ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        return True
    except Exception as e:
        print(f"AVISO: No se pudo configurar logging ({e})")
        return False

def log_message(message, log_active=True):
    """Escribe en log y consola"""
    print(message)
    if log_active:
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
        except:
            pass

def descargar_logo(equipo_abrev, logos_data):
    """Descarga el logo con manejo especial para NOP y múltiples fuentes"""
    global logos_descargados
    
    if equipo_abrev not in logos_data:
        log_message(f"❌ Equipo no encontrado: {equipo_abrev}", True)
        return False

    team_id = logos_data[equipo_abrev]["id"]
    
    # Manejo especial para New Orleans Pelicans (NOP)
    if equipo_abrev == "NOP":
        nop_url = "https://cdn.nba.com/logos/nba/1610612740/global/L/logo.svg"
        try:
            response = requests.get(nop_url, headers=HEADERS, timeout=TIMEOUT)
            if response.status_code == 200:
                with open(LOGOS_DIR / "NOP.png", 'wb') as f:
                    # Convertimos SVG a PNG directamente en memoria
                    import cairosvg
                    from io import BytesIO
                    png_data = cairosvg.svg2png(bytestring=response.content)
                    f.write(png_data)
                logos_descargados += 1
                log_message("✅ NOP: Logo descargado y convertido a PNG", True)
                return True
        except Exception as e:
            log_message(f"⚠️ NOP: Error con URL especial - {str(e)}", True)

    # Proceso normal para otros equipos
    for url_template in LOGO_URLS:
        try:
            url = url_template.format(team_id=team_id, team_code=equipo_abrev)
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            
            if response.status_code == 200:
                # Forzamos extensión .png para todos los logos
                with open(LOGOS_DIR / f"{equipo_abrev}.png", 'wb') as f:
                    f.write(response.content)
                
                # Verificar que el archivo no esté vacío
                if os.path.getsize(LOGOS_DIR / f"{equipo_abrev}.png") > 1024:
                    logos_descargados += 1
                    log_message(f"✅ {equipo_abrev}: Logo descargado correctamente", True)
                    return True
                else:
                    os.remove(LOGOS_DIR / f"{equipo_abrev}.png")
                    log_message(f"⚠️ {equipo_abrev}: Archivo descargado vacío", True)
                    
        except Exception as e:
            log_message(f"⚠️ {equipo_abrev}: Error con {url.split('/')[2]} - {str(e)}", True)
            continue
    
    log_message(f"❌ {equipo_abrev}: Todos los intentos fallaron", True)
    return False

def descargar_imagen_jugador(player_id, nombre, equipo_dir):
    """Descarga la imagen de un jugador"""
    global jugadores_descargados, jugadores_fallidos
    
    urls = [
        f"https://cdn.nba.com/headshots/nba/latest/260x190/{player_id}.png",
        f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{player_id}.png"
    ]
    
    safe_name = unidecode(nombre).replace(' ', '_').replace("'", "").replace("-", "_")
    filename = equipo_dir / f"{safe_name}.jpg"

    for attempt in range(MAX_RETRIES):
        for url in urls:
            try:
                time.sleep(DELAY_BETWEEN_PLAYERS * (attempt + 0.5))
                response = requests.get(url, stream=True, timeout=15)
                
                if response.status_code == 200 and len(response.content) > 5000:
                    with open(filename, "wb") as f:
                        f.write(response.content)
                    jugadores_descargados += 1
                    return True
            except Exception as e:
                continue
    
    jugadores_fallidos += 1
    return False

def deberia_procesar_equipo(equipo_abrev):
    """Determina si un equipo debe ser procesado según los filtros"""
    if EXCLUIR_TODOS_EQUIPOS and equipo_abrev not in EQUIPOS_A_DESCARGAR:
        return False
    if EQUIPOS_A_DESCARGAR and equipo_abrev not in EQUIPOS_A_DESCARGAR:
        return False
    if equipo_abrev in EQUIPOS_A_EXCLUIR:
        return False
    return True

def procesar_equipo(equipo_abrev, equipo_data, logos_data, log_active):
    """Procesa un equipo completo"""
    global total_jugadores, equipos_procesados
    
    if not deberia_procesar_equipo(equipo_abrev):
        log_message(f"\n⏩ Saltando equipo {equipo_data['nombre_completo']} - Filtrado por configuración", log_active)
        return
    
    # Descargar logo del equipo
    if descargar_logo(equipo_abrev, logos_data):
        log_message(f"🖼️ Logo de {equipo_abrev} descargado correctamente", log_active)
    else:
        log_message(f"❌ No se pudo descargar logo para {equipo_abrev}", log_active)
    
    # Si estamos en modo solo logos, terminamos aquí
    if DESCARGAR_SOLO_LOGOS:
        return
    
    # Procesar jugadores del equipo
    equipo_dir = PLAYERS_DIR / equipo_abrev
    equipo_dir.mkdir(exist_ok=True)
    
    total_jugadores += len(equipo_data['jugadores'])
    equipos_procesados += 1
    
    log_message(f"\n🏀 Procesando {equipo_data['nombre_completo']} ({len(equipo_data['jugadores'])} jugadores)", log_active)
    
    for jugador in equipo_data['jugadores']:
        if descargar_imagen_jugador(jugador['id'], jugador['nombre'], equipo_dir):
            log_message(f"✅ {jugador['nombre']} (ID: {jugador['id']})", log_active)
        else:
            log_message(f"❌ Fallo al descargar {jugador['nombre']}", log_active)

def main():
    """Función principal"""
    global log_active
    setup_directories()
    log_active = setup_logging()
    
    # Cargar datos
    try:
        with open(PLAYERS_JSON, 'r', encoding='utf-8') as f:
            players_data = json.load(f)
        with open(LOGOS_JSON, 'r', encoding='utf-8') as f:
            logos_data = json.load(f)
    except Exception as e:
        log_message(f"ERROR cargando JSON: {str(e)}", log_active)
        return
    
    # Procesar equipos
    for equipo_abrev, equipo_data in players_data.items():
        start_time = time.time()
        procesar_equipo(equipo_abrev, equipo_data, logos_data, log_active)
        elapsed_time = time.time() - start_time
        remaining_delay = max(0, DELAY_BETWEEN_TEAMS - elapsed_time)
        time.sleep(remaining_delay)
    
    # Resumen final
    log_message("\n" + "="*50, log_active)
    log_message(" RESUMEN FINAL".center(50), log_active)
    log_message("="*50, log_active)
    log_message(f"Equipos procesados: {equipos_procesados}", log_active)
    log_message(f"Logos descargados: {logos_descargados}/{len(players_data)}", log_active)
    log_message(f"Jugadores descargados: {jugadores_descargados}/{total_jugadores}", log_active)
    log_message("="*50, log_active)

if __name__ == "__main__":
    main()