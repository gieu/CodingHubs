# Referencia: Observaciones Docentes Biobots

Guía para trabajar y modificar los archivos que componen la página **Observaciones Docentes Biobots** dentro de la app Streamlit de CodingHubs.

---

## Estructura de archivos

```
app_pages/docentes_observados.py        ← Página Streamlit (UI + carga de datos)
actions/docentes_observados_actions.py  ← Lógica de gráficas y transformaciones
excel/Docentes_observados_inicial.xlsx  ← Referencia local de columnas y datos
docs/docentes_observados_reference.md  ← Este archivo
```

La página se registra en `app.py` como una de las páginas del menú de navegación.

---

## `app_pages/docentes_observados.py`

### Responsabilidades
- Configurar el encabezado corporativo (`#282255`).
- Definir la URL de descarga del Google Sheet de observaciones.
- Cachear la carga del CSV con `@st.cache_data(ttl=600)`.
- Llamar a las funciones de graficación definidas en `actions/`.

### Fuente de datos

| Parámetro | Valor |
|-----------|-------|
| Google Sheet ID | `1k7hHR838J85-SRZ-J6odEx8UDH3_MKYB` |
| Formato descarga | CSV vía URL pública de Google Sheets |
| TTL caché | 600 segundos (10 min) |
| Normalización | `df.columns.str.strip()` al cargar |

```python
SHEET_ID = "1k7hHR838J85-SRZ-J6odEx8UDH3_MKYB"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
```

> **Importante:** La normalización `str.strip()` elimina espacios al inicio y fin de todos los nombres de columna. Las constantes en `actions/` deben coincidir exactamente con las columnas ya sin espacios.

### Patrón para agregar una nueva sección

1. Importar la nueva función de `actions/docentes_observados_actions.py`.
2. Añadir un `st.subheader(...)` descriptivo.
3. Llamar la función pasando `df_obs` y `chart_config`.

```python
from actions.docentes_observados_actions import nueva_funcion_grafico

st.subheader("Título de la sección")
nueva_funcion_grafico(df_obs, chart_config)
```

### Cómo actualizar la hoja de datos

Para apuntar a otro Sheet completo, cambia `SHEET_ID`. La URL se recompone automáticamente.

---

## `actions/docentes_observados_actions.py`

### Responsabilidades
- Definir constantes de nombres de columnas y paletas de color.
- Validar presencia de columnas antes de graficar.
- Normalizar sedes educativas por código DANE.
- Construir y renderizar las gráficas con Plotly + `st.plotly_chart`.

### Constantes de columnas definidas

