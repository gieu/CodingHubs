import actions.utils as utils

# Rutas de imágenes para el footer
RUTAS_IMAGENES = [
    "./assets/logo_british.png",
    "./assets/luker.png",
    "./assets/alcaldia.png",
]

# Imágenes convertidas a base64
IMAGENES_BASE64 = [utils.imagen_a_base64(ruta) for ruta in RUTAS_IMAGENES]

# Enlaces asociados a cada imagen
ENLACES_IMAGENES = [
    "https://www.britishcouncil.org", 
    "https://fundacionluker.org.co/",  
    "https://manizales.gov.co/",  
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
    </div>
</div>
"""
