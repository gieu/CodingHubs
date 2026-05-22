import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.chart_config import get_chart_config

# ── Nombres de columnas ────────────────────────────────────────────────────

COL_SEXO = "Sexo"
COL_CIUDAD = "Ciudad"
COL_GRADO = "Grado"
COL_EDAD = "Edad"
COL_INSTITUCION = "Nombre_institución"

# ── Valores ordenados ──────────────────────────────────────────────────────

CIUDADES_ORDEN = ["Bucaramanga", "Manizales"]
GRADOS_ORDEN = ["Cuarto", "Quinto"]
EDADES_ORDEN_STR = ["8", "9", "10", "11", "12", "13"]

SEXO_NINO = "Niño"
SEXO_NINA = "Niña"
SEXO_PREFIERO = "Prefiero no decir"
SEXO_CATEGORIAS = [SEXO_NINO, SEXO_NINA, SEXO_PREFIERO]

# ── Paletas de color ──────────────────────────────────────────────────────

GRADO_COLORES = {
    "Cuarto": "#83C9FF",
    "Quinto": "#0068C9",
}

EDAD_COLORES = {
    "8": "#D5E8F5",
    "9": "#83C9FF",
    "10": "#0068C9",
    "11": "#662482",
    "12": "#e5007e",
    "13": "#23085a",
}

# ── Estereotipos de género ─────────────────────────────────────────────────

PROFESIONES = [
    "Programador/a",
    "Policía",
    "Bailarín/a",
    "Médico/a",
    "Ingeniero/a",
    "Psicólogo/a",
    "Biólogo/a",
    "Matemático/a",
    "Docente",
]

ESTEREOTIPO_CATEGORIAS = ["Hombre", "Mujer", "Cualquiera de los dos", "No responde"]

ESTEREOTIPO_COLORES = {
    "Hombre": "#83C9FF",
    "Mujer": "#0068C9",
    "Cualquiera de los dos": "#662482",
    "No responde": "#9CA3AF",
}

# ── Ítems de Pensamiento Computacional ───────────────────────────────────

ITEMS_PC_5_OPCIONES = ["PC_secuencia", "PC_organizar", "PC_pistas"]
ITEMS_PC_4_OPCIONES = [
    "PC_palabra",
    "PC_algoritmo_2_hormiga",
    "PC_error_capi",
    "PC_algoritmo_1",
    "PC_algoritmo_giro",
    "PC_clave_alien",
    "PC_algoritmo4_gato",
    "PC_almoritmo3_queso",
]
ITEMS_PC_TODOS = ITEMS_PC_5_OPCIONES + ITEMS_PC_4_OPCIONES

ITEM_PC_NOMBRES = {
    "PC_secuencia": "Secuencia",
    "PC_organizar": "Organizar",
    "PC_pistas": "Pistas",
    "PC_palabra": "Palabra",
    "PC_algoritmo_2_hormiga": "Alg. hormiga",
    "PC_error_capi": "Error Capi",
    "PC_algoritmo_1": "Algoritmo 1",
    "PC_algoritmo_giro": "Alg. giro",
    "PC_clave_alien": "Clave alien",
    "PC_algoritmo4_gato": "Alg. gato",
    "PC_almoritmo3_queso": "Alg. queso",
}

OPCIONES_PC_COLORES = {
    "A": "#83C9FF",
    "B": "#0068C9",
    "C": "#662482",
    "D": "#e5007e",
    "E": "#9CA3AF",
}

# ── Aliases de normalización ──────────────────────────────────────────────

SEXO_ALIASES = {
    "nino": SEXO_NINO,
    "niño": SEXO_NINO,
    "nina": SEXO_NINA,
    "niña": SEXO_NINA,
    "prefiero no decir": SEXO_PREFIERO,
    "prefiero no decirlo": SEXO_PREFIERO,
    "no especifica": SEXO_PREFIERO,
}

CIUDAD_ALIASES = {
    "bucaramanga": "Bucaramanga",
    "manizales": "Manizales",
}


def _normalizar_sexo(valor) -> str | None:
    if pd.isna(valor):
        return None
    texto = str(valor).strip()
    if not texto or texto.lower() in {"nan", "none", ""}:
        return None
    clave = texto.lower()
    if clave in SEXO_ALIASES:
        return SEXO_ALIASES[clave]
    for categoria in SEXO_CATEGORIAS:
        if texto.lower() == categoria.lower():
            return categoria
    return texto


