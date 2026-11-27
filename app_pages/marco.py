import os
import random

import pandas as pd
import streamlit as st
from actions.marco_actions import (
    barras_pretest_postest,
    conteo_estado,
    crear_grafico_radar,
    grafica_estado,
    heatmap,
    mapa_meta_3a,
    MOMENTOS_RADAR,
    obtener_datos_pretest_posttest,
    obtener_opciones_codigos,
    centrar_texto,
)
from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import header
from constants.marco_constants import TEXTO, TITULO, CODIGO_IE_NOMBRES, ETIQUETAS_INDICADORES
from utils.chart_config import get_chart_config

chart_config = get_chart_config()
centrar_texto(TITULO, "h1")


header("#282255")


CONSOLIDADO_URL = "https://docs.google.com/spreadsheets/d/1SsigQpvMuQSaqQrxfX550VvDZcbaKuYi/export?format=csv"
DIMENSION_1_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR1FBv9IicEsBDsANqyg5PxO8L6XYWTC0RV77KwmB-j7e9Nw1sRuCjtpHxeWn630u0flW5joYSv4jKK/pub?gid=1924393472&single=true&output=csv"
DIMENSION_2_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSnTVsXcL0Ag4rEfO0EmKu3NO-qPgnAlj1smalQE_CQlcop-00LyQ1KHemBf4xUp2CaLmbukJVz7SQw/pub?gid=586390731&single=true&output=csv"
DIMENSION_3_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQDS5KB6oesIgGpY7swU6CkWRwe36WYtjkZLI89GtlnZtE83DRjU7ZMOlJOvEaRu6e_1ce1FuSivOb5/pub?output=csv"
DIMENSION_4_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTNiRR1ZgsORsR0gMcDiIMnvKvz5BkJbsiGYao8PUqqdmPDTKCTZSIG1QwGkzjiQ8lwrJs8ZJ4gYUE7/pub?gid=1953862269&single=true&output=csv"
DIMENSION_5_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSZNZdE2EyuU8cwAQo8npoq1y-Vc2TeXlCwSqqyyerdjI8Q-fec9eJzqj9FWSH_txjgNgnU6UFyXZuU/pub?gid=879563828&single=true&output=csv"
DIMENSION_6_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRvjxEMDkL5lf_f286mSugQ4feXBwRjqyA6Bp-bi6gKZLX-NOfpV0ZIqCh021sw-sXfuSFcnkYsJz0O/pub?gid=1726025465&single=true&output=csv"
DIMENSION_7_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTdcYyV9ymYeuzRW29Kbb5lfBhNJB7Hgdrv9HqQJ6BhGJlBdDtLAHnizW_xwGWutkXwq4j3pbOTgd2w/pub?gid=1300816516&single=true&output=csv"
DIMENSION_8_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSllgD0avi01h8HvSPxAzikOSByy3BrEdXnDsOLIe78Q9-yOgU2o-Q4YBLngZ_VcVBlKC3DY6FQl8-m/pub?gid=618864730&single=true&output=csv"

# --- Cargar Datos con Cache ---
@st.cache_data(ttl=600)
def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    return df

df = load_data(CONSOLIDADO_URL)
momentos_2023 = df["Momento"].isin(("pre_2023", "post_2023"))
df.loc[momentos_2023, df.columns[2:]] = df.loc[momentos_2023, df.columns[2:]].replace({"3": "3B", "3.0": "3B", 3: "3B"})
dimension_1_df = load_data(DIMENSION_1_URL)
dimension_2_df = load_data(DIMENSION_2_URL)
dimension_3_df = load_data(DIMENSION_3_URL)
dimension_4_df = load_data(DIMENSION_4_URL)
dimension_5_df = load_data(DIMENSION_5_URL)
dimension_6_df = load_data(DIMENSION_6_URL)
dimension_7_df = load_data(DIMENSION_7_URL)
dimension_8_df = load_data(DIMENSION_8_URL)

dimensiones = {
    "1. Liderazgo y visión.": {
        "data": dimension_1_df,
        "clean_names": ETIQUETAS_INDICADORES[1],
    },
    "2. Plan de área": {
        "data": dimension_2_df,
        "clean_names": ETIQUETAS_INDICADORES[2],
    },
    "3. Enseñanza, aprendizaje y evaluación": {
        "data": dimension_3_df,
        "clean_names": ETIQUETAS_INDICADORES[3],
    },
    "4. Desarrollo profesional del personal docente": {
        "data": dimension_4_df,
        "clean_names": ETIQUETAS_INDICADORES[4],
    },
    "5. Equidad, diversidad e inclusión": {
        "data": dimension_5_df,
        "clean_names": ETIQUETAS_INDICADORES[5],
    },
    "6. Proyección en educación terciaria": {
        "data": dimension_6_df,
        "clean_names": ETIQUETAS_INDICADORES[6],
    },
    "7. Impacto en los resultados": {
        "data": dimension_7_df,
        "clean_names": ETIQUETAS_INDICADORES[7],
    },
    "8. Equidad de género": {
        "data": dimension_8_df,
        "clean_names": ETIQUETAS_INDICADORES[8],
    },
}


