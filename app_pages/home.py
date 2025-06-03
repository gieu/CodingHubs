import streamlit as st
from constants.home_constants import TITULO, BANNER_IMG, TEXTO, CSV_URL_COMPONENTE_2,CSV_URL_COMPONENTE_3
from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import  LOGO_NAVBAR_BASE64,HIDE_STREAMLIT_STYLE, NAVBAR_TEMPLATE, generar_css_personalizado
from actions.home_actions import mostrar_imagen, centrar_texto, obtener_datos_nodos, obtener_datos_mapa
from widgets.mapa_widget import dibujar_mapa

# Configuración de la página
st.set_page_config(
    layout="wide",
)
# Ocultar elementos de Streamlit
st.markdown(HIDE_STREAMLIT_STYLE, unsafe_allow_html=True)

# Generar el CSS personalizado con el color deseado
color_fondo_navbar = "#282255"  # Cambia este valor según lo necesites
custom_css = generar_css_personalizado(color_fondo_navbar)

# Aplicar el CSS en Streamlit
st.markdown(custom_css, unsafe_allow_html=True)

# Navbar personalizado con logo
navbar = NAVBAR_TEMPLATE.format(LOGO_NAVBAR_BASE64=LOGO_NAVBAR_BASE64)
# Mostrar el navbar
st.markdown(navbar, unsafe_allow_html=True)

mostrar_imagen(BANNER_IMG, use_container_width=True)
# Título y descripcion
centrar_texto(TITULO,"h1")
st.markdown("---")
st.write(TEXTO)
st.markdown("---")

# Pie de página
st.markdown("---")
st.write("© 2025 Colombia Programa - Ministerio de Tecnologías de la Información y las Comunicaciones (MinTIC)")

# Formatear el HTML con las imágenes convertidas a base64
formatted_footer = FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64)

# Mostrar el footer en Streamlit
st.markdown(formatted_footer, unsafe_allow_html=True)