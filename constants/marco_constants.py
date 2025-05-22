TITULO="Marco de Calidad"
TEXTO="""En esta sección se presentan los resultados consolidados de cada una de las 420 instituciones evaluadas, organizados por las dimensiones clave: Liderazgo y visión, Plan de estudios, Enseñanza, aprendizaje y
evaluación, Desarrollo profesional del personal docente, Equidad, diversidad e inclusión, Proyección en educación terciaria, Impacto en los resultados, y Equidad de género.

Cada institución recibe una calificación en una escala de 1A a 5 para cada una de las dimensiones, lo que permite evaluar su desempeño específico. Además, se muestra el promedio general de las calificaciones obtenidas en las 8 dimensiones, proporcionando una visión completa del estado de las instituciones en el marco del proyecto."""


# URL del CSV publicado de Google Sheets
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6Ql44xab2MHwi7PcPIa9nvMERf6oUTWktc5W6RG5KvhEP9SPPb_a638vdDPoWkTg_x8ovxt_RP9Xl/pub?output=csv"

# Opciones iniciales
OPCIONES_INICIALES = ['Promedio', 'Moda', 'Mediana']

# Mapeo actualizado para categorías
MAPPING = {'0': 0, '1A': 1, '1B': 2, '2A': 3, '2B': 4, '3A': 5, '3B': 6, '4': 7, '5': 8}

# Colores para los gráficos
COLORS = {
    'pretest': {'line': 'rgb(239, 85, 59)', 'fill': 'rgba(239, 85, 59, 0.5)'},
    'posttest': {'line': 'rgb(99, 110, 250)', 'fill': 'rgba(99, 110, 250, 0.5)'}
}