```python
# Identificación
COL_SEDE        = "Datos de identificación/Nombre de la sede educativa"
COL_DANE        = "Datos de identificación/Código DANE de la sede educativa"
COL_DOCENTE     = "Datos de identificación/Nombre del docente"
COL_NUM_OBS     = "Número de Observacion"
COL_OBSERVADOR  = "Datos de identificación/Nombre del observador(a)"
COL_FECHA       = "Datos de identificación/Fecha de observación"

# Información básica
COL_NINOS = "Información básica/¿Cuántos de los estudiantes son niños?"
COL_NINAS = "Información básica/¿Cuántos de los estudiantes son niñas?"
COL_GRADO = "Información básica/Selecciona los grados que estas observando en el aula."

# Organización antes del juego
COL_N_GRUPOS       = "Organización y preparación (Antes de jugar)/¿Cuántos grupos se organizan para usar el juego?"
COL_ESTU_POR_GRUPO = "Organización y preparación (Antes de jugar)/Aproximadamente, ¿cuántos estudiantes hay en cada uno de los grupos?"
COL_ESCENARIO      = "Organización y preparación (Antes de jugar)/Escenario de juego. ¿Cuál es el escenario a jugar?"

# Introducción al juego (multi-select binario)
COL_INTRO_NARRATIVA_MANUAL   = "Organización y preparación (Antes de jugar)/¿Cómo introdujo.../Usó la narrativa del manual del juego"
COL_INTRO_NARRATIVA_ADAPTADA = "Organización y preparación (Antes de jugar)/¿Cómo introdujo.../Usó una narrativa adaptada"
COL_INTRO_OBJETIVO           = "Organización y preparación (Antes de jugar)/¿Cómo introdujo.../Explicó el objetivo del juego"
COL_INTRO_VOCAB_TECNICO      = "Organización y preparación (Antes de jugar)/¿Cómo introdujo.../Usó vocabulario técnico del juego"
COL_INTRO_OTRO               = "Organización y preparación (Antes de jugar)/¿Cómo introdujo.../Otro"

# Organización de grupos (single-select → columna texto)
COL_ORG_GRUPOS = "Organización y preparación (Antes de jugar)/ ¿Cómo se organizaron los grupos?"

# Materiales y guías (Sí/No)
COL_GUIA_INICIO      = "Organización y preparación (Antes de jugar)/¿El/la docente se apoya en la guía de inicio...?"
COL_GUIA_PEDAGOGICA  = "Organización y preparación (Antes de jugar)/¿El/la docente se apoya en la guía pedagógica...?"
COL_LIBRO_ESCENARIOS = "Organización y preparación (Antes de jugar)/¿El/la docente se apoya en el libro de escenarios...?"
COL_LIBRILLO_MAPAS   = "Organización y preparación (Antes de jugar)/¿El/la docente se apoya en el librillo de mapas...?"
COL_AFICHE           = "Organización y preparación (Antes de jugar)/¿El/la docente usó el afiche de apoyo visual...?"
COL_MANUAL_CAP2      = "Organización y preparación (Antes de jugar)/.../Capítulo 2"

# Explicación de reglas (multi-select binario)
COL_REGLAS_VERBAL           = "Durante el juego/Explicación de las reglas. .../Explica las reglas de manera verbal."
COL_REGLAS_TABLERO          = "Durante el juego/Explicación de las reglas. .../Apoya su explicación escribiendo las reglas en el tablero"
COL_REGLAS_MATERIALES_JUEGO = "Durante el juego/Explicación de las reglas. .../Usa materiales del juego para ejemplificar las reglas."

# Tipos de dudas (multi-select binario)
COL_DUDAS_REGLAS     = "Durante el juego/Tipos de dudas.../Sobre las reglas del juego"
COL_DUDAS_MATERIALES = "Durante el juego/Tipos de dudas.../Sobre el uso de materiales"
COL_DUDAS_SECUENCIA  = "Durante el juego/Tipos de dudas.../Sobre la secuencia del juego"
COL_DUDAS_NINGUNA    = "Durante el juego/Tipos de dudas.../No hubo dudas significativas"

# Vocabulario técnico (multi-select binario)
COL_TERM_BIOBOTS       = "Durante el juego/¿Qué términos...? /Biobots"
COL_TERM_LOSETAS       = "Durante el juego/¿Qué términos...? /Losetas"
COL_TERM_PROGRAMAR     = "Durante el juego/¿Qué términos...? /Programar"
COL_TERM_INSTRUCCIONES = "Durante el juego/¿Qué términos...? /Instrucciones"
COL_TERM_ALGORITMO     = "Durante el juego/¿Qué términos...? /Algoritmo"
COL_TERM_OTRO          = "Durante el juego/¿Qué términos...? /Otro"
COL_VOCAB_QUIEN        = "Durante el juego/¿Quiénes utilizaron el vocabulario propio del juego?"

# Después del juego
COL_TIEMPO_USO    = "Después del juego/Tiempo total en horas clase..."
COL_PRIMERA_VEZ   = "Después del juego/¿Fue la primera vez que jugaron el escenario?"
COL_VECES_PREVIAS = "Después del juego/En caso de responder no, por favor indique el número de veces previas..."
COL_CONEXION_PC   = "Después del juego/¿Se hizo una conexión explícita con habilidades de pensamiento computacional...?"

# Tipo de cierre (multi-select binario)
COL_CIERRE_REFLEXION = "Después del juego/.../Reflexión grupal guiada por el/la docente"
COL_CIERRE_RETROALIM = "Después del juego/.../Retroalimentación individual"
COL_CIERRE_METACOG   = "Después del juego/.../Espacio de metacognición"
COL_CIERRE_NINGUNO   = "Después del juego/.../No se realizó ninguna actividad de cierre"
```

