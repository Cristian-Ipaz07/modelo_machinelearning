import pandas as pd
import numpy as np
import os

# Para normalización y graficación futura
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split


# 2. Cargar dataset limpio
ruta = "data/processed/dataprocessed.csv"  # ajusta si cambia la ruta
df = pd.read_csv(ruta)
"""""
# 3. Confirmar tipos de datos
print("\n✅ Tipos de datos:\n")
print(df.dtypes)

# 4. Vista previa del dataset
print("\n✅ Primeras filas del dataset:\n")
print(df.head())
"""""
# 5. Crear un ID de partido para cada equipo
df['Game_ID'] = df['Date'] + '_' + df['Team'] + '_' + df['Opp']

# 6. Agrupar datos por equipo en cada partido (sumando estadísticas individuales)
stats_to_sum = [
    'FG', 'FGA', '2P', '2PA', '3P', '3PA', 'FT', 'FTA', 'ORB', 'DRB',
    'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS'
]

df_team = df.groupby(['Game_ID', 'Date', 'Team', 'Opp']).agg({
    col: 'sum' for col in stats_to_sum
}).reset_index()
""""
# 7. Guardar para revisar
print("\n✅ Dataset agrupado por equipo en cada partido:\n")
print(df_team.head())
"""
# Agregar columna Is_Home
df['Is_Home'] = df.apply(lambda row: 1 if row['Game_ID'].split('_')[1] == row['Team'] else 0, axis=1)

df['Date'] = pd.to_datetime(df['Date'])
# Ordenar por equipo y fecha
df = df.sort_values(['Team', 'Date'])
# Calcular días de descanso
df['Days_Rest'] = df.groupby('Team')['Date'].diff().dt.days
# Para el primer partido que es NaN, rellenamos con un valor, por ejemplo 3 días
df['Days_Rest'] = df['Days_Rest'].fillna(3)
"""
print(df_team.dtypes)
"""
# Crear Features Avanzadas
# Asegúrate de que no haya divisiones por cero usando np.where

# Porcentajes
df_team['FG%'] = np.where(df_team['FGA'] != 0, df_team['FG'] / df_team['FGA'], 0)
df_team['2P%'] = np.where(df_team['2PA'] != 0, df_team['2P'] / df_team['2PA'], 0)
df_team['3P%'] = np.where(df_team['3PA'] != 0, df_team['3P'] / df_team['3PA'], 0)
df_team['FT%'] = np.where(df_team['FTA'] != 0, df_team['FT'] / df_team['FTA'], 0)

# True Shooting Percentage (TS%)
df_team['TS%'] = np.where(
    (2 * (df_team['FGA'] + 0.44 * df_team['FTA'])) != 0,
    df_team['PTS'] / (2 * (df_team['FGA'] + 0.44 * df_team['FTA'])),
    0
)
# AST/TO Ratio
df_team['AST_TO'] = np.where(df_team['TOV'] != 0, df_team['AST'] / df_team['TOV'], 0)
# Rebotes por intentos de tiro
df_team['ORB_per_FGA'] = np.where(df_team['FGA'] != 0, df_team['ORB'] / df_team['FGA'], 0)
df_team['DRB_per_FGA'] = np.where(df_team['FGA'] != 0, df_team['DRB'] / df_team['FGA'], 0)
df_team['TRB_per_FGA'] = np.where(df_team['FGA'] != 0, df_team['TRB'] / df_team['FGA'], 0)
""""
# Verificación rápida
print("\n✅ Features avanzadas creadas.\n")
print(df_team.columns)
print(df.columns)
"""
# 1. Para obtener los puntos del oponente, creamos un DataFrame temporal
opponent_pts = df_team[['Game_ID', 'Team', 'PTS']].copy()
opponent_pts.columns = ['Game_ID', 'Opp', 'Opponent_PTS']  # Renombramos 'Team' a 'Opp' para hacer el merge

# 2. Unimos de nuevo al df_team
df_team = df_team.merge(opponent_pts, on=['Game_ID', 'Opp'], how='left')
"""
# Verificación rápida
print("\n✅ Opponent_Points agregados.\n")
print(df_team[['Team', 'Opp', 'PTS', 'Opponent_PTS']].head())
print(df_team.head())
"""

# Primero ordenamos de nuevo por equipo y fecha
df_team['Date'] = pd.to_datetime(df_team['Date'])
df_team = df_team.sort_values(['Team', 'Date'])

# Definimos qué columnas queremos hacer rolling
rolling_features = ['PTS', 'AST', 'TRB', 'STL', 'BLK', 'TOV', 'FG%', '3P%', 'FT%']

# Para cada feature, calculamos el promedio móvil de los últimos 5 partidos
for feature in rolling_features:
    df_team[f'{feature}_rolling5'] = df_team.groupby('Team')[feature].transform(lambda x: x.rolling(window=5, min_periods=1).mean())
"""
print("\n✅ Rolling stats creadas.\n")
print(df_team[[f'{col}_rolling5' for col in rolling_features]].head())
"""
# Elegimos las columnas que vamos a normalizar (las numéricas y rolling)
features_to_scale = [col for col in df_team.columns if any(metric in col for metric in ['rolling5', '%', 'AST_TO', 'ORB_per_FGA', 'DRB_per_FGA', 'TRB_per_FGA'])]

scaler = StandardScaler()
df_team_scaled = df_team.copy()
df_team_scaled[features_to_scale] = scaler.fit_transform(df_team[features_to_scale])