tab1, tab2, tab_meta = st.tabs(["Marco de Calidad", "Análisis de dimensiones", "Meta 3A o más"])

with tab1:
    st.markdown("---")
    st.write(TEXTO)

    df_radar = df.rename(columns={'codigo_ie': 'Código IE'})
    opciones_codigos_IE = obtener_opciones_codigos(df_radar)
    codigos_selececionados = st.multiselect(
        "Seleccione los códigos de IE que desea visualizar la comparativa de Pretest y Posttest",
        opciones_codigos_IE,
    )
    momentos_seleccionados = st.multiselect(
        "Seleccione los momentos que desea graficar",
        MOMENTOS_RADAR,
        default=MOMENTOS_RADAR,
    )

    if codigos_selececionados and momentos_seleccionados:
        # Obtener los datos de Pretest y Posttest selecionados
        df_seleccionados = df_radar[df_radar["Código IE"].isin(codigos_selececionados)]
        

        for codigo in codigos_selececionados:
            datos_codigo = df_seleccionados[df_seleccionados["Código IE"] == codigo]

            series_momentos, categorias = obtener_datos_pretest_posttest(datos_codigo)

            if series_momentos is not None and categorias is not None:
                fig = crear_grafico_radar(
                    series_momentos,
                    categorias,
                    codigo,
                    momentos_seleccionados,
                )
                st.plotly_chart(fig)
            else:
                st.write(
                    f"No hay momentos disponibles para generar el grÃ¡fico de {codigo}."
                )
    elif codigos_selececionados:
        st.write("Seleccione al menos un momento para generar el gráfico.")
    else:
        st.write(
            "Por favor, seleccione al menos un código de IE para generar el gráfico."
        )

with tab2:

    dimension_priorizada = st.toggle("Prioriza la dimensión")

    for dimension, info in dimensiones.items():
        dim_df = info["data"]
        
        clean_names = info["clean_names"]


        if dimension_priorizada:
            dim_df = dim_df[dim_df["dim_priorizada"] == "Sí"]

        with st.expander("Análisis de dimensión: " + dimension, expanded=False):
            dim_number = dimension.split('.')[0]
            dim_values = df.pivot(
                index="codigo_ie",
                columns="Momento",
                values=df.columns[int(dim_number) + 1],
            )
            for momento in ("pre_2023", "post_2023"):
                column = f"dim{dim_number}_{momento}"
                dim_df[column] = dim_df["codigo_ie"].map(dim_values[momento])

            fig = barras_pretest_postest(
                dim_df,
                value_cols={
                    f"dim{dim_number}_pre_2023": "Pretest 2023",
                    f"dim{dim_number}_post_2023": "Postest 2023",
                    f"dim{dim_number}_pre_2024": "Pretest 2024",
                    f"dim{dim_number}_post_2024": "Postest 2024",
                    f"dim{dim_number}_post_2025": "Postest 2025",
                },
            )
            st.plotly_chart(fig, config=get_chart_config(), key=random.random())

            fig = conteo_estado(dim_df)
            st.plotly_chart(fig, config=get_chart_config(), key=random.random())

            fig = grafica_estado(dim_df, clean_names)
            st.plotly_chart(fig, config=get_chart_config(), key=random.random())

            fig = heatmap(dim_df, clean_names, list(clean_names.keys()), CODIGO_IE_NOMBRES)
            st.plotly_chart(fig, config=get_chart_config(), key=random.random())


with tab_meta:
    st.subheader("¿Cómo ha evolucionado el cumplimiento de la meta?")
    st.caption("Porcentaje de colegios con nivel 3A, 3B, 4 o 5 entre los evaluados en cada dimensión y momento.")
    nombres_dimensiones = [nombre.split(". ", 1)[1].rstrip(".") for nombre in dimensiones]
    st.plotly_chart(mapa_meta_3a(df, nombres_dimensiones), config=chart_config, key="marco_meta_3a")

st.markdown("---")
st.write(
    "© 2026 Universidad del Norte"
)

# Formatear el HTML con las imágenes convertidas a base64
formatted_footer = FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64)

# Mostrar el footer en Streamlit
st.markdown(formatted_footer, unsafe_allow_html=True)
