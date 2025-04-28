import pandas as pd
import os

# Definir rutas
raw_csv_path = os.path.join("..", "data", "raw", "2024-20252.csv")
processed_dir = os.path.join("..", "data", "processed")
processed_csv_path = os.path.join(processed_dir, "dataprocessed.csv")

# Crear carpeta 'processed' si no existe
os.makedirs(processed_dir, exist_ok=True)

# Cargar el dataset
df = pd.read_csv(raw_csv_path)

# 1. Verificar nulos antes de limpieza
print("📋 Valores nulos por columna antes de limpieza:")
print(df.isnull().sum())


# 2. Reemplazar nulos por 0
df = df.fillna(0)

print("\n📋 Valores nulos por columna después de limpieza:")

print(df.isnull().sum())
print("Vaolores completados con 0")

# 3. Convertir columna 'Date' a formato datetime
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    print("\n✅ Tipo de 'Date' actualizado a formato datetime.")
else:
    print("\n⚠️ Advertencia: No se encontró la columna 'Date' en el dataset.")

# 4. Verificar nulos después de limpieza


# 5. Guardar dataset limpio
df.to_csv(processed_csv_path, index=False)

print(f"\n✅ Dataset limpio guardado en: {processed_csv_path}")
