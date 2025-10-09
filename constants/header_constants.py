import actions.utils as utils

# Ruta del logo del navbar
RUTA_LOGO_NAVBAR = "./assets/recursos-01.png"
LOGO_NAVBAR_BASE64 = utils.imagen_a_base64(RUTA_LOGO_NAVBAR)

# Define una variable para el color de fondo
DEFAULT_COLOR_FONDO_NAVBAR = "#004884"  # Color por defecto

# CSS para ocultar elementos predeterminados de Streamlit
HIDE_STREAMLIT_STYLE = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""

NAVBAR_TEMPLATE = """
<div class="navbar">
    <div class="logo">
        <a href="/colpro_dev/" target="_self" class="logo-link">
            <img src="data:image/png;base64,{LOGO_NAVBAR_BASE64}" alt="Logo Colombia Programa" class="logo-img">
            <span class="logo-text"></span>
        </a>
    </div>
    <div class="nav-links">
        <a href="/colpro_dev/" target="_self">Inicio</a>
        <div class="dropdown">
            <a href="#" class="dropbtn">Análisis <span class="arrow-down">▼</span></a>
            <div class="dropdown-content">
                <a href="/colpro_dev/pares" target="_self">Pares Expertos</a>
                <a href="/colpro_dev/encuentros_colaborativos" target="_self">Encuentros Colaborativos</a>
            </div>
        </div>
    </div>
</div>
"""

def generar_css_personalizado(color_fondo_navbar=DEFAULT_COLOR_FONDO_NAVBAR):
    return f"""
    <style>
    /* Fondo de la aplicación y tipografía global */
    body, .stApp, .main, .block-container, .stMarkdown, .stHeader, .stSubheader, .stTitle, .stWrite {{
        background-color: white !important;
        color: black !important; /* Asegurar que el texto sea negro */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; /* Fuente más moderna */
    }}

    /* Navbar personalizado */
    .navbar {{
        position: fixed; /* Hace que el navbar sea fijo */
        top: 0; /* Lo coloca en la parte superior */
        left: 0;
        width: 100%; /* Ocupa todo el ancho de la pantalla */
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: {color_fondo_navbar}; /* Color de fondo más moderno */
        padding: 10px 20px; /* Ajuste de padding para mayor consistencia */
        color: white;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Sombra más pronunciada */
        z-index: 1000; /* Asegura que el navbar esté por encima de otros elementos */
    }}

    .navbar .nav-links {{
        display: flex;
        align-items: center;
    }}

    .navbar a {{
        color: white !important;
        text-decoration: none;
        margin: 0 15px;
        font-size: 16px; /* Tamaño de fuente más pequeño para mayor elegancia */
        transition: color 0.3s ease; /* Transición suave para el hover */
    }}

    .navbar a:hover {{
        color: #FFD700; /* Color dorado en hover */
        text-decoration: underline;
    }}

    .navbar .logo-link {{
        display: flex;
        align-items: center;
        text-decoration: none;
    }}

    .navbar .logo-img {{
        height: 40px; /* Altura ajustada para mayor consistencia */
        margin-right: 10px; /* Espacio entre la imagen y el texto */
    }}

    .navbar .logo-text {{
        color: white !important;
        font-size: 24px; /* Tamaño de fuente ajustado */
        font-weight: bold; /* Texto en negrita */
    }}

    /* Menú desplegable */
    .dropdown {{
        position: relative;
        display: inline-block;
    }}

    .dropdown .dropbtn {{
        display: flex;
        align-items: center;
        cursor: pointer;
        font-size: 16px;
        border: none;
        background: none;
        color: white;
        padding: 10px;
        transition: color 0.3s ease;
    }}

    .dropdown .arrow-down {{
        margin-left: 5px;
        font-size: 12px;
    }}

    .dropdown-content {{
        display: none;
        position: absolute;
        right: 0; /* Alinea el menú desplegable a la derecha */
        background-color: {color_fondo_navbar};
        min-width: 200px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        z-index: 1;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #ccc; /* Borde minimalista */
    }}

    .dropdown-content a {{
        color: white !important;
        padding: 12px 16px;
        text-decoration: none;
        display: block;
        font-size: 16px;
        transition: background-color 0.3s ease;
        margin: 0; /* Elimina el margen */
    }}

    .dropdown-content a:hover {{
        background-color: #d3d3d3; /* Color gris claro en hover */
        color: black !important;
    }}

    .dropdown:hover .dropdown-content {{
        display: block;
    }}

    .dropdown:hover .dropbtn {{
        color: #d3d3d3; /* Color gris claro en hover */
    }}

    /* Ajustar el contenido principal para que no se solape con el navbar */
    .main .block-container {{
        padding-top: 70px; /* Espacio para evitar que el contenido se solape con el navbar */
    }}

    /* Footer personalizado */
    .footer {{
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        height: 9%;
        background-color: #ffffff;
        padding: 5px;
        text-align: center;
    }}

    .logo-container {{
        display: flex;
        justify-content: space-evenly; /* Distribuye los íconos uniformemente */
        align-items: center;
        flex-wrap: wrap; /* Permite que los íconos se ajusten en varias filas si es necesario */
        width: 100%; /* Asegura que ocupe todo el ancho */
        margin: 0 auto; /* Centra el contenido */
    }}

    .logo-container img {{
        max-width: 100%; /* Ajusta el ancho máximo al 100% del contenedor */
        height: auto; /* Mantiene la proporción de la imagen */
        max-height: 50px; /* Ajusta la altura máxima de los íconos */
        transition: transform 0.3s ease;
    }}

    .logo-container img:hover {{
        transform: scale(1.2); /* Efecto de zoom al pasar el cursor */
    }}

    @media (max-width: 768px) {{
        .logo-container {{
            justify-content: center; /* Centra los íconos en pantallas pequeñas */
        }}

        .logo-container img {{
            max-height: 50px; /* Reduce el tamaño de los íconos en pantallas pequeñas */
        }}
    }}
    </style>
    """
