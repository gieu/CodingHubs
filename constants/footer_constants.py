import actions.utils as utils

# Rutas de imágenes para el footer
RUTAS_IMAGENES = [
    "./assets/logo_colombia.png",
    "./assets/logo_tic.png",
    "./assets/logo_british.png",
    "./assets/logo_colombia_programa.png",
    "./assets/logo_uninorte.png",
]

# Imágenes convertidas a base64
IMAGENES_BASE64 = [utils.imagen_a_base64(ruta) for ruta in RUTAS_IMAGENES]

# Enlaces asociados a cada imagen
ENLACES_IMAGENES = [
    "https://www.colombia.co",  # Enlace para el logo de Colombia
    "https://www.mintic.gov.co",  # Enlace para el logo de TIC
    "https://www.britishcouncil.org",  # Enlace para el logo de British Council
    "https://mintic.gov.co/colombiaprograma/847/w3-channel.html",  # Enlace para el logo de Colombia Programa
    "https://www.uninorte.edu.co",  # Enlace para el logo de Uninorte
]

# HTML para el footer
FOOTER_HTML = f"""
<div class="footer">
    <div class="logo-container">
        <a href="{ENLACES_IMAGENES[0]}" target="_blank">
            <img src="data:image/png;base64,{IMAGENES_BASE64[0]}" alt="Logo Colombia">
        </a>
        <a href="{ENLACES_IMAGENES[1]}" target="_blank">
            <img src="data:image/png;base64,{IMAGENES_BASE64[1]}" alt="Logo TIC">
        </a>
        <a href="{ENLACES_IMAGENES[2]}" target="_blank">
            <img src="data:image/png;base64,{IMAGENES_BASE64[2]}" alt="Logo British Council">
        </a>
        <a href="{ENLACES_IMAGENES[3]}" target="_blank">
            <img src="data:image/png;base64,{IMAGENES_BASE64[3]}" alt="Logo Colombia Programa">
        </a>
        <a href="{ENLACES_IMAGENES[4]}" target="_blank">
            <img src="data:image/png;base64,{IMAGENES_BASE64[4]}" alt="Logo Uninorte">
        </a>
    </div>
</div>
"""
