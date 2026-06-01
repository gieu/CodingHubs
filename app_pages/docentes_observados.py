import pandas as pd
import streamlit as st

from actions.docentes_observados_actions import (
    grafico_cierre_actividad,
    grafico_conexion_pc,
    grafico_distribucion_escenario,
    grafico_distribucion_grado,
    grafico_dudas_estudiantes,
    grafico_explicacion_reglas,
    grafico_introduccion_juego,
    grafico_mariposa_ninos_ninas,
    grafico_materiales_docente,
    grafico_organizacion_grupos,
    grafico_primera_vez,
    grafico_tiempo_uso,
    grafico_treemap_sedes,
    grafico_vocabulario_terminos,
)
from constants.header_constants import header
from utils.chart_config import get_chart_config

chart_config = get_chart_config()

header("#282255")

SHEET_ID = "1k7hHR838J85-SRZ-J6odEx8UDH3_MKYB"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"


@st.cache_data(ttl=600)
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df


st.title("Observaciones Docentes Biobots")

try:
    df_obs = load_data(CSV_URL)

    # ── Sección 1: Información básica ─────────────────────────────────────
    st.subheader("Distribución de estudiantes por sede educativa")
    grafico_mariposa_ninos_ninas(df_obs, chart_config)

    st.subheader("Distribución de observaciones por grado escolar")
    grafico_distribucion_grado(df_obs, chart_config)

    st.subheader("Distribución de observaciones por sede educativa")
    grafico_treemap_sedes(df_obs, chart_config)

    # ── Sección 2: Antes del juego ────────────────────────────────────────
    st.subheader("Distribución de observaciones por escenario jugado")
    grafico_distribucion_escenario(df_obs, chart_config)

    st.subheader("Métodos usados para introducir el juego")
    grafico_introduccion_juego(df_obs, chart_config)

    st.subheader("¿Cómo se organizaron los grupos?")
    grafico_organizacion_grupos(df_obs, chart_config)

    st.subheader("Uso de materiales y guías del kit por el docente")
    grafico_materiales_docente(df_obs, chart_config)

    # ── Sección 3: Durante el juego ───────────────────────────────────────
    st.subheader("Métodos usados para explicar las reglas del juego")
    grafico_explicacion_reglas(df_obs, chart_config)

    st.subheader("Tipos de dudas observadas en los estudiantes")
    grafico_dudas_estudiantes(df_obs, chart_config)

    st.subheader("Vocabulario técnico mencionado durante la sesión")
    grafico_vocabulario_terminos(df_obs, chart_config)

    # ── Sección 4: Después del juego ──────────────────────────────────────
    st.subheader("Tiempo de uso directo con el juego")
    grafico_tiempo_uso(df_obs, chart_config)

    st.subheader("¿Fue la primera vez que jugaron el escenario?")
    grafico_primera_vez(df_obs, chart_config)

    st.subheader("Conexión con pensamiento computacional al finalizar la sesión")
    grafico_conexion_pc(df_obs, chart_config)

    st.subheader("Tipo de espacio usado para el cierre")
    grafico_cierre_actividad(df_obs, chart_config)

except Exception as exc:
    st.error(f"No se pudieron cargar los datos: {exc}")
