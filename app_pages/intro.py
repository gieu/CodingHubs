import streamlit as st
import pandas as pd
import plotly.express as px # type: ignore

from constants.intro_constants import PROYECTO_TITULO, PROYECTO_HEADER, OBJETIVO_TITULO, OBJETIVO_TEXTO, COMPONENTES
from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import LOGO_NAVBAR_BASE64, HIDE_STREAMLIT_STYLE, NAVBAR_TEMPLATE, generar_css_personalizado
from actions.intro_actions import mostrar_imagen, mostrar_componente, centrar_texto

# Configuración de la página
st.set_page_config(
    layout="wide",
)

# Ocultar elementos de Streamlit
st.markdown(HIDE_STREAMLIT_STYLE, unsafe_allow_html=True)

# Generar el CSS personalizado con el color deseado
color_fondo_navbar = "#1DB2E8"  # Cambia este valor según lo necesites
custom_css = generar_css_personalizado(color_fondo_navbar)

# Aplicar el CSS en Streamlit
st.markdown(custom_css, unsafe_allow_html=True)

# Navbar personalizado con logo
navbar = NAVBAR_TEMPLATE.format(LOGO_NAVBAR_BASE64=LOGO_NAVBAR_BASE64)
# Mostrar el navbar
st.markdown(navbar, unsafe_allow_html=True)

centrar_texto(PROYECTO_TITULO, "h1")
st.subheader(PROYECTO_HEADER, "h3")
st.markdown("---")

# Objetivo del Proyecto
st.header(OBJETIVO_TITULO)
st.subheader(OBJETIVO_TEXTO)

# Mostrar cada componente
for componente in COMPONENTES.values():
    mostrar_componente(componente["titulo"], componente["imagen"], componente["secciones"])

# Pie de página
st.markdown("---")
st.write("© 2025 Colombia Programa - Ministerio de Tecnologías de la Información y las Comunicaciones (MinTIC)")

# Formatear el HTML con las imágenes convertidas a base64
formatted_footer = FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64)

# Mostrar el footer en Streamlit
st.markdown(formatted_footer, unsafe_allow_html=True)