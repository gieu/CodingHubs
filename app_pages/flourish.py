import streamlit as st
from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import  LOGO_NAVBAR_BASE64,HIDE_STREAMLIT_STYLE, NAVBAR_TEMPLATE, generar_css_personalizado
import streamlit.components.v1 as components

# Configuración de la página
st.set_page_config(
    layout="wide",
)
# Ocultar elementos de Streamlit
st.markdown(HIDE_STREAMLIT_STYLE, unsafe_allow_html=True)

# Generar el CSS personalizado con el color deseado
color_fondo_navbar = "#004884"  # Cambia este valor según lo necesites
custom_css = generar_css_personalizado(color_fondo_navbar)

# Aplicar el CSS en Streamlit
st.markdown(custom_css, unsafe_allow_html=True)

# Navbar personalizado con logo
navbar = NAVBAR_TEMPLATE.format(LOGO_NAVBAR_BASE64=LOGO_NAVBAR_BASE64)
# Mostrar el navbar
st.markdown(navbar, unsafe_allow_html=True)

st.title("Visualizaciones interactivas informe 2024")


flourish_url = "https://flo.uri.sh/story/3002860/embed"
components.iframe(flourish_url, width=1000, height=1000, scrolling=True)

# # URL de la visualización publicada en Flourish (modo iframe)
# flourish_url = "https://flo.uri.sh/visualisation/23040150/embed"
# components.iframe(flourish_url, width=800, height=600, scrolling=True)


# Pie de página
st.markdown("---")
st.write("© 2025 Colombia Programa - Ministerio de Tecnologías de la Información y las Comunicaciones (MinTIC)")

# Formatear el HTML con las imágenes convertidas a base64
formatted_footer = FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64)

# Mostrar el footer en Streamlit
st.markdown(formatted_footer, unsafe_allow_html=True)