> **Nota sobre espacios:** Los nombres de columna del CSV tienen espacios al final en algunos campos. La función `load_data` los elimina con `.str.strip()`, por lo que las constantes deben definirse **sin** espacios al final.

### Paleta corporativa

```python
AZUL_CLARO  = "#83C9FF"
AZUL_OSCURO = "#0068C9"
MORADO      = "#662482"
ROSA        = "#e5007e"
GRIS        = "#9CA3AF"
```

### Helpers privados

#### `_normalizar_sede(df)`

Devuelve una Serie con el **nombre de sede más frecuente** para cada código DANE, evitando variantes ortográficas del mismo colegio.

#### `_validar_columnas(df, columnas, nombre_grafico)`

Emite `st.warning` si alguna columna de `columnas` no está en `df.columns`. Retorna `True` si todo OK, `False` si falta algo. Todas las funciones de gráfico lo llaman al inicio.

#### `_frecuencias_binarias(df, columnas, etiquetas)`

Suma columnas binarias (0/1) presentes en `df` y devuelve un `DataFrame` con columnas `Etiqueta`, `Frecuencia`, `Porcentaje (%)`. Usado por las gráficas de multi-select.

---

## Gráficas implementadas

### `grafico_mariposa_ninos_ninas(df, chart_config)` ✅

Barras horizontales tipo mariposa: número de niños (izquierda) vs niñas (derecha) por sede educativa.

| Elemento | Detalle |
|----------|---------|
| Eje Y | Sede educativa (normalizada por código DANE) |
| Eje X | Conteo (negativo = niños, positivo = niñas) |
| Columnas requeridas | `COL_SEDE`, `COL_DANE`, `COL_NINOS`, `COL_NINAS` |
| Colores | Niños `#83C9FF`, Niñas `#0068C9` |
| Expander | Tabla con Niños, Niñas y Total por sede |

---

### `grafico_distribucion_grado(df, chart_config)` ✅

Barras verticales: número de observaciones por grado escolar (Cuarto / Quinto).

| Elemento | Detalle |
|----------|---------|
| Eje X | Grado escolar |
| Eje Y | Número de observaciones |
| Columnas requeridas | `COL_GRADO` |
| Colores | Cuarto `#83C9FF`, Quinto `#0068C9` |
| Expander | Tabla de conteos por grado |

---

### `grafico_treemap_sedes(df, chart_config)` ✅

Treemap: número de observaciones por sede educativa, con color proporcional al conteo.

| Elemento | Detalle |
|----------|---------|
| Jerarquía | Sede (nivel único, normalizada por DANE) |
| Valor | Conteo de observaciones por sede |
| Color | Escala continua azul claro → azul oscuro |
| Columnas requeridas | `COL_SEDE`, `COL_DANE` |
| Expander | Tabla de observaciones por sede ordenada descendente |

---

### `grafico_distribucion_escenario(df, chart_config)` ✅

Barras verticales: número de observaciones por escenario jugado.

| Elemento | Detalle |
|----------|---------|
| Eje X | Escenario (Escenario 2, Escenario 3, Otro) |
| Eje Y | Número de observaciones |
| Columnas requeridas | `COL_ESCENARIO` |
| Colores | Escenario 2 `#83C9FF`, Escenario 3 `#0068C9`, Otro `#9CA3AF` |
| Expander | Tabla de conteos por escenario |

---

### `grafico_introduccion_juego(df, chart_config)` ✅

Barras horizontales de frecuencia: métodos usados para introducir el juego (multi-select).

| Elemento | Detalle |
|----------|---------|
| Eje Y | Método de introducción |
| Eje X | Número de observaciones donde se usó |
| Columnas requeridas | Al menos una de: `COL_INTRO_OBJETIVO`, `COL_INTRO_VOCAB_TECNICO`, `COL_INTRO_NARRATIVA_MANUAL`, `COL_INTRO_NARRATIVA_ADAPTADA`, `COL_INTRO_OTRO` |
| Color | Azul oscuro `#0068C9` |
| Texto en barra | `N (X%)` |
| Expander | Tabla de frecuencias y porcentajes |

