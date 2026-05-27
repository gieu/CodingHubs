import pandas as pd
import streamlit as st

from actions.informe_biobots_actions import (
    grafico_boxplot_puntaje_pc,
    grafico_correlacion_pc_egma,
    grafico_distribucion_aciertos_egma,
    grafico_distribucion_aciertos_pc,
    grafico_distribucion_ciudad_edad,
    grafico_distribucion_ciudad_grado,
    grafico_estereotipos_genero,
    grafico_histograma_puntaje_pc,
    grafico_mariposa_sexo,
    grafico_respuestas_items_pc,
    grafico_treemap_instituciones,
)
from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import header
from utils.chart_config import get_chart_config

chart_config = get_chart_config()

header("#282255")

# ----------datos_biobots_og-----------------------------
SHEET_ID = "1GPoooJUN7OQ55BsOB7usBizqQXBCcN3K"
GID = "963668480"
CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export"
    f"?format=csv&gid={GID}"
)


@st.cache_data(ttl=600)
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df


st.title("Informe Biobots")

try:
    df_consolidado = load_data(CSV_URL)

    st.subheader("Distribuciones de estudiantes BIOBOTS")
    grafico_mariposa_sexo(df_consolidado, chart_config)

    st.subheader("Distribución por ciudad y grado escolar")
    grafico_distribucion_ciudad_grado(df_consolidado, chart_config)

    st.subheader("Distribución por ciudad y edad")
    grafico_distribucion_ciudad_edad(df_consolidado, chart_config)

    st.subheader("Distribución por institución educativa")
    grafico_treemap_instituciones(df_consolidado, chart_config)

    st.subheader("Estereotipos de género por profesión")
    grafico_estereotipos_genero(df_consolidado, chart_config)

    st.subheader("Respuestas por ítem de Pensamiento Computacional")
    grafico_respuestas_items_pc(df_consolidado, chart_config)

    st.subheader("Puntaje de Pensamiento Computacional por ciudad y sexo")
    grafico_boxplot_puntaje_pc(df_consolidado, chart_config)

    st.subheader("Distribución del puntaje de Pensamiento Computacional")
    grafico_histograma_puntaje_pc(df_consolidado, chart_config)

    st.subheader("Distribución de aciertos en Pensamiento Computacional")
    grafico_distribucion_aciertos_pc(df_consolidado, chart_config)

    st.subheader("Distribución de aciertos EGMA")
    grafico_distribucion_aciertos_egma(df_consolidado, chart_config)

    st.subheader("Relación entre aciertos EGMA y puntaje de Pensamiento Computacional")
    grafico_correlacion_pc_egma(df_consolidado, chart_config)

except Exception as exc:
    st.error(f"No se pudieron cargar los datos: {exc}")
