import json
from datetime import datetime
from statistics import mean
import os

def calcular_probabilidad_implícita(odds):
    """Convierte odds decimales a probabilidad implícita"""
    return 1 / odds

def calcular_valor_esperado(prob_modelo, odds_mercado):
    """Calcula el valor esperado de una apuesta"""
    prob_implícita = calcular_probabilidad_implícita(odds_mercado)
    return (prob_modelo - prob_implícita) / prob_implícita

def procesar_odds(odds_data):
    """Consolida odds de diferentes bookmakers para todos los mercados"""
    if isinstance(odds_data, list):
        if len(odds_data) == 0:
            raise ValueError("La lista de odds está vacía")
        odds_data = odds_data[0]
    
    if not isinstance(odds_data, dict) or 'bookmakers' not in odds_data:
        raise ValueError("Formato de datos de odds incorrecto. Se esperaba un diccionario con clave 'bookmakers'")
    
    consolidated = {
        'moneyline': {'home': [], 'away': []},
        'spread': {'home': [], 'away': [], 'points': []},
        'total': {'over': [], 'under': [], 'points': []}
    }
    
    for bookmaker in odds_data.get('bookmakers', []):
        for market in bookmaker.get('markets', []):
            if market['key'] == 'h2h':
                for outcome in market.get('outcomes', []):
                    if outcome['name'] == odds_data['home_team']:
                        consolidated['moneyline']['home'].append(outcome['price'])
                    else:
                        consolidated['moneyline']['away'].append(outcome['price'])
            
            elif market['key'] == 'spreads':
                for outcome in market.get('outcomes', []):
                    if outcome['name'] == odds_data['home_team']:
                        consolidated['spread']['home'].append(outcome['price'])
                        consolidated['spread']['points'].append(outcome['point'])
                    else:
                        consolidated['spread']['away'].append(outcome['price'])
            
            elif market['key'] == 'totals':
                for outcome in market.get('outcomes', []):
                    if outcome['name'] == 'Over':
                        consolidated['total']['over'].append(outcome['price'])
                        consolidated['total']['points'].append(outcome['point'])
                    else:
                        consolidated['total']['under'].append(outcome['price'])
    
    # Calcular promedios
    for market in consolidated:
        for key in consolidated[market]:
            if consolidated[market][key]:
                if key == 'points':
                    # Para puntos, tomamos el valor más común en lugar del promedio
                    try:
                        consolidated[market][key] = mean(consolidated[market][key])
                    except:
                        consolidated[market][key] = consolidated[market][key][0] if consolidated[market][key] else None
                else:
                    try:
                        consolidated[market][key] = mean(consolidated[market][key])
                    except:
                        consolidated[market][key] = None
            else:
                consolidated[market][key] = None
    
    return consolidated

def generar_recomendaciones(predicciones, odds_consolidadas, odds_data):
    """Genera recomendaciones basadas en valor esperado"""
    if not isinstance(predicciones, list):
        raise ValueError("Las predicciones deben ser una lista")
    
    recomendaciones = []
    
    for prediccion in predicciones:
        if not isinstance(prediccion, dict):
            continue
            
        try:
            if prediccion.get('prediction_type') == 'is_win':
                team_type = 'home' if prediccion.get('team') == odds_data.get('home_team') else 'away'
                if odds_consolidadas['moneyline'][team_type]:
                    valor = calcular_valor_esperado(
                        prediccion.get('probability', 0),
                        odds_consolidadas['moneyline'][team_type]
                    )
                    
                    recomendaciones.append({
                        'game_id': prediccion.get('game_id', ''),
                        'market': 'moneyline',
                        'selection': prediccion.get('team', ''),
                        'model_prob': prediccion.get('probability', 0),
                        'implied_prob': calcular_probabilidad_implícita(odds_consolidadas['moneyline'][team_type]),
                        'odds': odds_consolidadas['moneyline'][team_type],
                        'value': valor,
                        'confidence': prediccion.get('confidence', 0),
                        'recommendation': 'STRONG BET' if valor > 0.15 else ('BET' if valor > 0.05 else 'NO BET')
                    })
        except Exception as e:
            print(f"Error procesando predicción: {str(e)}")
            continue
    
    return recomendaciones

def generar_json_integrado(predicciones, odds_data, odds_consolidadas, recomendaciones):
    """Genera el JSON final para la app"""
    return {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'game_id': odds_data.get('id', ''),
            'home_team': odds_data.get('home_team', ''),
            'away_team': odds_data.get('away_team', ''),
            'commence_time': odds_data.get('commence_time', '')
        },
        'model_predictions': predicciones,
        'odds_consolidadas': odds_consolidadas,
        'value_analysis': recomendaciones,
        'top_recommendation': max(recomendaciones, key=lambda x: x.get('value', 0)) if recomendaciones else None
    }

