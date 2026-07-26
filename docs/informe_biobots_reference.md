# Referencia: Informe Biobots

Guía para trabajar y modificar los archivos que componen la página **Informe Biobots** dentro de la app Streamlit de CodingHubs.

---

## Estructura de archivos

```
app_pages/informe_biobots.py        ← Página Streamlit (UI + carga de datos)
actions/informe_biobots_actions.py  ← Lógica de gráficas y transformaciones
docs/informe_biobots_reference.md   ← Este archivo
```

La página se registra en `app.py` bajo la sección `"Informe Biobots"` con ruta `/informe_biobots`.

---

## `app_pages/informe_biobots.py`

### Responsabilidades
- Configurar el encabezado de la página.
- Definir la URL de descarga del Google Sheet (`datos_biobots_og`).
- Cachear la carga del CSV con `@st.cache_data(ttl=600)`.
- Llamar a las funciones de graficación definidas en `actions/`.

### Fuente de datos

| Parámetro | Valor |
|-----------|-------|
| Google Sheet ID | `1GPoooJUN7OQ55BsOB7usBizqQXBCcN3K` |
| GID de la hoja | `963668480` |
| Formato descarga | CSV vía URL pública de Google Sheets |
| TTL caché | 600 segundos (10 min) |

```python
SHEET_ID = "1GPoooJUN7OQ55BsOB7usBizqQXBCcN3K"
GID      = "963668480"
CSV_URL  = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
```

### Patrón para agregar una nueva sección

1. Importar la nueva función de `actions/informe_biobots_actions.py`.
2. Añadir un `st.subheader(...)` descriptivo.
3. Llamar la función pasando `df_consolidado` y `chart_config`.

```python
from actions.informe_biobots_actions import nueva_funcion_grafico

st.subheader("Título de la sección")
nueva_funcion_grafico(df_consolidado, chart_config)
```

### Cómo actualizar la hoja de datos

Para apuntar a otra pestaña del mismo Sheet, cambia el `GID`. Para otro Sheet completo, cambia `SHEET_ID`. La URL se recompone automáticamente.

---

## `actions/informe_biobots_actions.py`

### Responsabilidades
- Definir constantes de nombres de columnas, valores categóricos y paletas de color.
- Normalizar valores sucios del CSV (tildes, mayúsculas, variantes de texto).
- Construir y renderizar las gráficas con Plotly + `st.plotly_chart`.

### Constantes definidas

```python
# Columnas
COL_SEXO        = "Sexo"
COL_CIUDAD      = "Ciudad"
COL_GRADO       = "Grado"
COL_EDAD        = "Edad"
COL_INSTITUCION = "Nombre_institución"

# Valores ordenados
CIUDADES_ORDEN   = ["Bucaramanga", "Manizales"]
GRADOS_ORDEN     = ["Cuarto", "Quinto"]
EDADES_ORDEN_STR = ["8", "9", "10", "11", "12", "13"]
SEXO_CATEGORIAS  = ["Niño", "Niña", "Prefiero no decir"]

# Paletas
GRADO_COLORES        = {"Cuarto": "#83C9FF", "Quinto": "#0068C9"}
ESTEREOTIPO_COLORES  = {"Hombre": "#83C9FF", "Mujer": "#0068C9",
                        "Cualquiera de los dos": "#662482", "No responde": "#9CA3AF"}
OPCIONES_PC_COLORES  = {"A": "#83C9FF", "B": "#0068C9", "C": "#662482",
                        "D": "#e5007e", "E": "#9CA3AF"}

# Ítems PC
ITEMS_PC_TODOS = [
    "PC_secuencia", "PC_organizar", "PC_pistas",        # A–E
    "PC_palabra", "PC_algoritmo_2_hormiga", "PC_error_capi",
    "PC_algoritmo_1", "PC_algoritmo_giro", "PC_clave_alien",
    "PC_algoritmo4_gato", "PC_almoritmo3_queso",         # A–D
]
```

