# Archivo: actions.py

import streamlit as st

def mostrar_imagen(ruta_imagen, width=None, use_container_width=False):
    """Carga y muestra una imagen en Streamlit."""
    st.image(ruta_imagen, width=width, use_container_width=use_container_width)

def mostrar_componente(titulo, imagen, secciones):
    """Renderiza un componente con su imagen y secciones en Streamlit."""
    st.header(titulo)
    mostrar_imagen(imagen, width=1000)  # Se mantiene el ancho fijo
    
    for seccion in secciones:
        st.subheader(seccion["subtitulo"])
        st.write(seccion["contenido"])
    
    st.markdown("---")  # Línea divisoria

def centrar_texto(texto, tipo="h1"):
    """Centrar headers, subheaders y textos en Streamlit."""
    st.markdown(f"<{tipo} style='text-align: center;'>{texto}</{tipo}>", unsafe_allow_html=True)