> Funciona con columnas parciales: si alguna falta en el CSV, la omite silenciosamente.

---

### `grafico_organizacion_grupos(df, chart_config)` ✅

Barras horizontales: cómo se organizaron los grupos (respuesta de texto único).

| Elemento | Detalle |
|----------|---------|
| Eje Y | Forma de organización |
| Eje X | Número de observaciones |
| Columnas requeridas | `COL_ORG_GRUPOS` |
| Colores | Paleta corporativa rotando |
| Expander | Tabla de conteos |

---

### `grafico_materiales_docente(df, chart_config)` ✅

Barras horizontales apiladas (stacked): muestra tanto los docentes que **sí usaron** como los que **no usaron** cada material del kit.

| Elemento | Detalle |
|----------|---------|
| Eje Y | Material / guía (Guía de inicio, Guía pedagógica, Libro de escenarios, Librillo de mapas, Manual Cap. 2, Afiche) |
| Eje X | Número de observaciones |
| Segmento azul | "Sí usaron" — azul oscuro `#0068C9`, con etiqueta `N (X%)` |
| Segmento gris | "No usaron" — gris `#9CA3AF`, con etiqueta `N` |
| Columnas requeridas | Al menos una de las seis columnas de material |
| Expander 1 | Tabla con Usaron (Sí), No usaron, Porcentaje |
| Expander 2 | Descripciones cualitativas del uso de materiales |

> Soporta columnas en formato Sí/No (texto) o 0/1 (numérico) de forma automática.

---

### `grafico_explicacion_reglas(df, chart_config)` ✅

Barras horizontales de frecuencia: métodos usados para explicar las reglas (multi-select).

| Elemento | Detalle |
|----------|---------|
| Eje Y | Método de explicación |
| Eje X | Número de observaciones |
| Columnas requeridas | Al menos una de: `COL_REGLAS_VERBAL`, `COL_REGLAS_MATERIALES_JUEGO`, `COL_REGLAS_TABLERO` |
| Color | Azul oscuro `#0068C9` |
| Texto en barra | `N (X%)` |
| Expander | Tabla de frecuencias |

---

### `grafico_dudas_estudiantes(df, chart_config)` ✅

Barras horizontales de frecuencia: tipos de dudas observadas en los estudiantes (multi-select).

| Elemento | Detalle |
|----------|---------|
| Eje Y | Tipo de duda |
| Eje X | Número de observaciones |
| Columnas requeridas | Al menos una de: `COL_DUDAS_REGLAS`, `COL_DUDAS_MATERIALES`, `COL_DUDAS_SECUENCIA`, `COL_DUDAS_NINGUNA` |
| Color | Morado `#662482` |
| Texto en barra | `N (X%)` |
| Expander | Tabla de frecuencias |

---

### `grafico_vocabulario_terminos(df, chart_config)` ✅

Barras horizontales de frecuencia: términos técnicos del juego mencionados durante la sesión (multi-select).

| Elemento | Detalle |
|----------|---------|
| Eje Y | Término (Biobots, Losetas, Instrucciones, Algoritmo, Programar, Otro) |
| Eje X | Número de observaciones donde se mencionó |
| Columnas requeridas | Al menos una de las seis columnas de términos |
| Color | Azul oscuro `#0068C9` |
| Texto en barra | `N (X%)` |
| Expander | Tabla de frecuencias |

---

### `grafico_tiempo_uso(df, chart_config)` ✅

Barras verticales: distribución del tiempo de uso directo con el juego (en horas clase).

| Elemento | Detalle |
|----------|---------|
| Eje X | Horas de clase (entero) |
| Eje Y | Número de observaciones |
| Columnas requeridas | `COL_TIEMPO_USO` |
| Colores | 1 hora `#83C9FF`, 2 horas `#0068C9`, otros `#9CA3AF` |
| Expander | Tabla de conteos por duración |

> Los valores se convierten a numérico y se toma el valor absoluto para manejar posibles negativos.

---

### `grafico_primera_vez(df, chart_config)` ✅

Barras horizontales: si fue la primera vez que se jugó el escenario.

