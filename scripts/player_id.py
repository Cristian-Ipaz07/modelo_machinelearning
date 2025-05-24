import os
import json
import requests
import time
from unidecode import unidecode
from datetime import datetime
from pathlib import Path

# Configuración de rutas
BASE_DIR = Path("F:/Programacion/DESARROLLADOR PROFESIONAL/Modelo_Predictor")
JSON_PATH = BASE_DIR / "data" / "json" / "json.json"
IMAGES_DIR = BASE_DIR / "images" / "players"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "download_log.txt"

# Configuración de descarga
DELAY_BETWEEN_PLAYERS = 1.5
DELAY_BETWEEN_TEAMS = 3
MAX_RETRIES = 3

# Configuración de filtros (MODIFICA ESTO PARA SELECCIONAR EQUIPOS)
EQUIPOS_A_DESCARGAR = ["PHX", "POR", "SAC", "SAS", "UTA"]
# EQUIPOS_A_DESCARGAR = []  # Vacío para descargar todos
EQUIPOS_A_EXCLUIR = []  # Ejemplo: ["LAL", "GSW"] para excluir Lakers y Warriors

# Contadores globales
total_jugadores = 0
jugadores_descargados = 0
jugadores_fallidos = 0
equipos_procesados = 0

def setup_logging():
    """Configuración del sistema de logging"""
    try:
        LOG_DIR.mkdir(exist_ok=True)
        if not LOG_FILE.exists():
            LOG_FILE.touch()
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n\n=== Nueva ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        return True
    except Exception as e:
        print(f"AVISO: No se pudo configurar logging ({e}). Continuando sin log...")
        return False

def log_message(message, log_active=True):
    """Escribe en log y consola"""
    print(message)
    if not log_active:
        return
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except Exception as e:
        print(f"AVISO: No se pudo escribir en log ({e})")

def descargar_imagen(player_id, nombre, equipo_dir):
    """Descarga la imagen de un jugador"""
    global jugadores_descargados, jugadores_fallidos
    
    urls = [
        f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png",
        f"https://cdn.nba.com/headshots/nba/latest/260x190/{player_id}.png",
        f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{player_id}.png"
    ]
    
    safe_name = unidecode(nombre).replace(' ', '_').replace("-", "_").replace("'", "")
    filename = equipo_dir / f"{safe_name}.jpg"

    for attempt in range(MAX_RETRIES):
        for url in urls:
            try:
                time.sleep(DELAY_BETWEEN_PLAYERS * (attempt + 0.5))
                response = requests.get(url, stream=True, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
                
                if response.status_code == 200 and len(response.content) > 5000:
                    with open(filename, "wb") as f:
                        f.write(response.content)
                    jugadores_descargados += 1
                    return True
                    
            except Exception as e:
                log_message(f"Intento {attempt + 1} fallido para {nombre}: {str(e)}", log_active)
                continue
    
    jugadores_fallidos += 1
    return False

def deberia_procesar_equipo(equipo_abrev):
    """Determina si un equipo debe ser procesado según los filtros"""
    if EQUIPOS_A_DESCARGAR and equipo_abrev not in EQUIPOS_A_DESCARGAR:
        return False
    if equipo_abrev in EQUIPOS_A_EXCLUIR:
        return False
    return True

def procesar_equipo(equipo_abrev, equipo_data, log_active):
    """Procesa un equipo completo"""
    global total_jugadores, equipos_procesados
    
    if not deberia_procesar_equipo(equipo_abrev):
        log_message(f"\n⏩ Saltando equipo {equipo_data['nombre_completo']} ({equipo_abrev}) - Excluido por filtros", log_active)
        return
    
    equipo_dir = IMAGES_DIR / equipo_abrev
    equipo_dir.mkdir(exist_ok=True)
    
    total_jugadores += len(equipo_data['jugadores'])
    equipos_procesados += 1
    
    log_message(f"\n🏀 Iniciando descarga para {equipo_data['nombre_completo']} ({equipo_abrev})", log_active)
    
    for jugador in equipo_data['jugadores']:
        if descargar_imagen(jugador['id'], jugador['nombre'], equipo_dir):
            log_message(f"✅ {jugador['nombre']} (ID: {jugador['id']})", log_active)
        else:
            log_message(f"❌ Fallo al descargar {jugador['nombre']} (ID: {jugador['id']})", log_active)

def mostrar_resumen():
    """Muestra un resumen de la ejecución"""
    print("\n" + "="*50)
    print(" RESUMEN DE EJECUCIÓN".center(50))
    print("="*50)
    print(f"Equipos procesados: {equipos_procesados}")
    print(f"Total jugadores: {total_jugadores}")
    print(f"Jugadores descargados: {jugadores_descargados}")
    print(f"Jugadores fallidos: {jugadores_fallidos}")
    print(f"Tasa de éxito: {(jugadores_descargados/total_jugadores)*100:.2f}%" if total_jugadores > 0 else "Tasa de éxito: N/A")
    print("="*50)
    print(f"Equipos incluidos: {EQUIPOS_A_DESCARGAR or 'Todos'}")
    print(f"Equipos excluidos: {EQUIPOS_A_EXCLUIR or 'Ninguno'}")
    print("="*50)

def main():
    """Función principal"""
    global log_active
    log_active = setup_logging()
    
    if not JSON_PATH.exists():
        log_message(f"ERROR: Archivo JSON no encontrado en {JSON_PATH}", log_active)
        return
    
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        log_message(f"ERROR cargando JSON: {str(e)}", log_active)
        return
    
    for equipo_abrev, equipo_data in data.items():
        start_time = time.time()
        procesar_equipo(equipo_abrev, equipo_data, log_active)
        elapsed_time = time.time() - start_time
        remaining_delay = max(0, DELAY_BETWEEN_TEAMS - elapsed_time)
        time.sleep(remaining_delay)
    
    mostrar_resumen()

if __name__ == "__main__":
    main()