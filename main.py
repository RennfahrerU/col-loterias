import requests
import pandas as pd
from datetime import datetime

def obtener_resultados_loterias(fecha):
    url = f"https://api-resultadosloterias.com/api/results/{fecha}"
    
    # Definimos los slugs que nos interesan
    loterias_objetivo = [
        'sinuano-dia', 
        'sinuano-noche', 
        'caribena-dia', 
        'caribena-noche'
    ]
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == 'success':
            # 1. Convertir a DataFrame de Pandas
            df = pd.DataFrame(data['data'])
            
            # 2. Filtrar solo las loterías que te interesan
            df_filtrado = df[df['slug'].isin(loterias_objetivo)].copy()
            
            # 3. Limpieza: Eliminar duplicados (la API parece devolver varios registros iguales)
            df_filtrado = df_filtrado.drop_duplicates()
            
            return df_filtrado
        else:
            print(f"Error en la API: {data.get('message')}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Ocurrió un error al conectar: {e}")
        return pd.DataFrame()

# --- Ejecución ---
# Puedes cambiar la fecha manualmente o usar datetime.now()
fecha_consulta = "2026-02-21" 
resultados = obtener_resultados_loterias(fecha_consulta)

if not resultados.empty:
    # Guardar en CSV (modo 'a' para agregar datos si ya existe el archivo)
    nombre_archivo = 'historico_loterias.csv'
    
    # Si el archivo no existe, lo crea con encabezados. Si existe, solo agrega filas.
    import os
    header = not os.path.exists(nombre_archivo)
    
    resultados.to_csv(nombre_archivo, mode='a', index=False, header=header, encoding='utf-8')
    print(f"¡Éxito! Datos de {fecha_consulta} guardados en {nombre_archivo}")
    print(resultados)
else:
    print("No se encontraron datos para guardar.")