"""
print("\n✅ Normalización realizada.\n")
print(df_team_scaled.head())

# Histograma de puntos
plt.figure(figsize=(8,6))
sns.histplot(df_team['PTS'], kde=True, bins=30)
plt.title('Distribución de Puntos Anotados')
plt.xlabel('PTS')
plt.ylabel('Frecuencia')
plt.show()

# Mapa de calor de correlaciones
plt.figure(figsize=(14,10))
sns.heatmap(df_team[features_to_scale].corr(), cmap='coolwarm', annot=False)
plt.title('Mapa de Calor de Features')
plt.show()
"""
cols_to_drop = ['2P%', 'DRB_per_FGA', 'AST_TO', 'BLK_rolling5', 'STL_rolling5', '3P%']

# Borrar del dataframe
df_team_scaled = df_team_scaled.drop(columns=cols_to_drop)
"""
print("\n✅ Dataset listo. Columnas finales:\n")
print(df_team_scaled.columns)
"""
# Variables que NO usaremos como input directo
cols_to_exclude = ['Game_ID', 'Date', 'Team', 'Opp', 'PTS']  # Identificadores + Target

# X: Features (entrada al modelo)
X = df_team_scaled.drop(columns=cols_to_exclude)

# y: Target (lo que queremos predecir)
y = df_team_scaled['PTS']
X = X.drop(columns=['Opponent_PTS'])
""""
print("\n✅ Shapes:")
print("X shape:", X.shape)
print("y shape:", y.shape)
"""

X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2,      # 20% para test
    random_state=42,    # Semilla para reproducibilidad
)



"""
print("\n✅ Shapes después del split:")
print("X_train shape:", X_train.shape)
print("X_test shape:", X_test.shape)
print("y_train shape:", y_train.shape)
print("y_test shape:", y_test.shape)
"""

from keras.models import Sequential
from keras.layers import Dense, Dropout, LeakyReLU
from keras.optimizers import AdamW
from keras.callbacks import EarlyStopping

# Definimos el modelo
model = Sequential()

# Capa 1
model.add(Dense(256, input_shape=(X_train.shape[1],)))
model.add(LeakyReLU(alpha=0.01))

# Capa 2
model.add(Dense(512))
model.add(LeakyReLU(alpha=0.01))
model.add(Dropout(0.1))  # Dropout bajo

# Capa 3
model.add(Dense(256))
model.add(LeakyReLU(alpha=0.01))

# Capa de salida
model.add(Dense(1))

# Compilamos
optimizer = AdamW(learning_rate=0.0005, weight_decay=1e-5)
model.compile(optimizer=optimizer, loss='mse', metrics=['mae', 'mse'])

# Early stopping
early_stop = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)


# Entrenamiento
history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),  
    epochs=300,
    batch_size=64,
    callbacks=[early_stop],
    verbose=1
)


# Evaluación
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import matplotlib.pyplot as plt

# Predicciones
y_pred = model.predict(X_test).flatten()

import numpy as np

print(np.isnan(y_pred).sum())  # ¿Cuántos NaN hay?
print(np.isinf(y_pred).sum())  # ¿Cuántos Inf hay?


# Métricas
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("\n✅ Evaluación del modelo:")
print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"R²: {r2:.4f}")

# Graficar pérdida de entrenamiento y validación
plt.figure(figsize=(14,5))

# Curva de pérdida
plt.subplot(1,2,1)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Pérdida (Loss) durante el entrenamiento')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

# Predicciones vs reales
plt.subplot(1,2,2)
plt.scatter(y_test, y_pred, alpha=0.7)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')  # Línea ideal
plt.title('Predicciones vs Reales')
plt.xlabel('Valores Reales')
plt.ylabel('Valores Predichos')
plt.tight_layout()
plt.show()


# 🔥 1. Definir los partidos de hoy manualmente
partidos_hoy = [
    ("ORL", "BOS"),  # Magic vs Celtics
    ("MIL", "IND"),  # Bucks vs Pacers
    ("MIN", "LAL")   # Timberwolves vs Lakers
]

# 🔥 2. Obtener lista de equipos únicos involucrados
equipos_unicos = set([e for partido in partidos_hoy for e in partido])

# 🔥 3. Filtrar datos actualizados de cada equipo en df_team_scaled
df_equipos_hoy = df_team_scaled[df_team_scaled['Team'].isin(equipos_unicos)].copy()

# 🔥 4. Para cada equipo, preparar datos y predecir
for equipo in equipos_unicos:
    datos_equipo = df_equipos_hoy[df_equipos_hoy['Team'] == equipo]
    
    if datos_equipo.empty:
        print(f"No se encontraron datos para el equipo {equipo}.")
        continue
    
    # Preparamos las columnas igual que en el entrenamiento
    X_equipo = datos_equipo.drop(columns=['Game_ID', 'Date', 'Team', 'Opp', 'PTS', 'Opponent_PTS'], errors='ignore')
    
    # (Nota: No se hace scaler.transform porque ya df_team_scaled está normalizado)

    # Predicción
    prediccion = model.predict(X_equipo)
    prediccion = prediccion.flatten()[0]  # Convertimos array a número
    
    print(f"🔵 Predicción de puntos para {equipo}: {prediccion:.2f}")

# 🔥 5. Mostrar predicciones por partido
print("\n--- Predicciones de los partidos ---")
for local, visitante in partidos_hoy:
    print(f"{local} vs {visitante}")