def _normalizar_ciudad(valor) -> str | None:
    if pd.isna(valor):
        return None
    texto = str(valor).strip()
    if not texto or texto.lower() in {"nan", "none", ""}:
        return None
    clave = texto.lower()
    if clave in CIUDAD_ALIASES:
        return CIUDAD_ALIASES[clave]
    for ciudad in CIUDADES_ORDEN:
        if texto.lower() == ciudad.lower():
            return ciudad
    return texto


def grafico_mariposa_sexo(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Gráfico mariposa: Sexo (Niño, Niña, Prefiero no decir) por Ciudad."""
    if chart_config is None:
        chart_config = get_chart_config()

    columnas_requeridas = [COL_SEXO, COL_CIUDAD]
    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        st.warning(
            f"No se encontraron las columnas necesarias: {', '.join(faltantes)}. "
            f"Columnas disponibles: {', '.join(df.columns)}"
        )
        return

    work = df[[COL_CIUDAD, COL_SEXO]].copy()
    work[COL_SEXO] = work[COL_SEXO].map(_normalizar_sexo)
    work[COL_CIUDAD] = work[COL_CIUDAD].map(_normalizar_ciudad)
    work = work.dropna(subset=[COL_CIUDAD, COL_SEXO])

    if work.empty:
        st.warning("No hay registros válidos en las columnas Ciudad y Sexo.")
        return

    df_grouped = (
        work.groupby([COL_CIUDAD, COL_SEXO], as_index=False)
        .size()
        .rename(columns={"size": "Registros"})
    )

    pivot = (
        df_grouped.pivot(index=COL_CIUDAD, columns=COL_SEXO, values="Registros")
        .fillna(0)
        .reindex(index=CIUDADES_ORDEN, columns=SEXO_CATEGORIAS, fill_value=0)
    )

    # Mantener solo ciudades presentes en los datos
    pivot = pivot.loc[pivot.sum(axis=1) > 0]
    if pivot.empty:
        st.warning(
            f"No hay datos para las ciudades esperadas ({', '.join(CIUDADES_ORDEN)})."
        )
        return

    ciudades = pivot.index.tolist()
    nino = pivot[SEXO_NINO].astype(int).values
    nina = pivot[SEXO_NINA].astype(int).values
    prefiero = pivot[SEXO_PREFIERO].astype(int).values
    nino_neg = -nino
    prefiero_base = [-p / 2 for p in prefiero]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=ciudades,
            x=nino_neg,
            name=SEXO_NINO,
            orientation="h",
            marker_color="#83C9FF",
            text=[f"<b>{abs(int(v))}</b>" for v in nino_neg],
            textposition="outside",
            textfont=dict(size=13),
        )
    )

    fig.add_trace(
        go.Bar(
            y=ciudades,
            x=prefiero,
            base=prefiero_base,
            name=SEXO_PREFIERO,
            orientation="h",
            marker_color="#9CA3AF",
            text=[f"<b>{int(v)}</b>" if v > 0 else "" for v in prefiero],
            textposition="inside",
            textfont=dict(size=12),
        )
    )

    fig.add_trace(
        go.Bar(
            y=ciudades,
            x=nina,
            name=SEXO_NINA,
            orientation="h",
            marker_color="#0068C9",
            text=[f"<b>{int(v)}</b>" for v in nina],
            textposition="outside",
            textfont=dict(size=13),
        )
    )

    max_val = max(int(nino.max()), int(nina.max()), int(prefiero.max()), 1) * 1.15
    fig.update_layout(
        title="Distribución por sexo y ciudad (gráfico mariposa)",
        barmode="overlay",
        xaxis=dict(
            tickvals=[-max_val, -max_val / 2, 0, max_val / 2, max_val],
            ticktext=[
                str(int(max_val)),
                str(int(max_val / 2)),
                "0",
                str(int(max_val / 2)),
                str(int(max_val)),
            ],
            title="Número de registros",
        ),
        yaxis=dict(title="Ciudad"),
        legend_title=COL_SEXO,
        template="plotly_white",
        margin=dict(t=100, b=40, l=80, r=40),
        bargap=0.15,
        showlegend=True,
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)

    with st.expander("Ver tabla de conteos por ciudad y sexo"):
        tabla = pivot.reset_index()
        tabla.columns.name = None
        st.dataframe(tabla, hide_index=True)


# ── Helper privado: barras verticales agrupadas Ciudad × categoría ────────

def _grafico_barras_ciudad_categoria(
    df: pd.DataFrame,
    col_categoria: str,
    categorias_orden: list,
    titulo: str,
    leyenda_titulo: str,
    colores: dict,
    chart_config: dict,
) -> None:
    columnas_requeridas = [COL_CIUDAD, col_categoria]
    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        st.warning(
            f"No se encontraron las columnas necesarias: {', '.join(faltantes)}. "
            f"Columnas disponibles: {', '.join(df.columns)}"
        )
        return

    work = df[[COL_CIUDAD, col_categoria]].copy()
    work[COL_CIUDAD] = work[COL_CIUDAD].map(_normalizar_ciudad)
    work[col_categoria] = work[col_categoria].astype(str).str.strip()
    work = work.dropna(subset=[COL_CIUDAD])
    work = work[~work[col_categoria].str.upper().isin({"NAN", "NONE", ""})]

    if work.empty:
        st.warning(f"No hay registros válidos para Ciudad y {leyenda_titulo}.")
        return

    df_grouped = (
        work.groupby([COL_CIUDAD, col_categoria], as_index=False)
        .size()
        .rename(columns={"size": "Estudiantes"})
    )

    df_grouped = df_grouped[df_grouped[col_categoria].isin(categorias_orden)]
    if df_grouped.empty:
        st.warning(f"No hay datos que coincidan con las categorías esperadas de {leyenda_titulo}.")
        return

    df_grouped[col_categoria] = pd.Categorical(
        df_grouped[col_categoria], categories=categorias_orden, ordered=True
    )
    df_grouped = df_grouped.sort_values([COL_CIUDAD, col_categoria])

    fig = px.bar(
        df_grouped,
        x=COL_CIUDAD,
        y="Estudiantes",
        color=col_categoria,
        barmode="group",
        title=titulo,
        color_discrete_map=colores,
        text="Estudiantes",
        category_orders={COL_CIUDAD: CIUDADES_ORDEN, col_categoria: categorias_orden},
    )

    y_max = df_grouped["Estudiantes"].max() * 1.15

    for trace in fig.data:
        trace.texttemplate = "<b>%{text}</b>"
        trace.textposition = "outside"
        trace.textfont = dict(size=13)

    fig.update_layout(
        xaxis_title="Ciudad",
        yaxis_title="Número de estudiantes",
        legend_title=leyenda_titulo,
        template="plotly_white",
        margin=dict(t=100, b=40, l=60, r=40),
        yaxis=dict(range=[0, y_max]),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)

    with st.expander(f"Ver tabla de conteos por ciudad y {leyenda_titulo.lower()}"):
        pivot = (
            df_grouped.pivot(index=COL_CIUDAD, columns=col_categoria, values="Estudiantes")
            .fillna(0)
            .astype(int)
        )
        pivot.columns.name = None
        st.dataframe(pivot.reset_index(), hide_index=True)


# ── Gráfica 2: Distribución Ciudad × Grado ───────────────────────────────

def grafico_distribucion_ciudad_grado(
    df: pd.DataFrame, chart_config: dict | None = None
) -> None:
    """Barras agrupadas: número de estudiantes por ciudad y grado escolar."""
    if chart_config is None:
        chart_config = get_chart_config()
    _grafico_barras_ciudad_categoria(
        df=df,
        col_categoria=COL_GRADO,
        categorias_orden=GRADOS_ORDEN,
        titulo="Distribución de estudiantes por ciudad y grado",
        leyenda_titulo="Grado",
        colores=GRADO_COLORES,
        chart_config=chart_config,
    )


# ── Gráfica 3: Distribución Ciudad × Edad ────────────────────────────────

def grafico_distribucion_ciudad_edad(
    df: pd.DataFrame, chart_config: dict | None = None
) -> None:
    """Barras agrupadas: número de estudiantes por ciudad y edad."""
    if chart_config is None:
        chart_config = get_chart_config()
    _grafico_barras_ciudad_categoria(
        df=df,
        col_categoria=COL_EDAD,
        categorias_orden=EDADES_ORDEN_STR,
        titulo="Distribución de estudiantes por ciudad y edad",
        leyenda_titulo="Edad",
        colores=EDAD_COLORES,
        chart_config=chart_config,
    )


# ── Gráfica 4: Treemap por institución ───────────────────────────────────

def grafico_treemap_instituciones(
    df: pd.DataFrame, chart_config: dict | None = None
) -> None:
    """Treemap jerárquico: estudiantes por ciudad → institución."""
    if chart_config is None:
        chart_config = get_chart_config()

    columnas_requeridas = [COL_CIUDAD, COL_INSTITUCION]
    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        st.warning(
            f"No se encontraron las columnas necesarias: {', '.join(faltantes)}. "
            f"Columnas disponibles: {', '.join(df.columns)}"
        )
        return

    work = df[[COL_CIUDAD, COL_INSTITUCION]].copy()
    work[COL_CIUDAD] = work[COL_CIUDAD].map(_normalizar_ciudad)
    work[COL_INSTITUCION] = work[COL_INSTITUCION].astype(str).str.strip()
    work = work.dropna(subset=[COL_CIUDAD])
    work = work[~work[COL_INSTITUCION].str.upper().isin({"NAN", "NONE", ""})]

    if work.empty:
        st.warning("No hay registros válidos para Institución y Ciudad.")
        return

    df_counts = (
        work.groupby([COL_CIUDAD, COL_INSTITUCION], as_index=False)
        .size()
        .rename(columns={"size": "Estudiantes"})
    )

    fig = px.treemap(
        df_counts,
        path=[COL_CIUDAD, COL_INSTITUCION],
        values="Estudiantes",
        title="Distribución de estudiantes por institución y ciudad",
        color="Estudiantes",
        color_continuous_scale=[
            [0.0, "#83C9FF"],
            [0.5, "#0068C9"],
            [1.0, "#23085a"],
        ],
        hover_data={"Estudiantes": True},
    )

    fig.update_traces(
        texttemplate="<b>%{label}</b><br>%{value} est. (%{percentRoot:.1%})",
        textfont=dict(size=12, color="white"),
        marker=dict(line=dict(color="white", width=2)),
    )

    fig.update_layout(
        height=520,
        margin=dict(t=80, b=40, l=40, r=40),
        font=dict(size=11, color="#2C3E50"),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)

    with st.expander("Ver tabla de conteos por institución"):
        tabla = df_counts.sort_values("Estudiantes", ascending=False)
        st.dataframe(tabla, hide_index=True)


# ── Gráfica 5: Estereotipos de género ────────────────────────────────────

def grafico_estereotipos_genero(
    df: pd.DataFrame, chart_config: dict | None = None
) -> None:
    """Barras 100 % stacked horizontales: distribución de respuestas de estereotipos de género por profesión."""
    if chart_config is None:
        chart_config = get_chart_config()

    cols_presentes = [p for p in PROFESIONES if p in df.columns]
    if not cols_presentes:
        st.warning(
            f"No se encontraron columnas de profesiones. "
            f"Esperadas: {', '.join(PROFESIONES)}. "
            f"Disponibles: {', '.join(df.columns)}"
        )
        return

    df_long = (
        df[cols_presentes]
        .melt(var_name="Profesión", value_name="Respuesta")
    )
    df_long["Respuesta"] = df_long["Respuesta"].astype(str).str.strip()
    df_long = df_long[~df_long["Respuesta"].str.upper().isin({"NAN", "NONE", ""})]

    if df_long.empty:
        st.warning("No hay datos válidos para los estereotipos de género.")
        return

    def _normalizar_estereotipo(val: str) -> str:
        for cat in ESTEREOTIPO_CATEGORIAS:
            if val.strip().lower() == cat.lower():
                return cat
        return "No responde"

    df_long["Respuesta"] = df_long["Respuesta"].apply(_normalizar_estereotipo)

    df_counts = (
        df_long.groupby(["Profesión", "Respuesta"], as_index=False)
        .size()
        .rename(columns={"size": "Frecuencia"})
    )

    totales = df_counts.groupby("Profesión")["Frecuencia"].transform("sum")
    df_counts["Porcentaje"] = (df_counts["Frecuencia"] / totales * 100).round(1)

    df_counts["Profesión"] = pd.Categorical(
        df_counts["Profesión"], categories=cols_presentes, ordered=True
    )
    df_counts["Respuesta"] = pd.Categorical(
        df_counts["Respuesta"], categories=ESTEREOTIPO_CATEGORIAS, ordered=True
    )
    df_counts = df_counts.sort_values(["Profesión", "Respuesta"])

    fig = px.bar(
        df_counts,
        y="Profesión",
        x="Porcentaje",
        color="Respuesta",
        orientation="h",
        title="Estereotipos de género por profesión",
        color_discrete_map=ESTEREOTIPO_COLORES,
        text="Porcentaje",
        category_orders={
            "Profesión": cols_presentes,
            "Respuesta": ESTEREOTIPO_CATEGORIAS,
        },
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="inside",
        textfont=dict(size=11),
        insidetextanchor="middle",
    )

    fig.update_layout(
        barmode="stack",
        xaxis_title="Porcentaje (%)",
        yaxis_title="Profesión",
        legend_title="Respuesta",
        template="plotly_white",
        margin=dict(t=100, b=40, l=140, r=40),
        xaxis=dict(range=[0, 100]),
        height=max(420, len(cols_presentes) * 52),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)

    with st.expander("Ver tabla de frecuencias y porcentajes por profesión"):
        pivot = (
            df_counts.pivot(index="Profesión", columns="Respuesta", values="Porcentaje")
            .fillna(0)
            .round(1)
        )
        pivot.columns.name = None
        st.dataframe(pivot.reset_index(), hide_index=True)


# ── Gráfica 6: Respuestas por ítem de Pensamiento Computacional ──────────

def grafico_respuestas_items_pc(
    df: pd.DataFrame, chart_config: dict | None = None
) -> None:
    """Barras 100 % stacked: distribución de respuestas (A–E) por ítem de PC."""
    if chart_config is None:
        chart_config = get_chart_config()

    cols_presentes = [c for c in ITEMS_PC_TODOS if c in df.columns]
    if not cols_presentes:
        st.warning(
            f"No se encontraron columnas de ítems PC. "
            f"Columnas disponibles: {', '.join(df.columns)}"
        )
        return

    df_long = df[cols_presentes].melt(var_name="Item_raw", value_name="Respuesta")
    df_long["Ítem"] = df_long["Item_raw"].map(ITEM_PC_NOMBRES)
    df_long["Respuesta"] = df_long["Respuesta"].astype(str).str.strip().str.upper()
    df_long = df_long[~df_long["Respuesta"].isin({"NAN", "NONE", ""})]

    todas_opciones = ["A", "B", "C", "D", "E"]
    df_long = df_long[df_long["Respuesta"].isin(todas_opciones)]

    if df_long.empty:
        st.warning("No hay respuestas válidas en los ítems de Pensamiento Computacional.")
        return

    df_counts = (
        df_long.groupby(["Item_raw", "Ítem", "Respuesta"], as_index=False)
        .size()
        .rename(columns={"size": "Frecuencia"})
    )

    totales = df_counts.groupby("Ítem")["Frecuencia"].transform("sum")
    df_counts["Porcentaje"] = (df_counts["Frecuencia"] / totales * 100).round(1)

    orden_items_display = [
        ITEM_PC_NOMBRES[c] for c in ITEMS_PC_TODOS if c in cols_presentes
    ]
    df_counts["Ítem"] = pd.Categorical(
        df_counts["Ítem"], categories=orden_items_display, ordered=True
    )
    df_counts["Respuesta"] = pd.Categorical(
        df_counts["Respuesta"], categories=todas_opciones, ordered=True
    )
    df_counts = df_counts.sort_values(["Ítem", "Respuesta"])

    fig = px.bar(
        df_counts,
        y="Ítem",
        x="Porcentaje",
        color="Respuesta",
        orientation="h",
        title="Distribución de respuestas por ítem de Pensamiento Computacional",
        color_discrete_map=OPCIONES_PC_COLORES,
        text="Porcentaje",
        category_orders={
            "Ítem": orden_items_display,
            "Respuesta": todas_opciones,
        },
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="inside",
        textfont=dict(size=10),
        insidetextanchor="middle",
    )

    fig.update_layout(
        barmode="stack",
        xaxis_title="Porcentaje (%)",
        yaxis_title="Ítem",
        legend_title="Opción",
        template="plotly_white",
        margin=dict(t=100, b=40, l=130, r=40),
        xaxis=dict(range=[0, 100]),
        height=max(480, len(cols_presentes) * 48),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)

    with st.expander("Ver tabla de conteos y porcentajes por ítem"):
        pivot = (
            df_counts.pivot(index="Ítem", columns="Respuesta", values="Frecuencia")
            .fillna(0)
            .astype(int)
        )
        pivot.columns.name = None
        st.dataframe(pivot.reset_index(), hide_index=True)
