import os

import pandas as pd
import streamlit as st

from actions.observaciones_actions import (
    instantaneas,
    observaciones_generales,
    observaciones_ti,
    observaciones_stem,
)
from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import header
from utils.chart_config import get_chart_config

chart_config = get_chart_config()


header("#282255")


CSV_URL_1 = "https://drive.google.com/uc?export=download&id=1xZe66O9hCFpzYUhfKO88fyYNoWfX4qL-"
CSV_URL_2 = "https://drive.google.com/uc?export=download&id=1uWCQbdTG1MpryCDjRSFYKnvxn24C73vT"
CSV_URL_3 = "https://drive.google.com/uc?export=download&id=1YSvg7u38v7rzYL_JjIEao_ebBo5VeLKI"
CSV_URL_4 = "https://drive.google.com/uc?export=download&id=12YM6-zcvUngMYY2yv1IRzMzP98-6btsU"


# --- Cargar Datos con Cache ---
@st.cache_data(ttl=600)
def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    return df


df_ti_instantaneas = load_data(CSV_URL_1)
df_stem_instantaneas = load_data(CSV_URL_2)

df_ti_generales = load_data(CSV_URL_3)
df_stem_generales = load_data(CSV_URL_4)


tab1, tab2, tab3 = st.tabs(["Clases STEM", "Clases TI", "Todas las clases"])

with tab1:
    st.header("Observaciones STEM")
    df_stem_instantaneas = df_stem_instantaneas.drop(columns=["nombre_docente"])
    instantaneas(df_stem_instantaneas)

    with st.expander("Ver datos de instantáneas"):
        st.dataframe(df_stem_instantaneas)

    observaciones_generales(df_stem_generales)

    with st.expander("Ver datos generales"):
        #Drop columns between "tipo_respuesta" and "idioma"
        cols_to_drop = df_stem_generales.columns[
            df_stem_generales.columns.get_loc("tipo_respuesta")
            + 1 : df_stem_generales.columns.get_loc("idioma")
        ].to_list() + ["nombre_docente"]
        df_stem_generales = df_stem_generales.drop(columns=cols_to_drop)
        st.dataframe(df_stem_generales)

    #observaciones_stem(df_stem_generales)

with tab2:
    st.header("Observaciones TI")
    instantaneas(df_ti_instantaneas)
    df_ti_instantaneas = df_ti_instantaneas.drop(columns=["nombre_docente"])

    with st.expander("Ver datos de instantáneas"):
        st.dataframe(df_ti_instantaneas)

    observaciones_generales(df_ti_generales)

    with st.expander("Ver datos generales"):
        # Drop columns between "unidad" and "idioma"
        # cols_to_drop = df_ti_generales.columns[
        #     df_ti_generales.columns.get_loc("unidad")
        #     + 1 : df_ti_generales.columns.get_loc("idioma")
        # ].to_list() + ["nombre_docente"]
        df_ti_generales = df_ti_generales.drop(columns=cols_to_drop)
        st.dataframe(df_ti_generales)

    observaciones_ti(df_ti_generales)

with tab3:
    st.header("Observaciones Todas las Clases")
    combined_instantaneas = pd.concat(
        [df_stem_instantaneas, df_ti_instantaneas], ignore_index=True
    )
    instantaneas(combined_instantaneas)

    with st.expander("Ver datos de instantáneas"):
        st.dataframe(combined_instantaneas)

    combined_generales = pd.concat(
        [df_stem_generales, df_ti_generales], ignore_index=True
    )
    observaciones_generales(combined_generales)

    with st.expander("Ver datos generales"):
        st.dataframe(combined_generales)


st.markdown("---")
st.write(
    "© 2025 Colombia Programa - Ministerio de Tecnologías de la Información y las Comunicaciones (MinTIC)"
)

# Formatear el HTML con las imágenes convertidas a base64
formatted_footer = FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64)

# Mostrar el footer en Streamlit
st.markdown(formatted_footer, unsafe_allow_html=True)