Los diccionarios `SEXO_ALIASES` y `CIUDAD_ALIASES` normalizan variantes ortográficas del CSV antes de graficar.

### Helper privado

#### `_grafico_barras_ciudad_categoria(df, col_categoria, categorias_orden, titulo, leyenda_titulo, colores, chart_config)`

Lógica reutilizable para barras verticales agrupadas `Ciudad × categoría`. Usado internamente por `grafico_distribucion_ciudad_grado` y `grafico_distribucion_ciudad_edad`.

---

## Gráficas implementadas

### `grafico_mariposa_sexo(df, chart_config)` ✅

Barras horizontales tipo "mariposa": Niño a la izquierda, Niña a la derecha, Prefiero no decir centrado.

| Elemento | Detalle |
|----------|---------|
| Eje Y | Ciudad (Bucaramanga, Manizales) |
| Eje X | Conteo (negativo = Niño, positivo = Niña, centrado = Prefiero no decir) |
| Columnas requeridas | `Sexo`, `Ciudad` |
| Colores | Niño `#83C9FF`, Niña `#0068C9`, Prefiero no decir `#9CA3AF` |
| Expander | Tabla de conteos por ciudad y sexo |

---

### `grafico_distribucion_ciudad_grado(df, chart_config)` ✅

Barras verticales agrupadas: número de estudiantes por ciudad y grado escolar.

| Elemento | Detalle |
|----------|---------|
| Eje X | Ciudad |
| Eje Y | Número de estudiantes |
| Color | Grado (Cuarto `#83C9FF`, Quinto `#0068C9`) |
| Columnas requeridas | `Ciudad`, `Grado` |
| Expander | Tabla de conteos por ciudad y grado |

---

### `grafico_distribucion_ciudad_edad(df, chart_config)` ✅

Barras verticales agrupadas: número de estudiantes por ciudad y edad.

| Elemento | Detalle |
|----------|---------|
| Eje X | Ciudad |
| Eje Y | Número de estudiantes |
| Color | Edad (8–13, escala de azul claro a azul muy oscuro) |
| Columnas requeridas | `Ciudad`, `Edad` |
| Expander | Tabla de conteos por ciudad y edad |

> La columna `Edad` se convierte a string antes de agrupar; los valores esperados son `"8"` a `"13"`.

---

### `grafico_treemap_instituciones(df, chart_config)` ✅

Treemap jerárquico: Ciudad → Institución educativa, con color según número de estudiantes.

| Elemento | Detalle |
|----------|---------|
| Jerarquía | Ciudad (nivel 1) → Nombre_institución (nivel 2) |
| Valor | Conteo de estudiantes por institución |
| Color | Escala continua azul claro → azul muy oscuro |
| Columnas requeridas | `Ciudad`, `Nombre_institución` |
| Expander | Tabla de conteos por institución ordenada descendente |

---

### `grafico_estereotipos_genero(df, chart_config)` ✅

Barras 100 % stacked horizontales: distribución de respuestas de estereotipos de género para cada profesión.

| Elemento | Detalle |
|----------|---------|
| Eje Y | Profesión (9 categorías) |
| Eje X | Porcentaje (0–100 %) |
| Color | Categoría de respuesta: Hombre / Mujer / Cualquiera de los dos / No responde |
| Columnas requeridas | `Programador/a`, `Policía`, `Bailarín/a`, `Médico/a`, `Ingeniero/a`, `Psicólogo/a`, `Biólogo/a`, `Matemático/a`, `Docente` |
| Expander | Tabla de porcentajes por profesión |

Paleta de colores:

| Respuesta | Color |
|-----------|-------|
| Hombre | `#83C9FF` |
| Mujer | `#0068C9` |
| Cualquiera de los dos | `#662482` |
| No responde | `#9CA3AF` |

---

### `grafico_respuestas_items_pc(df, chart_config)` ✅

