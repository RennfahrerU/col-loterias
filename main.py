import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os

def extraer_historico(dias_atras, fecha_inicio=None):
    if fecha_inicio is None:
        fecha_inicio = datetime.now()
    else:
        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")

    loterias_objetivo = ['sinuano-dia', 'sinuano-noche', 'caribena-dia', 'caribena-noche', "super-astro-sol", "super-astro-luna", "super-astro-estrella"]
    archivo_csv = 'data_loterias_completo.csv'
    
    columna_fecha_formateada = [] # Para asegurar orden cronológico después

    for i in range(dias_atras):
        fecha_consulta = (fecha_inicio - timedelta(days=i)).strftime("%Y-%m-%d")
        url = f"https://api-resultadosloterias.com/api/results/{fecha_consulta}"
        
        print(f"Consultando: {fecha_consulta}...")
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success' and data['data']:
                    df = pd.DataFrame(data['data'])
                    
                    # Filtrar y limpiar
                    df_res = df[df['slug'].isin(loterias_objetivo)].copy()
                    df_res = df_res.drop_duplicates()
                    
                    if not df_res.empty:
                        # Guardar (Append)
                        header = not os.path.exists(archivo_csv)
                        df_res.to_csv(archivo_csv, mode='a', index=False, header=header, encoding='utf-8')
                    
                else:
                    print(f"Sin datos para {fecha_consulta}")
            
            # Respetar la API: Pausa de 1 segundo entre peticiones para evitar bloqueos
            time.sleep(1) 
            
        except Exception as e:
            print(f"Error en {fecha_consulta}: {e}")

    print(f"\nProceso terminado. Datos guardados en {archivo_csv}")

# --- CONFIGURACIÓN ---
# Ejemplo: Extraer los últimos 30 días a partir de hoy
extraer_historico(dias_atras=90)