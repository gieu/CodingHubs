import streamlit as st
import pandas as pd
from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import LOGO_NAVBAR_BASE64, HIDE_STREAMLIT_STYLE, NAVBAR_TEMPLATE, generar_css_personalizado
import actions.utils as utils
from actions.graficas_jesus_actions import graficas_jesus
from actions.resumen_actions import resumen_ejecutivo
from actions.momentos_actions import (
    mapa_calor_conductas_que, mapa_calor_conductas_como, lineas_conductas_como, burbujas_acciones_momento,
)
import os
# ==========================================
# FUNCIÓN HEADER PERSONALIZADA PARA ESTA PÁGINA
# ==========================================

def header_encuentros_colaborativos(color_fondo_navbar="#ff7f00"):
    """Genera el header personalizado con el logo de Coding Hubs específicamente para encuentros colaborativos."""
    import streamlit as st
    
    # Ruta del logo específico para esta página
    RUTA_LOGO_CODINGHUBS = "./assets/codinghubs.png"
    LOGO_CODINGHUBS_BASE64 = utils.imagen_a_base64(RUTA_LOGO_CODINGHUBS)
    
    # Deploy environment
    deploy_env = os.getenv("DEPLOY_ENV", "local")
    BASE_URL = "/"
    if deploy_env == 'prod':
        BASE_URL = "/codinghubs/"
    else:
        BASE_URL = "/"
    
    # Ocultar elementos de Streamlit
    st.markdown(HIDE_STREAMLIT_STYLE, unsafe_allow_html=True)

    # Generar el CSS personalizado con el color deseado
    custom_css = generar_css_personalizado(color_fondo_navbar)

    # Aplicar el CSS en Streamlit
    st.markdown(custom_css, unsafe_allow_html=True)

    # Navbar personalizado con logo específico de Coding Hubs
    navbar_codinghubs = NAVBAR_TEMPLATE.format(
        LOGO_NAVBAR_BASE64=LOGO_CODINGHUBS_BASE64,
        BASE_URL=BASE_URL
    )
    st.markdown(navbar_codinghubs, unsafe_allow_html=True)

# Definir el color personalizado para esta página
color_fondo_navbar = "#ff7f00"  # Naranja para distinguir esta página

# Crear navbar con el color personalizado y logo específico
header_encuentros_colaborativos(color_fondo_navbar)
# ==========================================
# CARGA DE DATOS
# ==========================================
# URL del CSV

import unicodedata


ACCIONES_INSTANTANEAS_GRUPOS = {
    'Transferencia y Diálogo': [
        'Dialogan activamente entre pares',
        'Un(a) docente hace una participación o intervención',
        'Hacen preguntas o solicitan aclaraciones',
        'Toman notas o registran información',
    ],
    'Actividades y Recursos': [
        'Realizan una actividad práctica',
        'Usan materiales o recursos del encuentro, como las guías para la enseñanza del pensamiento computacional.',
        'Exploran o desarrollan actividades con la Micro:bit',
        'Usan dispositivos como celular o computador con fines educativos',
    ],
    'Escucha': [
        'Escuchan una explicación temática de un par experto',
        'Escuchan instrucciones para el desarrollo de una actividad de un par experto',
        'Escuchan una explicación temática de un facilitador del encuentro (ej. mentor)',
        'Escuchan instrucciones para el desarrollo de una actividad de un facilitador del encuentro (ej. mentor)',
    ],
    'Otras': [
        'Observan un ejemplo, demostración o modelamiento',
        'Observan material audiovisual (ej. video explicativo sobre nodos o pensamiento computacional)',
        'Conversan sobre un tema personal o no relacionado con el encuentro',
        'Están distraídos o desconectados de las actividades',
        'Otra',
    ],
}


