import pandas as pd
import streamlit as st

from actions.pares_analisis import (
    bar_plots_categorical,
    bar_plots_numerical,
    box_plots,
)
from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import header
from utils.chart_config import get_chart_config

chart_config = get_chart_config()
header("#282255")

CSV_URL_1 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT4vz317WN2UspAJU401x9OjLPjv1EAyW0zu3mxrOOrO67rmzFiqMH63zYU8bNuwkXZGMcSU5jzbVJG/pub?output=csv"


# --- Cargar Datos con Cache ---
@st.cache_data(ttl=600)
def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    return df


df_evaluacion_pares = load_data(CSV_URL_1)
tab1, tab2 = st.tabs(["Evaluación de Pares", "Característización de Pares"])


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
    "sexo_asistencia": "Género",
    "formacion_pc": "Formación en PC",
    "asignatura_docente": "Asignatura que enseña",
    "razon_participacion": "Razón de participación",
    "total_mentorias_formacion": "Número de mentorías 2025",
    "nivelaciones_total_formacion": "Número de nivelaciones 2025",
    "num_usos_guia_bitacora": "Usos Guía Bitácora",
    "horas_2024_formacion": "Horas de formación 2024",
    "categoria_docente_asistencia": "Categoría Par",
}

with tab1:
    st.subheader("Evaluación de Pares")

    # Things to plot
    escalas = [
        "apoyo",
        "frustracion",
        "demandas",
        "redes_inter",
        "trabajo_colaborativo",
        "sentido_comunidad",
        "disposicion",
        "mentoria_yo",
        "mentoria_otros",
        "autoeficacia_pc",
        "autoeficacia_pedagogica",
        "autoeficacia_tecnologica",
        "planeacion",
        "adaptación enseñanza",
        "influencia",
        "eficacia_col",
        "puntaje_PC",
    ]

    # Preprocess things to group by (color, x axis)

    df_evaluacion_pares["sexo_asistencia"] = (
        df_evaluacion_pares["sexo_asistencia"].fillna("No especifica").str.title()
    )
    df_evaluacion_pares["razon_participacion"] = (
        df_evaluacion_pares["razon_participacion"]
        .map(
            {
                "Ingresé por interés propio en el programa y sus contenidos.": "Interés propio",
                "Ingresé por sugerencia de mis superiores, y tenía interés en el programa.": "Sugerencia de superiores",
                "Ingresé porque fui asignado por mis superiores, aunque no tenía un interés previo.": "Sugerencia de superiores",
            }
        )
        .fillna("Otro")
    )

    # Merge "docente_ti", "docente_stem", "docente_otras", in asignatura_docente, taking as positive non-null values
    def asignatura_docente(row):
        if pd.notna(row["docente_ti"]) and pd.notna(row["docente_stem"]):
            return "Ambas"
        elif pd.notna(row["docente_ti"]):
            return "TI"
        elif pd.notna(row["docente_stem"]):
            return "STEM"
        else:
            return "Otra"

    df_evaluacion_pares["asignatura_docente"] = df_evaluacion_pares.apply(
        asignatura_docente, axis=1
    )

    # Merge "pc_pregrado", "pc_cursos", "pc_posgrado", "pc_otro"  taking as positive non-null values
    def formacion_pc(row):
        if pd.notna(row["pc_pregrado"]) and pd.notna(row["pc_posgrado"]):
            return "Pregrado y Posgrado"
        elif pd.notna(row["pc_pregrado"]):
            return "Pregrado"
        elif pd.notna(row["pc_posgrado"]):
            return "Posgrado"
        else:
            return "Otra"

    df_evaluacion_pares["formacion_pc"] = df_evaluacion_pares.apply(
        formacion_pc, axis=1
    )

    df_evaluacion_pares["categoria_docente_asistencia"] = df_evaluacion_pares[
        "categoria_docente_asistencia"
    ].str.title()

    # Columnas filtrables
    columnas_filtrables = ["sexo_asistencia"]

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
            "sexo_asistencia",
            "razon_participacion",
            "asignatura_docente",
            "formacion_pc",
            "categoria_docente_asistencia",
        ],
        format_func=lambda x: nombres_mostrar[x] if x else "Ninguno",
        index=0,
    )
    color_by = col2.selectbox(
        "Selecciona la variable para el color:",
        options=[
            None,
            "sexo_asistencia",
            "razon_participacion",
            "asignatura_docente",
            "formacion_pc",
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
    columnas_filtrables = ["sexo_asistencia"]

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
        "sexo_asistencia",
        "razon_participacion",
        "asignatura_docente",
        "formacion_pc",
    ]

    escalas_numericas = [
        "num_usos_guia_bitacora",
    ]

    col2.markdown("### Dividir Gráficas Por")
    color_by_cat = col2.selectbox(
        "Selecciona la variable para dividir:",
        options=[
            None,
            "sexo_asistencia",
            "razon_participacion",
            "asignatura_docente",
            "formacion_pc",
            "categoria_docente_asistencia",
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

    escalas_numericas_a_graficar = col3.multiselect(
        "Selecciona las escalas numéricas a graficar:",
        options=escalas_numericas,
        format_func=lambda x: nombres_mostrar[x],
        key="tab2_grafica_seleccionada_num",
    )

    st.divider()

    if "Todas" in escalas_numericas_a_graficar or not escalas_numericas_a_graficar:
        escalas_numericas_a_graficar = escalas_numericas
    else:
        escalas_numericas_a_graficar = escalas_numericas_a_graficar

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

    st.markdown("### Gráficas para Variables Numéricas")
    bar_plots_numerical(
        df_filtrado,
        escalas_numericas_a_graficar,
        color=color_by_cat,
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
