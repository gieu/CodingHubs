from urllib.error import URLError

import pandas as pd
import streamlit as st

from actions.marco_actions import (
    barras_pretest_postest,
    centrar_texto,
    crear_grafico_radar,
    obtener_datos_pretest_posttest,
    obtener_opciones_codigos,
)
from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import header
from constants.marco_constants import COLORS, MAPPING, OPCIONES_INICIALES
from utils.chart_config import get_chart_config


CONSOLIDADO_URL = "https://docs.google.com/spreadsheets/d/1qMlLT2gCVcwHZb1UC1f3U-LBcfHV_Dnt/export?format=csv"
ESCALA_NIVELES = [nivel for nivel in MAPPING if nivel != "0"]
ETIQUETAS_MOMENTOS = {
    "pre_2024": "Pretest 2024",
    "post_2024": "Postest 2024",
    "post_2025": "Postest 2025",
    "nivel_2025": "Nivel 2025",
    "post_2026_junio": "Postest · junio 2026",
    "nivel_2026_junio": "Nivel · junio 2026",
    "post_2026_diciembre": "Postest · diciembre 2026",
    "nivel_2026_diciembre": "Nivel · diciembre 2026",
}
COLORES_RADAR = {
    **COLORS,
    "post_2026_junio": {"line": "#138276", "fill": "rgba(19, 130, 118, 0.18)"},
    "nivel_2026_junio": {"line": "#577d1b", "fill": "rgba(87, 125, 27, 0.18)"},
    "post_2026_diciembre": {"line": "#1f5480", "fill": "rgba(31, 84, 128, 0.18)"},
    "nivel_2026_diciembre": {"line": "#a7522b", "fill": "rgba(167, 82, 43, 0.18)"},
}
DIMENSIONES = (
    "Liderazgo y visión",
    "Plan de área",
    "Enseñanza, aprendizaje y evaluación",
    "Desarrollo profesional del personal docente",
    "Equidad, diversidad e inclusión",
    "Proyección en educación terciaria",
    "Impacto en los resultados",
    "Equidad de género",
)

@st.cache_data(ttl=600)
def cargar_consolidado(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df


chart_config = get_chart_config()
centrar_texto("Marco Bucaramanga", "h1")
header("#282255")

try:
    df = cargar_consolidado(CONSOLIDADO_URL)
except (URLError, pd.errors.EmptyDataError, pd.errors.ParserError):
    st.error("No se pudo leer el consolidado de Marco de Calidad desde Google Sheets.")
    st.stop()

columnas = ["codigo_ie", "Momento", *(f"Dimensión {numero}" for numero in range(1, 9))]
if not set(columnas).issubset(df.columns):
    st.error("El consolidado debe incluir el código de institución, el momento y las ocho dimensiones.")
    st.stop()
df = df[columnas]

momentos_consolidado = set(df["Momento"])
momentos_disponibles = [momento for momento in ETIQUETAS_MOMENTOS if momento in momentos_consolidado]


tab1, tab2 = st.tabs(["Marco de Calidad", "Análisis de dimensiones"])

with tab1:
    st.write("Los resultados se presentan en ocho dimensiones, con una escala de 1A a 5.")
    if not momentos_disponibles:
        st.info("El consolidado no tiene mediciones disponibles.")
    else:
        df_radar = df[df["Momento"].isin(momentos_disponibles)].rename(columns={"codigo_ie": "Código IE"})
        codigos_disponibles = set(df_radar["Código IE"])
        opciones_codigos = [codigo for codigo in obtener_opciones_codigos(df_radar) if codigo in codigos_disponibles]
        codigos_seleccionados = st.multiselect(
            "Instituciones o resúmenes del consolidado",
            opciones_codigos,
            default=opciones_codigos[:1],
            key="marco_bucaramanga_instituciones",
            placeholder="Selecciona para ver el radar",
        )
        momentos_seleccionados = st.multiselect(
            "Mediciones del radar",
            momentos_disponibles,
            default=momentos_disponibles,
            format_func=lambda momento: (
                ETIQUETAS_MOMENTOS[momento]
                .replace(" · junio ", " jun. ")
                .replace(" · diciembre ", " dic. ")
            ),
        )
        if not momentos_seleccionados:
            st.info("Selecciona al menos una medición para ver el radar.")
        for codigo in codigos_seleccionados:
            datos_codigo = df_radar[
                (df_radar["Código IE"] == codigo) & df_radar["Momento"].isin(momentos_seleccionados)
            ]
            series, categorias = obtener_datos_pretest_posttest(datos_codigo, momentos_seleccionados)
            if series:
                fig = crear_grafico_radar(
                    series, categorias, codigo, etiquetas=ETIQUETAS_MOMENTOS, colores=COLORES_RADAR
                )
                st.plotly_chart(fig, key=f"marco_bucaramanga_radar_{codigo}")
            elif momentos_seleccionados:
                st.info(f"No hay mediciones en los períodos elegidos para {codigo}.")

with tab2:
    if not momentos_disponibles:
        st.info("El consolidado no tiene mediciones disponibles.")
    else:
        instituciones = df[~df["codigo_ie"].isin(OPCIONES_INICIALES)]
        for numero, dimension in enumerate(DIMENSIONES, start=1):
            with st.expander(f"{numero}. {dimension}"):
                niveles = instituciones.pivot(
                    index="codigo_ie", columns="Momento", values=f"Dimensión {numero}"
                )
                etiquetas = {
                    momento: ETIQUETAS_MOMENTOS[momento]
                    for momento in momentos_disponibles
                    if momento in niveles and niveles[momento].isin(ESCALA_NIVELES).any()
                }
                if etiquetas:
                    fig = barras_pretest_postest(niveles, etiquetas, mostrar_conteos=True)
                    st.plotly_chart(fig, config=chart_config, key=f"marco_bucaramanga_distribucion_{numero}")
                else:
                    st.info("No hay puntajes de instituciones para esta dimensión.")


st.markdown("---")
st.write(
    "© 2026 Universidad del Norte"
)

# Formatear el HTML con las imágenes convertidas a base64
formatted_footer = FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64)

# Mostrar el footer en Streamlit
st.markdown(formatted_footer, unsafe_allow_html=True)
