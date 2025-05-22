import base64

# Función para convertir imágenes a base64
def imagen_a_base64(ruta):
    with open(ruta, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