def normalizar_texto_busqueda(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower().strip()


# Tabla de correspondencia Match entre fases
# MATCH_ENCUENTROS = {
#     'Fase 1': ['EC24', 'EC12', 'EC37', 'EC1', 'EC15', 'EC22', 'EC39', 'EC35', 'EC41', 'EC40', 'EC34', 'EC10', 'EC16', 'EC36'],
#     'Fase 2': ['EC1', 'EC10', 'EC11', 'EC12', 'EC13', 'EC14', 'EC15', 'EC3', 'EC4', 'EC5', 'EC6', 'EC7', 'EC8', 'EC9']
# }

# MATCH_ENCUENTROS_INSTANTANEAS = {
#     'Fase 1': ['EC24', 'EC12', 'EC37', 'EC1', 'EC15', 'EC22',  'EC35', 'EC41', 'EC40', 'EC34', 'EC10', 'EC16', 'EC36'],
#     'Fase 2': ['EC1', 'EC10', 'EC11', 'EC12', 'EC13', 'EC14',  'EC3', 'EC4', 'EC5', 'EC6', 'EC7', 'EC8', 'EC9']
# }

# URL del CSV
import os
from io import BytesIO
DEPLOY_ENV = os.getenv("DEPLOY_ENV")

# --- Cargar Datos con Cache ---
@st.cache_data(ttl=600)
def load_data(file, mostrar_aviso=True):
    try:
        df = pd.read_csv(file, encoding='utf-8')
    except Exception:
        if mostrar_aviso:
            st.warning("No se pudo cargar una de las fuentes actuales. Los demás análisis siguen disponibles.")
        return pd.DataFrame()
    df.columns = df.columns.str.strip()
    # Older sheets identify an encounter by its phase and code.
    if not {'idEncuentro', 'IDEncuentro'}.intersection(df.columns) and {'Fase', 'Encuentro'}.issubset(df.columns):
        df['idEncuentro'] = df['Fase'].astype(str) + ':' + df['Encuentro'].astype(str)
    return df


def resumen_ejecutivo_momentos():
    """Resumen ejecutivo de 2026: conductas por tipo de participante y distribución por género."""
    resumen_ejecutivo(load_data(URL_MOMENTOS_EC), load_data(URL_DOCENTES_UNICOS, mostrar_aviso=False))


URL_DOCENTES_UNICOS = "https://docs.google.com/spreadsheets/d/1nCnSS2qt45U8Bh8n6YobT8Tyw_LLPSN86Vgzs3oq-wg/export?format=csv&gid=2015426318"
URL_MOMENTOS_EC = "https://docs.google.com/spreadsheets/d/1pfcVzbsb2N9hbRR3wEsuEfuaU76EwBuac8moRMXNd78/export?format=csv&gid=1073044251"
URL_AFIRMACIONES_EC = "https://docs.google.com/spreadsheets/d/1dbQaOF24h5FzGXbw3X2Gx4cU9Vjgdh-22kNKo2jXPDE/export?format=csv&gid=1583679053"


def momentos():
    """Pestaña Momentos: conductas asociadas al qué y al cómo, por momento (sin filtros)."""
    df_afirmaciones = load_data(URL_AFIRMACIONES_EC)
    st.subheader("📊 Conductas asociadas al qué")
    mapa_calor_conductas_que(df_afirmaciones)
    st.subheader("📊 Conductas asociadas al cómo")
    mapa_calor_conductas_como(df_afirmaciones)

    st.subheader("📈 Conductas del cómo por tipo de participante")
    lineas_conductas_como(load_data(URL_MOMENTOS_EC))

    st.subheader("🫧 Acciones por momento")
    burbujas_acciones_momento(load_data(URL_INSTANTANEAS_ACCIONES))


URL_INSTANTANEAS_ACCIONES = "https://docs.google.com/spreadsheets/d/1dU6-Hb5MW252A_PF3iaOqhX95W1tXF1J5BWrCIhD_u8/export?format=csv&gid=134781920"


def instantaneas():
    """Pestaña Instantáneas: gráficas sobre la hoja de instantáneas (sin filtros)."""
    df_inst = load_data(URL_INSTANTANEAS_ACCIONES)
    graficas_jesus(df_inst)


# ==========================================
# APLICACIÓN PRINCIPAL
# ==========================================
st.title("🤝  Análisis Encuentros Colaborativos 2026 e Instantáneas")

st.markdown("""
Esta página está dedicada al análisis profundo de los **encuentros colaborativos** entre docentes, 
explorando tanto las actitudes como las prácticas de colaboración en el contexto educativo.
""")

# Crear las pestañas principales
tab1, tab2, tab3 = st.tabs([" Resumen Ejecutivo", "📊 Momentos", "⚡ Instantáneas"])

with tab1:
    # Mostrar resumen ejecutivo
    resumen_ejecutivo_momentos()

with tab2:
    
    momentos()

with tab3:
    st.header("⚡ Instantáneas - Métricas Rápidas")
    st.markdown("""
    Vista rápida de métricas clave y visualizaciones instantáneas sobre redes y 
    comunidades colaborativas.
    """)
    instantaneas()


# Pie de página
st.markdown("---")
st.write("© 2026 Colombia Programa - Encuentros Colaborativos 2026 - Ministerio de Tecnologías de la Información y las Comunicaciones (MinTIC)")

# Formatear el HTML con las imágenes convertidas a base64
formatted_footer = FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64)

# Mostrar el footer en Streamlit
st.markdown(formatted_footer, unsafe_allow_html=True)