def imprimir_resumen(analisis):
    """Muestra un resumen en consola"""
    if not isinstance(analisis, dict):
        print("Datos de análisis no válidos")
        return
    
    print("\n=== RESUMEN DE ANÁLISIS ===")
    print(f"Partido: {analisis.get('metadata', {}).get('home_team', 'Desconocido')} vs {analisis.get('metadata', {}).get('away_team', 'Desconocido')}")
    print(f"Fecha: {analisis.get('metadata', {}).get('commence_time', 'Desconocida')}")
    
    print("\nODDS CONSOLIDADAS:")
    print(f"Moneyline - {analisis.get('metadata', {}).get('home_team', 'Local')}: {analisis.get('odds_consolidadas', {}).get('moneyline', {}).get('home', 'N/A'):.2f}")
    print(f"Moneyline - {analisis.get('metadata', {}).get('away_team', 'Visitante')}: {analisis.get('odds_consolidadas', {}).get('moneyline', {}).get('away', 'N/A'):.2f}")
    
    print("\nMEJOR RECOMENDACIÓN:")
    top_rec = analisis.get('top_recommendation')
    if top_rec:
        print(f"Mercado: {top_rec.get('market', '')} - {top_rec.get('selection', '')}")
        print(f"Odds: {top_rec.get('odds', 0):.2f} | Valor: {top_rec.get('value', 0)*100:.1f}%")
        print(f"Confianza modelo: {top_rec.get('confidence', 0)*100:.0f}%")
        print(f"Recomendación: {top_rec.get('recommendation', '')}")
    else:
        print("No hay recomendaciones con valor positivo")

def main():
    try:
        # Configuración de rutas
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        DATA_JSON_DIR = os.path.join(BASE_DIR, 'data', 'json')
        ODDS_JSON_DIR = os.path.join(BASE_DIR, 'json', 'odds_extraidas')
        
        # Crear directorios si no existen
        os.makedirs(DATA_JSON_DIR, exist_ok=True)
        os.makedirs(ODDS_JSON_DIR, exist_ok=True)

        # Archivos de entrada/salida
        datos_modelo_path = os.path.join(DATA_JSON_DIR, 'datos_modelo.json')
        odds_api_path = os.path.join(ODDS_JSON_DIR, 'odds_completas_2025_06_08.json')
        output_path = os.path.join(DATA_JSON_DIR, 'analisis_odds.json')

        # Cargar datos del modelo
        if not os.path.exists(datos_modelo_path):
            raise FileNotFoundError(f"No se encontró el archivo de predicciones: {datos_modelo_path}")
        
        with open(datos_modelo_path, 'r', encoding='utf-8') as f:
            datos_modelo = json.load(f)
            if not isinstance(datos_modelo, dict) or 'predictions' not in datos_modelo:
                raise ValueError("El archivo datos_modelo.json no tiene el formato correcto")

        # Cargar datos de odds
        if not os.path.exists(odds_api_path):
            raise FileNotFoundError(f"No se encontró el archivo de odds: {odds_api_path}")
        
        with open(odds_api_path, 'r', encoding='utf-8') as f:
            odds_data = json.load(f)
            if not odds_data:
                raise ValueError("El archivo de odds está vacío")

        # Procesamiento
        odds_api = odds_data[0] if isinstance(odds_data, list) else odds_data
        odds_consolidadas = procesar_odds(odds_api)
        recomendaciones = generar_recomendaciones(datos_modelo['predictions'], odds_consolidadas, odds_api)
        analisis_completo = generar_json_integrado(datos_modelo['predictions'], odds_api, odds_consolidadas, recomendaciones)

        # Guardar resultados
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analisis_completo, f, indent=2, ensure_ascii=False)
        
        # Mostrar resumen
        imprimir_resumen(analisis_completo)
        print(f"\nAnálisis completo guardado en: {output_path}")

    except FileNotFoundError as e:
        print(f"\nERROR: {str(e)}")
        print("Verifica que los archivos existan en las rutas especificadas")
    except json.JSONDecodeError:
        print("\nERROR: Los archivos JSON no tienen un formato válido")
    except Exception as e:
        print(f"\nERROR inesperado: {str(e)}")
        print("Revisa la estructura de tus archivos y los datos de entrada")

if __name__ == '__main__':
    main()