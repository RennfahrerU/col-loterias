import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# Configuración de la página
st.set_page_config(page_title="Lottery Analytics Colombia", layout="wide")

class AnalizadorLoteria:
    def __init__(self, archivo_csv):
        self.archivo = archivo_csv
        self.df = self.cargar_datos()

    def cargar_datos(self):
        if not os.path.exists(self.archivo):
            st.error(f"No se encontró el archivo {self.archivo}. ¡Corre el scraper primero!")
            return pd.DataFrame()
        
        df = pd.read_csv(self.archivo, dtype={'result': str})
        # Limpieza de duplicados inmediata
        df = df.drop_duplicates(subset=['date', 'slug', 'result'])
        df['date'] = pd.to_datetime(df['date'])
        df['result'] = df['result'].str.zfill(4)
        
        for i in range(4):
            df[f'pos_{i+1}'] = df['result'].str[i].astype(int)
        
        df['suma_total'] = df[[f'pos_{i+1}' for i in range(4)]].sum(axis=1)
        return df

# --- INTERFAZ DE STREAMLIT ---

st.title("📊 Panel de Análisis Técnico de Loterías")
st.markdown("Analiza tendencias, frecuencias y atrasos de forma interactiva.")

# Cargar el analizador
analizador = AnalizadorLoteria('data_loterias_completo.csv')

if not analizador.df.empty:
    # --- SIDEBAR (Filtros) ---
    st.sidebar.header("Configuración")
    
    lista_loterias = analizador.df['slug'].unique().tolist()
    loteria_sel = st.sidebar.selectbox("Selecciona la Lotería", lista_loterias)
    
    dias_analisis = st.sidebar.slider("Días hacia atrás", 7, 365, 30)
    
    # Filtrar datos por la selección
    data_lote = analizador.df[analizador.df['slug'] == loteria_sel].copy()
    fecha_max = data_lote['date'].max()
    fecha_limite = fecha_max - pd.Timedelta(days=dias_analisis)
    df_filtrado = data_lote[data_lote['date'] >= fecha_limite]

    # --- MÉTRICAS RÁPIDAS ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sorteos", len(df_filtrado))
    with col2:
        num_caliente = "".join([str(df_filtrado[f'pos_{i+1}'].mode()[0]) for i in range(4)])
        st.metric("Número Caliente (Moda)", num_caliente)
    with col3:
        st.metric("Suma Promedio", f"{df_filtrado['suma_total'].mean():.1f}")

    # --- PESTAÑAS DE ANÁLISIS ---
    tab1, tab2, tab3 = st.tabs(["Frecuencias", "Mapas de Calor", "Atrasos (Lag)"])

    with tab1:
        st.subheader("Distribución por Posición")
        fig, axes = plt.subplots(2, 2, figsize=(10, 8))
        for i in range(4):
            ax = axes.flat[i]
            sns.countplot(x=f'pos_{i+1}', data=df_filtrado, ax=ax, palette='viridis')
            ax.set_title(f"Cifra {i+1}")
        st.pyplot(fig)

    with tab2:
        st.subheader("¿Qué días caen más ciertos números?")
        df_filtrado['dia_semana'] = df_filtrado['date'].dt.day_name()
        dias_ord = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        pos_sel = st.selectbox("Ver Mapa para Cifra:", [1, 2, 3, 4])
        pivot = df_filtrado.pivot_table(index='dia_semana', columns=f'pos_{pos_sel}', aggfunc='size', fill_value=0)
        pivot = pivot.reindex(index=dias_ord, columns=range(10), fill_value=0)
        
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        sns.heatmap(pivot, annot=True, cmap="YlGnBu", ax=ax2)
        st.pyplot(fig2)

    with tab3:
        st.subheader("Análisis de Atraso Posicional")
        # Lógica de atraso
        data_sort = data_lote.sort_values('date', ascending=False).reset_index(drop=True)
        atrasos = {}
        for i in range(1, 5):
            pos = f'pos_{i}'
            atrasos[f'Cifra {i}'] = [data_sort.index[data_sort[pos] == n].tolist()[0] if n in data_sort[pos].values else 99 for n in range(10)]
        
        df_atraso = pd.DataFrame(atrasos)
        fig3, ax3 = plt.subplots(figsize=(10, 5))
        sns.heatmap(df_atraso.T, annot=True, cmap="Reds", cbar_kws={'label': 'Sorteos atrás'})
        st.pyplot(fig3)

else:
    st.warning("No hay datos para mostrar.")