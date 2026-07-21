from io import StringIO
import os

import pandas as pd
import requests
import streamlit as st
from actions.pares_analisis import (
    bar_plots_categorical,
    box_plots,
    correlation_plot,
    scatter_plot,
)
from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import header
from utils.chart_config import get_chart_config

chart_config = get_chart_config()


header("#4A90E2")


DEPLOY_ENV = os.getenv("DEPLOY_ENV")

@st.cache_data(ttl=300)
def load_data(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return pd.read_csv(StringIO(r.text))
CSV_URL_1 = "https://docs.google.com/spreadsheets/d/1yMi3ik5jPO-Ies3mc-VKMkHxG3cZ8F5WETldG8JhPUw/gviz/tq?tqx=out:csv"

df_evaluacion_pares = load_data(CSV_URL_1)
tab1, tab2, tab3 = st.tabs(
    ["Evaluación de Estudiantes", "Caracterización de Estudiantes", "Correlaciones"]
)

# st.dataframe(df_filtrado, use_container_width=True)
nombres_mostrar = {
    "apoyo": "Apoyo institucional",
    "frustracion": "Frustración",
    "demandas": "Demandas",
    "redes_inter": "Redes interinstitucionales",
    "trabajo_colaborativo": "Trabajo colaborativo",
    "sentido_comunidad": "Sentido de comunidad",
    "disposicion": "Disposición para colaborar",
    "mentoria_yo": "Mentoría intrínseca",
    "mentoria_otros": "Mentoría extrínseca",
    "autoeficacia_pc": "Autoeficacia PC",
    "autoeficacia_pedagogica": "Autoeficacia Pedagógica",
    "autoeficacia_tecnologica": "Autoeficacia Tecnológica",
    "planeacion": "Enseñanza centrada - Planeación",
    "adaptación enseñanza": "Enseñanza centrada - Adaptación",
    "influencia": "Influencia en estudiantes",
    "eficacia_col": "Eficacia Colectiva",
    "puntaje_PC": "Puntaje Conocimiento",
    "puntaje_PC_par": "Puntaje Conocimiento (Par)",
    "zona_base": "Zona",
    "sexo_asistencia": "Género Par",
    "sexo": "Género",
    "categoria_2025_base": "Categoría Docente 2025",
    "razon_participacion": "Razón de participación",
    "total_horas_2025_formacion": "Horas de formación 2025",
    "total_horas_de_mentoria_formacion": "Horas de mentoría 2025",
    "total_mentorias_formacion": "Número de mentorías 2025",
    "num_usos_guia_bitacora": "Usos Guía Bitácora",
    "horas_2024_formacion": "Horas de formación 2024",
    "categoria_2024_base": "Categoría Docente 2024",
    "cant_clases_pc": "Cantidad de clases de PC",
    "grado": "Grado",
    "discapacidad": "Discapacidad",
    "nivel": "Nivel",
    "conceptos_habilidades": "Conceptos y Habilidades",
    "problemas_comp": "Resolución de Problemas de Computación",
    "sentir": "Afecto Clases PC",
    "hacer": "Participación Clases PC",
    "capacidad_decidir": "Capacidad de Decidir",
    "puntaje_PC_estudiante": "Puntaje Conocimiento Estudiantes",
    "pc_alfabetizacion": "PC Alfabetización",
}

df_evaluacion_pares["sexo_asistencia"] = df_evaluacion_pares[
    "sexo_asistencia"
].str.title()

with tab1:
    st.subheader("Evaluación de Estudiantes")

    # Things to plot
    escalas = [
        "conceptos_habilidades",
        "problemas_comp",
        "sentir",
        "hacer",
        "capacidad_decidir",
        "puntaje_PC_estudiante",
    ]

    # Columnas filtrables
    columnas_filtrables = ["sexo", "sexo_asistencia", "nivel"]

    col1, col2 = st.columns(2)
    col1.markdown("### Filtros")
    df_filtrado = df_evaluacion_pares.copy()
    filtros = {}
    for columna in columnas_filtrables:
        opciones = df_filtrado[columna].dropna().unique().tolist()
        opciones.sort()
        columna_clean = nombres_mostrar[columna]
        seleccion = col1.multiselect(
            f"Filtrar por {columna_clean}:", opciones, default=None
        )
        filtros[columna] = seleccion
    for columna, seleccion in filtros.items():
        if seleccion:
            df_filtrado = df_filtrado[df_filtrado[columna].isin(seleccion)]

    col2.markdown("### Configuración de Gráfica")

    x_axis = col2.selectbox(
        "Selecciona la variable para el eje X:",
        options=[
            None,
            "cant_clases_pc",
            "sexo",
            "grado",
            "discapacidad",
            "nivel",
            "sexo_asistencia",
        ],
        format_func=lambda x: nombres_mostrar[x] if x else "Ninguno",
        index=0,
    )
    color_by = col2.selectbox(
        "Selecciona la variable para el color:",
        options=[
            None,
            "cant_clases_pc",
            "sexo",
            "grado",
            "discapacidad",
            "nivel",
            "sexo_asistencia",
        ],
        format_func=lambda x: nombres_mostrar[x] if x else "Ninguno",
        index=0,
    )

    st.markdown("### Selección de Escalas")

    grafica_seleccionada = st.multiselect(
        "Selecciona las escalas a graficar:",
        options=escalas,
        format_func=lambda x: nombres_mostrar[x],
    )

    if "Todas" in grafica_seleccionada or not grafica_seleccionada:
        escalas_a_graficar = escalas
    else:
        escalas_a_graficar = grafica_seleccionada
    st.markdown("### Gráficas")

    box_plots(
        df_filtrado,
        escalas_a_graficar,
        x_axis=x_axis,
        color=color_by,
        clean_names=nombres_mostrar,
    )

with tab2:
    # Columnas filtrables
    columnas_filtrables = ["sexo", "sexo_asistencia", "nivel"]

    col1, col2, col3 = st.columns(3)
    col1.markdown("### Filtros")
    df_filtrado = df_evaluacion_pares.copy()
    filtros = {}
    for columna in columnas_filtrables:
        opciones = df_filtrado[columna].dropna().unique().tolist()
        opciones.sort()
        columna_clean = nombres_mostrar[columna]
        seleccion = col1.multiselect(
            f"Filtrar por {columna_clean}:",
            opciones,
            default=None,
            key=f"tab2_{columna}",
        )
        filtros[columna] = seleccion
    for columna, seleccion in filtros.items():
        if seleccion:
            df_filtrado = df_filtrado[df_filtrado[columna].isin(seleccion)]

    escalas_categoricas = [
        "cant_clases_pc",
        "sexo",
        "grado",
        "discapacidad",
        "nivel",
        "sexo_asistencia",
    ]

    col2.markdown("### Dividir Gráficas Por")
    color_by_cat = col2.selectbox(
        "Selecciona la variable para dividir:",
        options=[
            None,
            "cant_clases_pc",
            "sexo",
            "grado",
            "discapacidad",
            "nivel",
            "sexo_asistencia",
        ],
        format_func=lambda x: nombres_mostrar[x] if x else "Ninguno",
        index=0,
        key="tab2_color_by_cat",
    )

    col3.markdown("### Selección de Escalas")

    escalas_categoricas_a_graficar = col3.multiselect(
        "Selecciona las escalas categóricas a graficar:",
        options=escalas_categoricas,
        format_func=lambda x: nombres_mostrar[x],
        key="tab2_grafica_seleccionada_cat",
    )

    if "Todas" in escalas_categoricas_a_graficar or not escalas_categoricas_a_graficar:
        escalas_categoricas_a_graficar = escalas_categoricas
    else:
        escalas_categoricas_a_graficar = escalas_categoricas_a_graficar

    st.markdown("### Gráficas para Variables Categóricas")
    bar_plots_categorical(
        df_filtrado,
        escalas_categoricas_a_graficar,
        color=color_by_cat,
        clean_names=nombres_mostrar,
    )

    with tab3:
        st.subheader("Análisis de Correlación entre Pares y Estudiantes")

        # columnas correlaciones (docente)
        columnas_docente = [
            "apoyo",
            "frustracion",
            "demandas",
            "redes_inter",
            "trabajo_colaborativo",
            "sentido_comunidad",
            "disposicion",
            "mentoria_yo",
            "mentoria_otros",
            "autoeficacia_pedagogica",
            "autoeficacia_tecnologica",
            "autoeficacia_pc",
            "planeacion",
            "adaptación enseñanza",
            "influencia",
            "eficacia_col",
            "pc_alfabetizacion",
            "puntaje_PC_par",
        ]

        # columnas correlaciones (estudiante)
        columnas_estudiante = [
            "conceptos_habilidades",
            "problemas_comp",
            "sentir",
            "hacer",
            "capacidad_decidir",
            "puntaje_PC_estudiante",
        ]

        st.markdown("### Matriz de Correlación Total")
        correlation_plot(
            df_filtrado,
            columnas_docente + columnas_estudiante,
            clean_names=nombres_mostrar,
        )

        # Escoger columnas para correlacion
        col1, col2 = st.columns(2)
        col1.markdown("### Selección de Escalas Docente")
        escalas_docente_seleccionadas = col1.multiselect(
            "Selecciona las escalas del docente para correlacionar:",
            options=columnas_docente,
            format_func=lambda x: nombres_mostrar[x],
            key="tab3_escalas_docente",
        )
        col2.markdown("### Selección de Escalas Estudiante")
        escalas_estudiante_seleccionadas = col2.multiselect(
            "Selecciona las escalas del estudiante para correlacionar:",
            options=columnas_estudiante,
            format_func=lambda x: nombres_mostrar[x],
            key="tab3_escalas_estudiante",
        )

        st.markdown("### Gráficas de Correlación")
        if (
            len(escalas_docente_seleccionadas) + len(escalas_estudiante_seleccionadas)
            < 2
        ):
            st.info(
                "Por favor, selecciona selecciona al menos dos escalas para ver la gráfica de correlación."
            )
        else:
            correlation_plot(
                df_filtrado,
                escalas_docente_seleccionadas + escalas_estudiante_seleccionadas,
                clean_names=nombres_mostrar,
            )

        if (
            len(escalas_docente_seleccionadas) + len(escalas_estudiante_seleccionadas)
            > 5
        ):
            st.warning(
                "Para evitar sobrecarga, las gráficas de dispersión solo se mostrarán cuando se seleccionen 5 o menos escalas en total."
            )
        elif not escalas_docente_seleccionadas or not escalas_estudiante_seleccionadas:
            st.info(
                "Por favor, selecciona al menos una escala tanto para docentes como para estudiantes para ver las gráficas de dispersión."
            )
        else:
            st.markdown("### Gráficas de Dispersión entre Escalas Seleccionadas")
            for docente_scale in escalas_docente_seleccionadas:
                for estudiante_scale in escalas_estudiante_seleccionadas:
                    scatter_plot(
                        df_filtrado,
                        docente_scale,
                        estudiante_scale,
                        clean_names=nombres_mostrar,
                    )


st.markdown("---")
st.write(
    "© 2025 Colombia Programa - Ministerio de Tecnologías de la Información y las Comunicaciones (MinTIC)"
)

# Formatear el HTML con las imágenes convertidas a base64
formatted_footer = FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64)

# Mostrar el footer en Streamlit
st.markdown(formatted_footer, unsafe_allow_html=True)
