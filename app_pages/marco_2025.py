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


CONSOLIDADO_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSRVc2rbCoOeSvbw99wbWhECryfq3cvS5YA8HHhnYGKCtLHNGleoGM6wPqde8Qtfg/pub?gid=618340973&single=true&output=csv"
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
        "clean_names": {
            "nivel_importancia_pc": "Importancia PC",
            "nivel_promedio_acciones_largo_plazo": "Acciones a Largo Plazo",
            "nivel_inclusion_explicita_proporcion": "Inclusión Explícita PC",
            "nivel_grados_pc_presente_proporcion": "Grados incluyen PC",
            "nivel_pc_alfabetizacion": "PC Alfabetización",
            "nivel_apoyo": "Apoyo Institucional",
            "nivel_no_frustracion": "Baja Frustración",
            "nivel_trabajo_colaborativo": "Trabajo Colaborativo",
            "nivel_oportunidades_formacion": "Oportunidades de Formación",
            "nivel_seguimiento_vision": "Seguimiento a la Visión Institucional",
            "nivel_consejo_academico": "Rol Consejo Académico",
            "nivel_definicion_ensenanza": "Definición de la Enseñanza",
            "nivel_comunicacion_familias": "Comunicación con Familias",
            "nivel_evidencian_impacto_institucional": "Evidencian Impacto Institucional",
            "nivel_reduccion_impacto_rotacion": "Reducción Impacto Rotación",
            "nivel_induccion_docente": "Inducción Docente",
            "nivel_promueven_alianzas_estrategicas": "Promueven Alianzas Estratégicas",
            "nivel_resaltan_beneficios_alianzas": "Resaltan Beneficios Alianzas",
            "codigo_ie": "Código IE",
        },
    },
    "2. Plan de área": {
        "data": dimension_2_df,
        "clean_names": {
            "nivel_realiza_ajustes_piar": "Ajustes PIAR",
            "nivel_realiza_ajustes_necesidades": "Ajustes Necesidades",
            "nivel_recursos_suficientes_num": "Recursos Suficientes",
            "nivel_inclusion_explicita_proporcion": "Inclusión Explícita",
            "nivel_equipos_proporcion": "Equipos y Software",
            "nivel_responsables_plan_proporcion": "Responsables del Plan",
            "nivel_conexion_areas_proporcion": "Conexión con otras áreas",
            "nivel_grados_pc_presente_proporcion": "Grados incluyen PC",
            "nivel_tema_repite_niveles": "Progresión en niveles (temas se retoman)",
            "nivel_alertas_progresion": "Alertas de Progresión",
            "nivel_percepcion_progresion": "Percepción de Progresión",
            "nivel_frecuencia_actualizacion": "Frecuencia de Actualización",
            "nivel_actividades_incluidas": "Actividades Incluidas",
            "nivel_elementos_evaluacion": "Elementos de Evaluación",
            "nivel_elementos_diseno": "Elementos de Diseño",
            "nivel_cant_adaptaciones": "Cantidad de Adaptaciones Explícitas",
            "nivel_presente_niveles": "Presencia en Niveles",
            "nivel_profes_stem": "Profesores STEM",
            "nivel_mejora_plan": "Mejora del Plan",
            "codigo_ie": "Código IE",
        },
    },
    "3. Enseñanza, aprendizaje y evaluación": {
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
            "nivel_planeacion": "Acompañamiento a estudiantes",
            "nivel_adaptación enseñanza": "Adaptación Enseñanza",
            "nivel_trabajo_colaborativo": "Trabajo Colaborativo",
            "nivel_redes_inter": "Redes Inter",
            "codigo_ie": "Código IE",
        },
    },
    "4. Desarrollo profesional del personal docente": {
        "data": dimension_4_df,
        "clean_names": {
            "nivel_promedio_acciones_largo_plazo": "Acciones a Largo Plazo",
            "nivel_formacion_pc": "Formación en PC - Pares",
            "nivel_planeacion_dllo_proporcion": "Planeación y Desarrollo",
            "nivel_oportunidades_dllo_proporcion": "Oportunidades de Desarrollo",
            "nivel_apoyo": "Apoyo Institucional",
            "nivel_no_demandas": "Carga laboral",
            "nivel_trabajo_colaborativo": "Trabajo Colaborativo",
            "nivel_mentoria_yo": "Mentoría: autopercepción",
            "nivel_mentoria_otros": "Mentoría: acciones frente a otros",
            "nivel_disposicion": "Disposición para colaborar",
            "nivel_oportunidades_formacion": "Oportunidades de Formación",
            "nivel_razon_participacion": "Razón de Participación - Pares",
            "nivel_planeacion_formacion_pc": "Planeación Formación en PC",
            "nivel_registro_formacion_pc": "Registro Formación en PC",
            "nivel_reduccion_impacto_rotacion": "Reducción Impacto Rotación",
            "nivel_induccion_docente": "Inducción Docente",
            "codigo_ie": "Código IE",
        },
    },
    "5. Equidad, diversidad e inclusión": {
        "data": dimension_5_df,
        "clean_names": {
            "nivel_practicas_frecuencia": "Frecuencia Prácticas Docentes",
            "nivel_realiza_ajustes_necesidades": "Ajustes según Necesidades",
            "nivel_realiza_ajustes_piar": "Ajustes según PIAR",
            "nivel_edterciaria_proporcion": "Acciones Institucionales",
            "nivel_practicas_proporcion": "Proporción Prácticas Docentes",
            "nivel_trabajo_colaborativo": "Trabajo Colaborativo",
            "nivel_planeacion": "Acompañamiento a estudiantes",
            "nivel_adaptación enseñanza": "Adaptación Enseñanza",
            "nivel_act_pc_participa": "Participa en actividades PC",
            "nivel_sentir": "Afecto clases PC",
            "nivel_hacer": "Participación clases PC",
            "nivel_identifican_discapacidad": "Identifican Discapacidad",
            "nivel_cant_acciones_inclusion": "Cantidad Acciones Inclusión",
            "nivel_faltan_registros": "Faltan Registros",
            "nivel_faltan_evidencias": "Faltan Evidencias",
            "nivel_incluyen_dua": "Incluyen DUA",
            "nivel_elementos_diseno_total": "Elementos de Diseño Total",
            "nivel_cant_adaptaciones": "Cantidad de Adaptaciones Explícitas",
            "codigo_ie": "Código IE",
        },
    },
    "6. Proyección en educación terciaria": {
        "data": dimension_6_df,
        "clean_names": {
        "nivel_practicas_frecuencia":"Frecuencia Prácticas Docentes",
        "nivel_importancia_pc": "Importancia PC Directivos",
        "nivel_act_pc_participa": "Participa en actividades PC",
        "nivel_edterciaria_proporcion": "Acciones Institucionales",
        "nivel_pc_alfabetizacion": "PC Alfabetización",
        "nivel_practicas_proporcion": "Proporción Prácticas Docentes",
        "nivel_capacidad_decidir": "Capacidad de Decidir",
        "nivel_alianzas":"Alianzas externas",
        "nivel_conexion_areas_proporcion": "Conexión con otras áreas",
        "nivel_equipos_proporcion": "Equipos y software",
        "nivel_recursos_suficientes_num": "Recursos Suficientes",
        "codigo_ie": "Código IE",
        },
    },
    "7. Impacto en los resultados": {
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
    "8. Equidad de género": {
        "data": dimension_8_df,
        "clean_names": {
            "nivel_practicas_frecuencia": "Frecuencia Prácticas",
            "nivel_acciones_proporcion": "Proporción Acciones",
            "nivel_analizan_brechas_con_datos": "Analizan Brechas con Datos",
            "nivel_practicas_proporcion": "Proporción Prácticas",
            "nivel_disposicion": "Disposición para colaborar",
            "nivel_mentoria_yo": "Mentoría: autopercepción",
            "nivel_mentoria_otros": "Mentoría: acciones frente a otros",
            "nivel_espacios_reflexion": "Espacios Reflexión",
            "nivel_no_identifica": "No Identifican Brechas",
            "nivel_nunca_analizan": "Nunca Analizan",
            "nivel_frecuencia_puntual": "Frecuencia Puntual",
            "nivel_frecuencia_periodica": "Frecuencia Periódica",
            "codigo_ie": "Código IE",
        },
    },
}


tab1, tab2 = st.tabs(["Marco de Calidad 2025", "Análisis de dimensiones"])

with tab1:
    st.markdown("---")
    st.write(TEXTO)

    df = df.rename(columns={'codigo_ie': 'Código IE'})
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

            pretest_numeric, posttest_numeric, posttest_2025_numeric, nivel_2025_numeric, categorias = (
                obtener_datos_pretest_posttest(datos_codigo)
            )

            if pretest_numeric is not None and posttest_numeric is not None and posttest_2025_numeric is not None:
                fig = crear_grafico_radar(
                    pretest_numeric, posttest_numeric, posttest_2025_numeric, categorias, codigo, nivel_2025_numeric
                )
                st.plotly_chart(fig)
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
            dim_number = dimension.split('.')[0]

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
