# Archivo: actions.py
import pandas as pd
import streamlit as st
import geopandas as gpd # type: ignore
from constants.home_constants import NODOS_MAP_FILEPATH

def cargar_datos(csv):
    """leer csv desde url"""
    return pd.read_csv(csv)


def obtener_datos_nodos(csv):
    """Obtener los datos de los nodos"""
    df = cargar_datos(csv)
    nodos_count = len(df)
    deparamentos_count = df["Departamento"].nunique()
    mentores_count = df["Cédula Mentor"].nunique()
    return nodos_count, deparamentos_count, mentores_count

def obtener_datos_mapa(csv):
    #Obtener el mapa de Colombia
    gdf = gpd.read_file(NODOS_MAP_FILEPATH)
    
    # Cargar los datos de los nodos
    df= cargar_datos(csv)
    
    
    # Agrupar por 'departamento' y contar los nodos
    count_by_departamento = df.groupby('Departamento').size().reset_index(name='Nodos')
    
    gdf['Nodos'] = 0
    for _, row in count_by_departamento.iterrows():
        gdf.loc[gdf['dpto_cnmbr'] == row['Departamento'].upper(), 'Nodos'] = row['Nodos']
    
    return gdf


def mostrar_imagen(ruta_imagen, width=None, use_container_width=False):
    """Carga y muestra una imagen en Streamlit."""
    st.image(ruta_imagen, width=width, use_container_width=use_container_width)


def centrar_texto(texto, tipo="h1"):
    """Centrar headers, subheaders y textos en Streamlit."""
    st.markdown(f"<{tipo} style='text-align: center;'>{texto}</{tipo}>", unsafe_allow_html=True)