Barras 100 % stacked horizontales: distribución de opciones elegidas (A–E) por ítem de Pensamiento Computacional.

| Elemento | Detalle |
|----------|---------|
| Eje Y | Nombre corto del ítem (11 ítems) |
| Eje X | Porcentaje (0–100 %) |
| Color | Opción elegida (A–E) |
| Columnas requeridas | Los 11 ítems `PC_*` |
| Expander | Tabla de conteos absolutos por ítem y opción |

Nombres cortos de ítems:

| Columna original | Nombre en gráfica |
|------------------|-------------------|
| `PC_secuencia` | Secuencia |
| `PC_organizar` | Organizar |
| `PC_pistas` | Pistas |
| `PC_palabra` | Palabra |
| `PC_algoritmo_2_hormiga` | Alg. hormiga |
| `PC_error_capi` | Error Capi |
| `PC_algoritmo_1` | Algoritmo 1 |
| `PC_algoritmo_giro` | Alg. giro |
| `PC_clave_alien` | Clave alien |
| `PC_algoritmo4_gato` | Alg. gato |
| `PC_almoritmo3_queso` | Alg. queso |

> `PC_almoritmo3_queso` tiene un error tipográfico en la fuente original. Mantener tal cual al referenciar la columna.

---

### `grafico_boxplot_puntaje_pc(df, chart_config)` ✅

Boxplot de `puntaje_PC` (0–50) agrupado por ciudad, con color por sexo.

| Elemento | Detalle |
|----------|---------|
| Eje X | Ciudad (Bucaramanga, Manizales) |
| Eje Y | Puntaje PC (0–50) |
| Color | Sexo (Niño `#83C9FF`, Niña `#0068C9`, Prefiero no decir `#9CA3AF`) |
| Puntos | Outliers visibles |
| Columnas requeridas | `puntaje_PC`, `Ciudad`, `Sexo` |
| Expander | Tabla de estadísticos (N, media, mediana, mín, máx, desv. est.) por ciudad y sexo |

---

### `grafico_histograma_puntaje_pc(df, chart_config)` ✅

Histograma superpuesto de `puntaje_PC` por ciudad, con líneas de media.

| Elemento | Detalle |
|----------|---------|
| Eje X | Puntaje PC (0–50, 15 bins) |
| Eje Y | Número de estudiantes |
| Color | Ciudad (Bucaramanga `#83C9FF`, Manizales `#0068C9`) |
| Modo barras | `overlay` con opacidad 0.75 |
| Anotaciones | Línea vertical discontinua con media por ciudad |
| Columnas requeridas | `puntaje_PC`, `Ciudad` |
| Expander | Tabla de estadísticos por ciudad |

---

### `grafico_distribucion_aciertos_pc(df, chart_config)` ✅

Barras agrupadas de frecuencia: distribución de aciertos en PC expresada como porcentaje.

| Elemento | Detalle |
|----------|---------|
| Eje X | Porcentaje de aciertos (9 %, 18 %, …, 100 %) |
| Eje Y | Número de estudiantes |
| Color | Ciudad |
| Columnas requeridas | `aciertos_PC`, `Ciudad` |
| Conversión | `aciertos_PC × 100` redondeado a entero |
| Expander | Tabla de conteos por ciudad y nivel de aciertos |

---

### `grafico_distribucion_aciertos_egma(df, chart_config)` ✅

Barras agrupadas de frecuencia: distribución de aciertos EGMA expresada como porcentaje.

| Elemento | Detalle |
|----------|---------|
| Eje X | Porcentaje de aciertos EGMA (0 %, 20 %, 40 %, 60 %, 80 %, 100 %) |
| Eje Y | Número de estudiantes |
| Color | Ciudad |
| Columnas requeridas | `aciertos_P_EGMA`, `Ciudad` |
| Conversión | `aciertos_P_EGMA × 100` redondeado a entero |
| Expander | Tabla de conteos por ciudad y nivel de aciertos |

