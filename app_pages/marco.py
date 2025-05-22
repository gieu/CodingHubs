import streamlit as st
import pandas as pd
import plotly.express as px
from actions.marco_actions import cargar_datos, obtener_opciones_codigos, obtener_datos_pretest_posttest, crear_grafico_radar, centrar_texto
from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import LOGO_NAVBAR_BASE64, HIDE_STREAMLIT_STYLE ,  NAVBAR_TEMPLATE, generar_css_personalizado
from constants.marco_constants import TITULO, TEXTO

# Configuración de la página
st.set_page_config(layout="wide")

# Ocultar elementos de Streamlit
st.markdown(HIDE_STREAMLIT_STYLE, unsafe_allow_html=True)

# Generar el CSS personalizado con el color deseado
color_fondo_navbar = "#4A90E2"  # Cambia este valor según lo necesites
custom_css = generar_css_personalizado(color_fondo_navbar)

# Aplicar el CSS en Streamlit
st.markdown(custom_css, unsafe_allow_html=True)

# Navbar personalizado con logo
navbar = NAVBAR_TEMPLATE.format(LOGO_NAVBAR_BASE64=LOGO_NAVBAR_BASE64)
st.markdown(navbar, unsafe_allow_html=True)

centrar_texto(TITULO, "h1")
st.markdown("---")
st.write(TEXTO)

# Realizar la carga de datos y graficas
df = cargar_datos()

opciones_codigos_IE = obtener_opciones_codigos(df)

codigos_selececionados = st.multiselect(
    "Seleccione los códigos de IE que desea visualizar la comparativa de Pretest y Posttest", 
    opciones_codigos_IE
)

if codigos_selececionados:
    # Obtener los datos de Pretest y Posttest selecionados
    df_seleccionados = df[df['Código IE'].isin(codigos_selececionados)]
    
    for codigo in codigos_selececionados:
        datos_codigo = df_seleccionados[df_seleccionados['Código IE'] == codigo]
        
        pretest_numeric, posttest_numeric, categorias = obtener_datos_pretest_posttest(datos_codigo)
        
        if pretest_numeric is not None and posttest_numeric is not None:
            fig = crear_grafico_radar(pretest_numeric, posttest_numeric, categorias, codigo)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write(f"Datos incompletos para {codigo}. Se requieren tanto Pretest como Posttest.")
else:
    st.write("Por favor, seleccione al menos un código de IE para generar el gráfico.")

# Pie de página
st.markdown("---")
st.write("© 2025 Colombia Programa - Ministerio de Tecnologías de la Información y las Comunicaciones (MinTIC)")

# Formatear el HTML con las imágenes convertidas a base64
formatted_footer = FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64)

# Mostrar el footer en Streamlit
st.markdown(formatted_footer, unsafe_allow_html=True)
