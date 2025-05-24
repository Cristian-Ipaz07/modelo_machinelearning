import os
import requests
import xml.etree.ElementTree as ET

API_KEY = "Z46Ud2TAfYs4jeaeUZF3cxoggW7ZNuhneOAdtued"
YEAR = "2024"
PLAYER_ID = "fd5ecb47-fb70-495d-95d8-2fe5fce2fce9"  # Stephen Curry

# Endpoint del manifiesto XML
manifest_url = f"https://api.sportradar.com/nba-images-t3/getty/headshots/players/{YEAR}/manifest.xml?api_key={API_KEY}"

# Carpeta para guardar la imagen
photos_folder = "player_photos"
os.makedirs(photos_folder, exist_ok=True)

# Descargar el manifiesto
response = requests.get(manifest_url)

if response.status_code == 200:
    root = ET.fromstring(response.content)

    # Buscar imagen con el player_id
    found = False
    for image in root.findall(".//image"):
        id_elem = image.find("id")
        if id_elem is not None and id_elem.text == PLAYER_ID:
            url_elem = image.find("url")
            if url_elem is not None:
                image_url = url_elem.text
                print(f"🔗 Imagen encontrada: {image_url}")

                img_resp = requests.get(image_url)
                if img_resp.status_code == 200:
                    image_path = os.path.join(photos_folder, f"{PLAYER_ID}.jpg")
                    with open(image_path, "wb") as f:
                        f.write(img_resp.content)
                    print(f"✅ Imagen guardada en: {image_path}")
                else:
                    print("❌ No se pudo descargar la imagen.")
                found = True
                break

    if not found:
        print(f"❌ No se encontró imagen para el player_id {PLAYER_ID}")
else:
    print(f"❌ Error al obtener el manifiesto. Código HTTP: {response.status_code}")
