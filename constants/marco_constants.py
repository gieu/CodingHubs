TITULO="Marco de Calidad"
TEXTO = "Los resultados se presentan en ocho dimensiones, con una escala de 1A a 5."


# CSV del consolidado compartido en Google Drive.
CSV_URL = "https://docs.google.com/spreadsheets/d/1qMlLT2gCVcwHZb1UC1f3U-LBcfHV_Dnt/export?format=csv"

# Opciones iniciales
OPCIONES_INICIALES = ['Promedio', 'Moda', 'Mediana']

# Mapeo actualizado para categorías
MAPPING = {'0': 0, '1A': 1, '1B': 2, '2A': 3, '2B': 4, '3A': 5, '3B': 6, '4': 7, '5': 8}
ESCALA_NIVELES = [nivel for nivel in MAPPING if nivel != "0"]

ETIQUETAS_MOMENTOS = {
    "pre_2023": "Pretest 2023",
    "post_2023": "Postest 2023",
    "pre_2024": "Pretest 2024",
    "post_2024": "Postest 2024",
    "post_2025": "Postest 2025",
    "nivel_2025": "Nivel 2025",
    "post_2026_junio": "Postest · junio 2026",
    "nivel_2026_junio": "Nivel · junio 2026",
    "post_2026_diciembre": "Postest · diciembre 2026",
    "nivel_2026_diciembre": "Nivel · diciembre 2026",
}

# Colores para los gráficos
COLORS = {
    'pre_2023': {'line': 'rgb(131, 201, 255)', 'fill': 'rgba(131, 201, 255, 0.22)'},
    'post_2023': {'line': 'rgb(0, 104, 201)', 'fill': 'rgba(0, 104, 201, 0.22)'},
    'pre_2024': {'line': 'rgb(102, 36, 130)', 'fill': 'rgba(102, 36, 130, 0.3)'},
    'post_2024': {'line': 'rgb(35, 8, 90)', 'fill': 'rgba(35, 8, 90, 0.3)'},
    'post_2025': {'line': 'rgb(229, 0, 126)', 'fill': 'rgba(229, 0, 126, 0.3)'},
    'nivel_2025': {'line': 'rgb(233, 161, 69)', 'fill': 'rgba(233, 161, 69, 0.3)'},
    'post_2026_junio': {'line': '#138276', 'fill': 'rgba(19, 130, 118, 0.18)'},
    'nivel_2026_junio': {'line': '#577d1b', 'fill': 'rgba(87, 125, 27, 0.18)'},
    'post_2026_diciembre': {'line': '#1f5480', 'fill': 'rgba(31, 84, 128, 0.18)'},
    'nivel_2026_diciembre': {'line': '#a7522b', 'fill': 'rgba(167, 82, 43, 0.18)'},
}

# Mapeo de nombres completos a nombres cortos
CODIGO_IE_NOMBRES = {
    'Institución Educativa Escuela Normal Superior de Caldas': 'IEM01',
    'Institución Educativa Gran Colombia': 'IEM02',
    'Institución Educativa Instituto Chipre': 'IEM03',
    'Institución Educativa Instituto Latinoamericano': 'IEM04',
    'Institución Educativa Instituto Manizales': 'IEM05',
    'Institución Educativa Instituto Técnico Francisco José de Caldas': 'IEM06',
    'Institución Educativa Instituto Técnico Marco Fidel Suarez': 'IEM07',
    'Institución Educativa Liceo León de Greiff': 'IEM08',
    'Institución Educativa Mariscal Sucre': 'IEM09',
    'Institución Educativa San Sebastián': 'IEM10'
}