| Elemento | Detalle |
|----------|---------|
| Eje Y | Respuesta (Sí / No) |
| Eje X | Número de observaciones |
| Columnas requeridas | `COL_PRIMERA_VEZ` |
| Colores | Sí `#83C9FF`, No `#0068C9` |
| Expander condicional | Tabla de veces previas jugadas (solo si `COL_VECES_PREVIAS` existe en el DF) |

---

### `grafico_conexion_pc(df, chart_config)` ✅

Barras horizontales: tipo de conexión explícita con pensamiento computacional al finalizar.

| Elemento | Detalle |
|----------|---------|
| Eje Y | Tipo de conexión (Sí / De forma implícita o superficial / No) |
| Eje X | Número de observaciones |
| Columnas requeridas | `COL_CONEXION_PC` |
| Colores | Sí `#0068C9`, Implícita `#662482`, No `#9CA3AF` |
| Expander | Tabla de conteos |

---

### `grafico_cierre_actividad(df, chart_config)` ✅

Barras horizontales de frecuencia: tipo de espacio usado para el cierre / conexión con PC (multi-select).

| Elemento | Detalle |
|----------|---------|
| Eje Y | Tipo de cierre |
| Eje X | Número de observaciones |
| Columnas requeridas | Al menos una de: `COL_CIERRE_REFLEXION`, `COL_CIERRE_NINGUNO`, `COL_CIERRE_RETROALIM`, `COL_CIERRE_METACOG` |
| Color | Azul oscuro `#0068C9` |
| Texto en barra | `N (X%)` |
| Expander | Tabla de frecuencias |

---

## Flujo de secciones en la página

| Sección | Subheader | Función |
|---------|-----------|---------|
| Información básica | Distribución de estudiantes por sede educativa | `grafico_mariposa_ninos_ninas` |
| Información básica | Distribución de observaciones por grado escolar | `grafico_distribucion_grado` |
| Información básica | Distribución de observaciones por sede educativa | `grafico_treemap_sedes` |
| Antes del juego | Distribución de observaciones por escenario jugado | `grafico_distribucion_escenario` |
| Antes del juego | Métodos usados para introducir el juego | `grafico_introduccion_juego` |
| Antes del juego | ¿Cómo se organizaron los grupos? | `grafico_organizacion_grupos` |
| Antes del juego | Uso de materiales y guías del kit por el docente | `grafico_materiales_docente` |
| Durante el juego | Métodos usados para explicar las reglas del juego | `grafico_explicacion_reglas` |
| Durante el juego | Tipos de dudas observadas en los estudiantes | `grafico_dudas_estudiantes` |
| Durante el juego | Vocabulario técnico mencionado durante la sesión | `grafico_vocabulario_terminos` |
| Después del juego | Tiempo de uso directo con el juego | `grafico_tiempo_uso` |
| Después del juego | ¿Fue la primera vez que jugaron el escenario? | `grafico_primera_vez` |
| Después del juego | Conexión con pensamiento computacional al finalizar | `grafico_conexion_pc` |
| Después del juego | Tipo de espacio usado para el cierre | `grafico_cierre_actividad` |

---

## Consideraciones técnicas

### Manejo de columnas faltantes

Cada función de gráfico llama `_validar_columnas(df, [...], "nombre_grafico")` al inicio:
- Si **todas** las columnas requeridas existen → continúa normalmente.
- Si **alguna** falta → muestra `st.warning` con las columnas faltantes y retorna sin renderizar.

Para gráficas de tipo multi-select (`grafico_introduccion_juego`, `grafico_materiales_docente`, etc.), el comportamiento es más tolerante: opera con las columnas que sí existen y omite las faltantes.

### Normalización de sedes por DANE

La función `_normalizar_sede(df)` agrupa por `COL_DANE` y retorna el nombre de sede más frecuente para cada código. Esto evita que el mismo colegio aparezca con nombres ligeramente distintos en el treemap y la mariposa.

### Espacio en nombres de columna

Al cargar el CSV, se aplica `df.columns.str.strip()`. Las constantes deben definirse **sin** espacios al inicio ni al final. Si el Google Sheet modifica un nombre de columna agregando o quitando espacios, actualizar la constante correspondiente en `actions/docentes_observados_actions.py`.
