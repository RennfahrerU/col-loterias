import pandas as pd

def analizar_resultados(archivo_csv):
    if not pd.io.common.file_exists(archivo_csv):
        print("El archivo no existe. Primero corre el scraper.")
        return

    # 1. Cargar datos
    df = pd.read_csv(archivo_csv, dtype={'result': str}) # Leer resultado como texto para no perder ceros a la izquierda
    
    # 2. Limpieza y preparación
    df['result'] = df['result'].str.zfill(4) # Asegurar que tengan 4 cifras (ej. '0123')
    
    # Desglosar el resultado en 4 columnas (Posición 1, 2, 3 y 4)
    df['pos_1'] = df['result'].str[0]
    df['pos_2'] = df['result'].str[1]
    df['pos_3'] = df['result'].str[2]
    df['pos_4'] = df['result'].str[3]

    loterias = df['lottery'].unique()

    print("=== REPORTE DE ANALÍTICA DE LOTERÍA ===")
    
    for loteria in loterias:
        df_lote = df[df['lottery'] == loteria]
        total_sorteos = len(df_lote)
        
        print(f"\n>>> ANÁLISIS PARA: {loteria} ({total_sorteos} sorteos registrados)")
        
        # Analizar cada posición
        for i in range(1, 5):
            col = f'pos_{i}'
            # Obtener el top 3 de números que más salen en esta posición
            top_numeros = df_lote[col].value_counts().head(3)
            
            res_str = ", ".join([f"Num {num} ({cant} veces)" for num, cant in top_numeros.items()])
            print(f"  Posición {i} (Cifra {i}): {res_str}")

        # Análisis de "Números Calientes" (Combinación sugerida)
        sugerido = "".join([df_lote[f'pos_{j}'].mode()[0] for j in range(1, 5)])
        print(f"  > Número 'Más Frecuente' (Basado en modas): {sugerido}")

# --- EJECUCIÓN ---
analizar_resultados('data_loterias_completo.csv')