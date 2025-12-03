TITULO="Marco de Calidad"
TEXTO="""En esta sección se presentan los resultados consolidados de cada una de las 420 instituciones evaluadas, organizados por las dimensiones clave: Liderazgo y visión, Plan de estudios, Enseñanza, aprendizaje y
evaluación, Desarrollo profesional del personal docente, Equidad, diversidad e inclusión, Proyección en educación terciaria, Impacto en los resultados, y Equidad de género.

Cada institución recibe una calificación en una escala de 1A a 5 para cada una de las dimensiones, lo que permite evaluar su desempeño específico. Además, se muestra el promedio general de las calificaciones obtenidas en las 8 dimensiones, proporcionando una visión completa del estado de las instituciones en el marco del proyecto."""


# URL del CSV publicado de Google Sheets
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSRVc2rbCoOeSvbw99wbWhECryfq3cvS5YA8HHhnYGKCtLHNGleoGM6wPqde8Qtfg/pub?gid=618340973&single=true&output=csv"

# Opciones iniciales
OPCIONES_INICIALES = ['Promedio', 'Moda', 'Mediana']

# Mapeo actualizado para categorías
MAPPING = {'0': 0, '1A': 1, '1B': 2, '2A': 3, '2B': 4, '3A': 5, '3B': 6, '4': 7, '5': 8}

# Colores para los gráficos
COLORS = {
    'pre_2024': {'line': 'rgb(102, 36, 130)', 'fill': 'rgba(102, 36, 130, 0.3)'},
    'post_2024': {'line': 'rgb(35, 8, 90)', 'fill': 'rgba(35, 8, 90, 0.3)'},
    'post_2025': {'line': 'rgb(229, 0, 126)', 'fill': 'rgba(229, 0, 126, 0.3)'},
    'nivel_2025': {'line': 'rgb(233, 161, 69)', 'fill': 'rgba(233, 161, 69, 0.3)'},
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
