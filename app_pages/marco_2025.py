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
    obtener_datos_pretest_posttest,
    obtener_opciones_codigos,
    centrar_texto,
)
from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import header
from constants.marco_constants import TEXTO, TITULO, CODIGO_IE_NOMBRES
from utils.chart_config import get_chart_config

chart_config = get_chart_config()
centrar_texto(TITULO, "h1")


header("#282255")


CONSOLIDADO_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6Ql44xab2MHwi7PcPIa9nvMERf6oUTWktc5W6RG5KvhEP9SPPb_a638vdDPoWkTg_x8ovxt_RP9Xl/pub?output=csv"
DIMENSION_3_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQDS5KB6oesIgGpY7swU6CkWRwe36WYtjkZLI89GtlnZtE83DRjU7ZMOlJOvEaRu6e_1ce1FuSivOb5/pub?output=csv"
DIMENSION_7_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTdcYyV9ymYeuzRW29Kbb5lfBhNJB7Hgdrv9HqQJ6BhGJlBdDtLAHnizW_xwGWutkXwq4j3pbOTgd2w/pub?gid=1300816516&single=true&output=csv"
DIMENSION_8_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSllgD0avi01h8HvSPxAzikOSByy3BrEdXnDsOLIe78Q9-yOgU2o-Q4YBLngZ_VcVBlKC3DY6FQl8-m/pub?gid=618864730&single=true&output=csv"

# --- Cargar Datos con Cache ---
@st.cache_data(ttl=600)
def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    return df


df = load_data(CONSOLIDADO_URL)

dimension_3_df = load_data(DIMENSION_3_URL)
dimension_7_df = load_data(DIMENSION_7_URL)
dimension_8_df = load_data(DIMENSION_8_URL)

dimensiones = {
    "Dimensión 3": {
        "data": dimension_3_df,
        "clean_names": {
            "nivel_importancia_pc": "Importancia PC",
            "nivel_pped_frecuencia": "Frecuencia Prácticas Pedagógicas",
            "nivel_ap_autonomo_frecuencia": "Aprendizaje Autónomo Frecuencia",
            "nivel_pc_alfabetizacion": "PC Alfabetización",
            "nivel_pped_proporcion": "Prácticas Pedagógicas Proporción",
            "nivel_ap_autonomo_proporcion": "Aprendizaje Autónomo Proporción",
            "nivel_puntaje_PC": "Puntaje PC",
            "nivel_autoeficacia_pc": "Autoeficacia PC",
            "nivel_autoeficacia_pedagogica": "Autoeficacia Pedagógica",
            "nivel_planeacion": "Planeación",
            "nivel_adaptación enseñanza": "Adaptación Enseñanza",
            "nivel_trabajo_colaborativo": "Trabajo Colaborativo",
            "nivel_redes_inter": "Redes Inter",
            "codigo_ie": "Código IE",
        },
    },
        "Dimensión 7": {
        "data": dimension_7_df,
        "clean_names": {
            "nivel_act_pc_participa": "Participa en actividades PC",
            "nivel_reconoce_valor": "Reconoce Valor PC",
            "nivel_puntaje_PC_estudiante": "Puntaje PC Estudiante",
            "nivel_conceptos_habilidades": "Autoeficacia: Conceptos y Habilidades",
            "nivel_problemas_comp": "Autoeficacia: Problemas Computacionales",
            "nivel_capacidad_decidir": "Capacidad de Decidir",
            "nivel_sentir": "Afecto clases PC",
            "nivel_hacer": "Participación clases PC",
            "nivel_dif_genero": "Diferencias por Género",
            "nivel_dif_discapacidad": "Diferencias Discapacidad",
            "nivel_no_identifica": "No Identifican Brechas",
            "nivel_analizan_brechas_con_datos": "Analizan Brechas con Datos",
            "codigo_ie": "Código IE",
            },
        },
    "Dimensión 8": {
        "data": dimension_8_df,
        "clean_names": {
            "nivel_practicas_frecuencia": "Frecuencia Prácticas",
            "nivel_acciones_proporcion": "Proporción Acciones",
            "nivel_analizan_brechas_con_datos": "Analizan Brechas con Datos",
            "nivel_practicas_proporcion": "Proporción Prácticas",
            "nivel_disposicion": "Disposición",
            "nivel_mentoria_yo": "Mentoría: autopercepción",
            "nivel_mentoria_otros": "Mentoría: acciones frente a otros",
            "nivel_espacios_reflexion": "Espacios Reflexión",
            "nivel_no_identifica": "No Identifican Brechas",
            "nivel_nunca_analizan": "Nunca Analizan",
            "nivel_frecuencia_puntual": "Frecuencia Puntual",
            "nivel_frecuencia_periodica": "Frecuencia Periódica",
            "codigo_ie": "Código IE",
        },
    }
}


tab1, tab2 = st.tabs(["Marco de Calidad 2025", "Análisis de dimensiones"])

with tab1:
    st.markdown("---")
    st.write(TEXTO)

    opciones_codigos_IE = obtener_opciones_codigos(df)
    codigos_selececionados = st.multiselect(
        "Seleccione los códigos de IE que desea visualizar la comparativa de Pretest y Posttest",
        opciones_codigos_IE,
    )

    if codigos_selececionados:
        # Obtener los datos de Pretest y Posttest selecionados
        df_seleccionados = df[df["Código IE"].isin(codigos_selececionados)]

        for codigo in codigos_selececionados:
            datos_codigo = df_seleccionados[df_seleccionados["Código IE"] == codigo]

            pretest_numeric, posttest_numeric, categorias = (
                obtener_datos_pretest_posttest(datos_codigo)
            )

            if pretest_numeric is not None and posttest_numeric is not None:
                fig = crear_grafico_radar(
                    pretest_numeric, posttest_numeric, categorias, codigo
                )
                st.plotly_chart(fig, config=get_chart_config(), key=random.random())
            else:
                st.write(
                    f"Datos incompletos para {codigo}. Se requieren tanto Pretest como Posttest."
                )
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
            dim_number = dimension.split()[-1]

            fig = barras_pretest_postest(
                dim_df,
                value_cols={
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


st.markdown("---")
st.write(
    "© 2025 Colombia Programa - Ministerio de Tecnologías de la Información y las Comunicaciones (MinTIC)"
)

# Formatear el HTML con las imágenes convertidas a base64
formatted_footer = FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64)

# Mostrar el footer en Streamlit
st.markdown(formatted_footer, unsafe_allow_html=True)