---

### `grafico_correlacion_pc_egma(df, chart_config)` ✅

Scatter plot con línea de tendencia OLS por ciudad: relación entre puntaje PC y aciertos EGMA.

| Elemento | Detalle |
|----------|---------|
| Eje X | `puntaje_PC` (0–50) |
| Eje Y | `aciertos_P_EGMA` × 100 (0–100 %) |
| Color | Ciudad (Bucaramanga `#83C9FF`, Manizales `#0068C9`) |
| Línea de tendencia | Regresión lineal OLS por ciudad (`trendline="ols"`, requiere `statsmodels`) |
| Columnas requeridas | `puntaje_PC`, `aciertos_P_EGMA`, `Ciudad` |
| Expander | Tabla con N y coeficiente de Pearson r por ciudad |

---

## Gráficas pendientes

Todas las gráficas están implementadas.

---

## Patrón para agregar una nueva función de gráfica

```python
def grafico_nueva(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Descripción del gráfico."""
    if chart_config is None:
        chart_config = get_chart_config()

    # 1. Validar columnas requeridas
    columnas_requeridas = ["ColumnaA", "ColumnaB"]
    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        st.warning(f"Columnas faltantes: {', '.join(faltantes)}")
        return

    # 2. Limpiar / transformar datos
    work = df[columnas_requeridas].copy()
    # ... normalización ...

    # 3. Construir figura Plotly
    fig = go.Figure()   # o px.bar / px.treemap
    # ... trazas ...

    # 4. Renderizar
    st.plotly_chart(fig, width="stretch", config=chart_config)

    # 5. Tabla opcional
    with st.expander("Ver tabla..."):
        st.dataframe(...)
```

---

## Resumen de datos: `datos_biobots_og`

### Variables de identificación

| Variable | Descripción |
|----------|-------------|
| `Nombre_institución` | 11 instituciones únicas (INEM Custodio García Rovira Sede B, Institución Educativa de Santander, Instituto Latinoamericano Sede A, Instituto Técnico Francisco José de Caldas, entre otras) |
| `Nombre_estudiante` | Identificador de texto libre, único por persona |
| `ID_estudiante` | Identificador numérico único por persona |

### Variables sociodemográficas

| Variable | Valores posibles |
|----------|-----------------|
| `Sexo` | `Niña`, `Niño`, `Prefiero no decir` |
| `Edad` | `8`, `9`, `10`, `11`, `12`, `13` (años) |
| `Grado` | `Cuarto`, `Quinto` |
| `Momento` | `pre_2026` (valor único — todos son medición previa) |
| `Ciudad` | `Bucaramanga`, `Manizales` |

### Puntajes y aciertos

| Variable | Tipo | Rango / Valores |
|----------|------|-----------------|
| `puntaje_PC` | Continua | 0 a 50 |
| `aciertos_PC` | Proporción | Fracciones de 11vos: `0.09, 0.18, 0.27, 0.36, 0.45, 0.55, 0.64, 0.73, 0.82, 0.91, 1.0` |
| `aciertos_P_EGMA` | Proporción | Pasos de 0.2: `0.0, 0.2, 0.4, 0.6, 0.8, 1.0` |

### Estereotipos de género por profesión

9 variables, una por profesión. Todas toman los mismos valores.

**Profesiones:** `Programador/a`, `Policía`, `Bailarín/a`, `Médico/a`, `Ingeniero/a`, `Psicólogo/a`, `Biólogo/a`, `Matemático/a`, `Docente`

**Valores:** `Hombre`, `Mujer`, `Cualquiera de los dos`, `No responde`

### Ítems de Pensamiento Computacional (PC) — opción múltiple

