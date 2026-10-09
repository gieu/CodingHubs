import pandas as pd
import streamlit as st

from actions.observaciones_2026_actions import (
    instantaneas,
    observaciones_generales,
    observaciones_ti,
)
from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import header
from utils.chart_config import get_chart_config

chart_config = get_chart_config()
OBSERVACIONES_YEAR = 2026


header("#282255")
st.markdown("""
<style>
.footer {position: static !important; height: auto !important; margin-top: 2rem; padding: 1rem 0;}
.block-container {padding-bottom: 2rem !important;}
</style>
""", unsafe_allow_html=True)
st.title(f"Observaciones de aula {OBSERVACIONES_YEAR}")
st.caption(f"Seguimiento de las observaciones de aula de la vigencia {OBSERVACIONES_YEAR}")


CSV_URL_1 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQcfm9v6gG5wBoIhmIaFYlmH3lN-n1xTIs9NqYY9D_ynMIAWB-4qZMoFA43cogaZHLsZwhLcyBmyU-j/pub?gid=719223759&single=true&output=csv"
CSV_URL_2 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTU9IGnFp4vidgKKcvMj8dJfkTHQkDMvkswo1O7wvcTZb9dGT41iDaXAPBFBtVpr2oP-xeLh1IkYXM8/pub?gid=884233825&single=true&output=csv"
CSV_URL_3 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRlTUaCvb5Nmsd7m4IvXfBghCP_7si-VwrjtkubfrrWLN6PsWfGDMdBX91uCP8e9kh0ASntvU79U7_3/pub?gid=2039031145&single=true&output=csv"
CSV_URL_4 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSbReSZM6d4dLqOk_N5_h-8xXcvW55-6OY2iRt9cT2jTvt3jokCo7Ja5sibEDlYZSKywrc9WgSxl5ad/pub?output=csv"


# --- Cargar Datos con Cache ---
@st.cache_data(ttl=600)
def load_data(file):
    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        st.warning("No se pudo cargar una fuente de observaciones. Los demás datos siguen disponibles.")
        return pd.DataFrame()


df_ti_instantaneas = load_data(CSV_URL_1)
df_stem_instantaneas = load_data(CSV_URL_2)

df_ti_generales = load_data(CSV_URL_3)
df_stem_generales = load_data(CSV_URL_4)


def mostrar_datos(df, titulo):
    # Hide identifying and collection metadata only in the displayed table.
    columnas_ocultas = [
        "nombre_docente", "correo_docente", "email", "ip", "direccion_ip",
        "tipo_respuesta", "progreso", "finalizado", "idioma",
    ]
    with st.expander(titulo):
        st.dataframe(df.drop(columns=columnas_ocultas, errors="ignore"), width="stretch")


def mostrar_observaciones(df_instantaneas, df_generales, especialidad=None):
    if not df_instantaneas.empty:
        instantaneas(df_instantaneas.copy())
        mostrar_datos(df_instantaneas, "Ver datos de instantáneas")
    else:
        st.info("No hay datos de instantáneas disponibles para esta selección.")
    if not df_generales.empty:
        observaciones_generales(df_generales.copy())
        if especialidad == "TI":
            observaciones_ti(df_generales.copy())
        mostrar_datos(df_generales, "Ver datos generales")
    else:
        st.info("No hay observaciones generales disponibles para esta selección.")


tab1, tab2, tab3 = st.tabs(["Clases STEM", "Clases TI", "Todas las clases"])

with tab1:
    st.header("Observaciones STEM")
    mostrar_observaciones(df_stem_instantaneas, df_stem_generales, "STEM")

with tab2:
    st.header("Observaciones TI")
    mostrar_observaciones(df_ti_instantaneas, df_ti_generales, "TI")

with tab3:
    st.header("Observaciones Todas las Clases")
    combined_instantaneas = pd.concat(
        [df_stem_instantaneas.assign(tipo_clase="STEM"), df_ti_instantaneas.assign(tipo_clase="TI")],
        ignore_index=True,
    )
    combined_generales = pd.concat(
        [df_stem_generales.assign(tipo_clase="STEM"), df_ti_generales.assign(tipo_clase="TI")],
        ignore_index=True,
    )
    mostrar_observaciones(combined_instantaneas, combined_generales)


st.markdown("---")
st.write(
    f"© {OBSERVACIONES_YEAR} Colombia Programa - Ministerio de Tecnologías de la Información y las Comunicaciones (MinTIC)"
)

# Formatear el HTML con las imágenes convertidas a base64
formatted_footer = FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64)

# Mostrar el footer en Streamlit
st.markdown(formatted_footer, unsafe_allow_html=True)