| Variable | Opciones |
|----------|----------|
| `PC_secuencia` | A, B, C, D, E |
| `PC_organizar` | A, B, C, D, E |
| `PC_pistas` | A, B, C, D, E |
| `PC_palabra` | A, B, C, D |
| `PC_algoritmo_2_hormiga` | A, B, C, D |
| `PC_error_capi` | A, B, C, D |
| `PC_algoritmo_1` | A, B, C, D |
| `PC_algoritmo_giro` | A, B, C, D |
| `PC_clave_alien` | A, B, C, D |
| `PC_algoritmo4_gato` | A, B, C, D |
| `PC_almoritmo3_queso` | A, B, C, D |

### Ítems EGMA (matemáticas)

| Variable | Tipo | Rango |
|----------|------|-------|
| `P_EGMA_1` | Continua | 0 a 5000 |
| `P_EGMA_2` | Continua | 0 a 874 |
| `P_EGMA_3` | Continua | 0 a 49 |
| `P_EGMA_5` | Continua | 0 a 300 |
| `P_EGMA_4` | Categórica | A, B, C, D, E |

---

## Estado actual de gráficas

| Gráfica | Función | Estado | Columnas usadas |
|---------|---------|--------|-----------------|
| Distribución por sexo y ciudad | `grafico_mariposa_sexo` | ✅ Implementada | `Sexo`, `Ciudad` |
| Distribución por ciudad y grado | `grafico_distribucion_ciudad_grado` | ✅ Implementada | `Ciudad`, `Grado` |
| Distribución por ciudad y edad | `grafico_distribucion_ciudad_edad` | ✅ Implementada | `Ciudad`, `Edad` |
| Distribución por institución | `grafico_treemap_instituciones` | ✅ Implementada | `Ciudad`, `Nombre_institución` |
| Estereotipos de género | `grafico_estereotipos_genero` | ✅ Implementada | 9 columnas de profesión |
| Respuestas por ítem PC | `grafico_respuestas_items_pc` | ✅ Implementada | 11 ítems `PC_*` |
| Boxplot puntaje PC por ciudad y sexo | `grafico_boxplot_puntaje_pc` | ✅ Implementada | `puntaje_PC`, `Ciudad`, `Sexo` |
| Histograma puntaje PC | `grafico_histograma_puntaje_pc` | ✅ Implementada | `puntaje_PC`, `Ciudad` |
| Distribución aciertos PC | `grafico_distribucion_aciertos_pc` | ✅ Implementada | `aciertos_PC`, `Ciudad` |
| Distribución aciertos EGMA | `grafico_distribucion_aciertos_egma` | ✅ Implementada | `aciertos_P_EGMA`, `Ciudad` |
| Correlación PC vs EGMA | `grafico_correlacion_pc_egma` | ✅ Implementada | `puntaje_PC`, `aciertos_P_EGMA`, `Ciudad` |

---

## Dependencias relevantes

| Módulo | Uso |
|--------|-----|
| `streamlit` | UI, caché, widgets |
| `pandas` | Carga y transformación del CSV |
| `plotly.graph_objects` | Gráficos mariposa (trazas manuales) |
| `plotly.express` | Barras agrupadas, treemap, stacked bars |
| `utils.chart_config.get_chart_config` | Config de exportación PNG (escala 3x) |
| `constants.header_constants.header` | Encabezado corporativo con color `#282255` |
| `constants.footer_constants` | Pie de página HTML |

---

## Notas de estilo

- Usar `barmode="overlay"` con valores negativos para gráficos mariposa (`go.Figure`).
- Usar `barmode="stack"` con `px.bar` para gráficos 100 % stacked.
- Siempre pasar `width="stretch"` a `st.plotly_chart` para que la gráfica ocupe todo el ancho.
- Envolver tablas de detalle en `st.expander("Ver tabla...")` para no saturar la vista.
- Validar columnas requeridas al inicio de cada función y emitir `st.warning` en lugar de lanzar excepciones.
- Para barras stacked con porcentajes, calcular el porcentaje dentro del DataFrame antes de graficar, no usar `barnorm` de Plotly.
