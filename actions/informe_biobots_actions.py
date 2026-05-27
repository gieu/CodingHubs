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

# ── Columnas de puntaje y aciertos ────────────────────────────────────────

COL_PUNTAJE_PC    = "puntaje_PC"
COL_ACIERTOS_PC   = "aciertos_PC"
COL_ACIERTOS_EGMA = "aciertos_P_EGMA"

CIUDAD_COLORES = {"Bucaramanga": "#83C9FF", "Manizales": "#0068C9"}

SEXO_COLORES = {
    SEXO_NINO: "#83C9FF",
    SEXO_NINA: "#0068C9",
    SEXO_PREFIERO: "#9CA3AF",
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


# ── Gráfica 7: Boxplot puntaje PC por ciudad y sexo ──────────────────────

def grafico_boxplot_puntaje_pc(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Boxplot de puntaje_PC (0–50) agrupado por Ciudad, con color por Sexo."""
    if chart_config is None:
        chart_config = get_chart_config()

    columnas_requeridas = [COL_PUNTAJE_PC, COL_CIUDAD, COL_SEXO]
    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        st.warning(
            f"No se encontraron las columnas necesarias: {', '.join(faltantes)}. "
            f"Columnas disponibles: {', '.join(df.columns)}"
        )
        return

    work = df[[COL_CIUDAD, COL_SEXO, COL_PUNTAJE_PC]].copy()
    work[COL_CIUDAD] = work[COL_CIUDAD].map(_normalizar_ciudad)
    work[COL_SEXO] = work[COL_SEXO].map(_normalizar_sexo)
    work[COL_PUNTAJE_PC] = pd.to_numeric(work[COL_PUNTAJE_PC], errors="coerce")
    work = work.dropna(subset=[COL_CIUDAD, COL_SEXO, COL_PUNTAJE_PC])
    work = work[work[COL_CIUDAD].isin(CIUDADES_ORDEN)]
    work = work[work[COL_SEXO].isin(SEXO_CATEGORIAS)]

    if work.empty:
        st.warning("No hay registros válidos para graficar el puntaje de PC.")
        return

    work[COL_SEXO] = pd.Categorical(work[COL_SEXO], categories=SEXO_CATEGORIAS, ordered=True)
    work[COL_CIUDAD] = pd.Categorical(work[COL_CIUDAD], categories=CIUDADES_ORDEN, ordered=True)

    fig = px.box(
        work,
        x=COL_CIUDAD,
        y=COL_PUNTAJE_PC,
        color=COL_SEXO,
        points="outliers",
        title="Distribución del puntaje de Pensamiento Computacional por ciudad y sexo",
        color_discrete_map=SEXO_COLORES,
        category_orders={COL_CIUDAD: CIUDADES_ORDEN, COL_SEXO: SEXO_CATEGORIAS},
        labels={COL_CIUDAD: "Ciudad", COL_PUNTAJE_PC: "Puntaje PC", COL_SEXO: "Sexo"},
    )

    fig.update_layout(
        yaxis=dict(range=[0, 55], title="Puntaje PC"),
        xaxis_title="Ciudad",
        legend_title="Sexo",
        template="plotly_white",
        margin=dict(t=100, b=40, l=60, r=40),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)

    with st.expander("Ver estadísticos por ciudad y sexo"):
        stats = (
            work.groupby([COL_CIUDAD, COL_SEXO], observed=True)[COL_PUNTAJE_PC]
            .agg(["count", "mean", "median", "min", "max", "std"])
            .round(2)
            .reset_index()
        )
        stats.columns = ["Ciudad", "Sexo", "N", "Media", "Mediana", "Mín", "Máx", "Desv. Est."]
        st.dataframe(stats, hide_index=True)


# ── Gráfica 8: Histograma puntaje PC por ciudad ───────────────────────────

def grafico_histograma_puntaje_pc(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Histograma de puntaje_PC (0–50) con distribución por ciudad."""
    if chart_config is None:
        chart_config = get_chart_config()

    columnas_requeridas = [COL_PUNTAJE_PC, COL_CIUDAD]
    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        st.warning(
            f"No se encontraron las columnas necesarias: {', '.join(faltantes)}. "
            f"Columnas disponibles: {', '.join(df.columns)}"
        )
        return

    work = df[[COL_CIUDAD, COL_PUNTAJE_PC]].copy()
    work[COL_CIUDAD] = work[COL_CIUDAD].map(_normalizar_ciudad)
    work[COL_PUNTAJE_PC] = pd.to_numeric(work[COL_PUNTAJE_PC], errors="coerce")
    work = work.dropna(subset=[COL_CIUDAD, COL_PUNTAJE_PC])
    work = work[work[COL_CIUDAD].isin(CIUDADES_ORDEN)]

    if work.empty:
        st.warning("No hay registros válidos para el histograma de puntaje PC.")
        return

    fig = px.histogram(
        work,
        x=COL_PUNTAJE_PC,
        color=COL_CIUDAD,
        barmode="overlay",
        nbins=15,
        opacity=0.75,
        title="Distribución del puntaje de Pensamiento Computacional",
        color_discrete_map=CIUDAD_COLORES,
        category_orders={COL_CIUDAD: CIUDADES_ORDEN},
        labels={COL_PUNTAJE_PC: "Puntaje PC", COL_CIUDAD: "Ciudad"},
    )

    for ciudad in CIUDADES_ORDEN:
        subset = work[work[COL_CIUDAD] == ciudad][COL_PUNTAJE_PC]
        if subset.empty:
            continue
        media = subset.mean()
        fig.add_vline(
            x=media,
            line_dash="dash",
            line_color=CIUDAD_COLORES.get(ciudad, "#333333"),
            annotation_text=f"{ciudad}: {media:.1f}",
            annotation_position="top right",
            annotation_font_size=12,
        )

    fig.update_layout(
        xaxis=dict(range=[0, 55], title="Puntaje PC"),
        yaxis_title="Número de estudiantes",
        legend_title="Ciudad",
        template="plotly_white",
        margin=dict(t=100, b=40, l=60, r=40),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)

    with st.expander("Ver estadísticos por ciudad"):
        stats = (
            work.groupby(COL_CIUDAD)[COL_PUNTAJE_PC]
            .agg(["count", "mean", "median", "min", "max", "std"])
            .round(2)
            .reset_index()
        )
        stats.columns = ["Ciudad", "N", "Media", "Mediana", "Mín", "Máx", "Desv. Est."]
        st.dataframe(stats, hide_index=True)


# ── Gráfica 9: Distribución de aciertos PC ───────────────────────────────

def grafico_distribucion_aciertos_pc(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Barras de frecuencia de aciertos_PC (proporción de ítems correctos) por ciudad."""
    if chart_config is None:
        chart_config = get_chart_config()

    columnas_requeridas = [COL_ACIERTOS_PC, COL_CIUDAD]
    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        st.warning(
            f"No se encontraron las columnas necesarias: {', '.join(faltantes)}. "
            f"Columnas disponibles: {', '.join(df.columns)}"
        )
        return

    work = df[[COL_CIUDAD, COL_ACIERTOS_PC]].copy()
    work[COL_CIUDAD] = work[COL_CIUDAD].map(_normalizar_ciudad)
    work[COL_ACIERTOS_PC] = pd.to_numeric(work[COL_ACIERTOS_PC], errors="coerce")
    work = work.dropna(subset=[COL_CIUDAD, COL_ACIERTOS_PC])
    work = work[work[COL_CIUDAD].isin(CIUDADES_ORDEN)]

    if work.empty:
        st.warning("No hay registros válidos para la distribución de aciertos PC.")
        return

    bins   = [0, 20, 40, 60, 80, 100]
    labels_rango = ["0–20%", "21–40%", "41–60%", "61–80%", "81–100%"]
    work["Rango aciertos"] = pd.cut(
        work[COL_ACIERTOS_PC] * 100,
        bins=bins,
        labels=labels_rango,
        include_lowest=True,
    )

    df_counts = (
        work.groupby([COL_CIUDAD, "Rango aciertos"], as_index=False, observed=True)
        .size()
        .rename(columns={"size": "Estudiantes"})
    )

    fig = px.bar(
        df_counts,
        x="Rango aciertos",
        y="Estudiantes",
        color=COL_CIUDAD,
        barmode="group",
        title="Distribución de aciertos en Pensamiento Computacional",
        color_discrete_map=CIUDAD_COLORES,
        text="Estudiantes",
        category_orders={COL_CIUDAD: CIUDADES_ORDEN, "Rango aciertos": labels_rango},
        labels={
            "Rango aciertos": "Rango de aciertos",
            "Estudiantes": "Número de estudiantes",
            COL_CIUDAD: "Ciudad",
        },
    )

    for trace in fig.data:
        trace.texttemplate = "<b>%{text}</b>"
        trace.textposition = "outside"
        trace.textfont = dict(size=12)

    y_max = df_counts["Estudiantes"].max() * 1.15
    fig.update_layout(
        xaxis_title="Rango de aciertos",
        yaxis=dict(title="Número de estudiantes", range=[0, y_max]),
        legend_title="Ciudad",
        template="plotly_white",
        margin=dict(t=100, b=40, l=60, r=40),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)

    with st.expander("Ver tabla de conteos por ciudad y rango de aciertos"):
        pivot = (
            df_counts.pivot(index="Rango aciertos", columns=COL_CIUDAD, values="Estudiantes")
            .fillna(0)
            .astype(int)
            .reset_index()
        )
        pivot.columns.name = None
        st.dataframe(pivot, hide_index=True)


# ── Gráfica 10: Distribución de aciertos EGMA ────────────────────────────

def grafico_distribucion_aciertos_egma(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Barras de frecuencia de aciertos_P_EGMA (proporción) por ciudad."""
    if chart_config is None:
        chart_config = get_chart_config()

    columnas_requeridas = [COL_ACIERTOS_EGMA, COL_CIUDAD]
    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        st.warning(
            f"No se encontraron las columnas necesarias: {', '.join(faltantes)}. "
            f"Columnas disponibles: {', '.join(df.columns)}"
        )
        return

    work = df[[COL_CIUDAD, COL_ACIERTOS_EGMA]].copy()
    work[COL_CIUDAD] = work[COL_CIUDAD].map(_normalizar_ciudad)
    work[COL_ACIERTOS_EGMA] = pd.to_numeric(work[COL_ACIERTOS_EGMA], errors="coerce")
    work = work.dropna(subset=[COL_CIUDAD, COL_ACIERTOS_EGMA])
    work = work[work[COL_CIUDAD].isin(CIUDADES_ORDEN)]

    if work.empty:
        st.warning("No hay registros válidos para la distribución de aciertos EGMA.")
        return

    work["Aciertos (%)"] = (work[COL_ACIERTOS_EGMA] * 100).round(0).astype(int)

    df_counts = (
        work.groupby([COL_CIUDAD, "Aciertos (%)"], as_index=False)
        .size()
        .rename(columns={"size": "Estudiantes"})
    )

    orden_x = sorted(df_counts["Aciertos (%)"].unique().tolist())

    fig = px.bar(
        df_counts,
        x="Aciertos (%)",
        y="Estudiantes",
        color=COL_CIUDAD,
        barmode="group",
        title="Distribución de aciertos EGMA",
        color_discrete_map=CIUDAD_COLORES,
        text="Estudiantes",
        category_orders={COL_CIUDAD: CIUDADES_ORDEN, "Aciertos (%)": orden_x},
        labels={
            "Aciertos (%)": "Porcentaje de aciertos EGMA (%)",
            "Estudiantes": "Número de estudiantes",
            COL_CIUDAD: "Ciudad",
        },
    )

    for trace in fig.data:
        trace.texttemplate = "<b>%{text}</b>"
        trace.textposition = "outside"
        trace.textfont = dict(size=12)

    y_max = df_counts["Estudiantes"].max() * 1.15
    fig.update_layout(
        xaxis=dict(title="Porcentaje de aciertos EGMA (%)", ticksuffix="%"),
        yaxis=dict(title="Número de estudiantes", range=[0, y_max]),
        legend_title="Ciudad",
        template="plotly_white",
        margin=dict(t=100, b=40, l=60, r=40),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)

    with st.expander("Ver tabla de conteos por ciudad y nivel de aciertos EGMA"):
        pivot = (
            df_counts.pivot(index="Aciertos (%)", columns=COL_CIUDAD, values="Estudiantes")
            .fillna(0)
            .astype(int)
            .reset_index()
        )
        pivot.columns.name = None
        st.dataframe(pivot, hide_index=True)


# ── Gráfica 11: Correlación puntaje PC vs aciertos EGMA ──────────────────

def grafico_correlacion_pc_egma(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Scatter plot: puntaje_PC (0–50) vs aciertos_P_EGMA (%) con línea de tendencia por ciudad."""
    if chart_config is None:
        chart_config = get_chart_config()

    columnas_requeridas = [COL_PUNTAJE_PC, COL_ACIERTOS_EGMA, COL_CIUDAD]
    faltantes = [c for c in columnas_requeridas if c not in df.columns]
    if faltantes:
        st.warning(
            f"No se encontraron las columnas necesarias: {', '.join(faltantes)}. "
            f"Columnas disponibles: {', '.join(df.columns)}"
        )
        return

    work = df[[COL_CIUDAD, COL_PUNTAJE_PC, COL_ACIERTOS_EGMA]].copy()
    work[COL_CIUDAD] = work[COL_CIUDAD].map(_normalizar_ciudad)
    work[COL_PUNTAJE_PC] = pd.to_numeric(work[COL_PUNTAJE_PC], errors="coerce")
    work[COL_ACIERTOS_EGMA] = pd.to_numeric(work[COL_ACIERTOS_EGMA], errors="coerce")
    work = work.dropna(subset=[COL_CIUDAD, COL_PUNTAJE_PC, COL_ACIERTOS_EGMA])
    work = work[work[COL_CIUDAD].isin(CIUDADES_ORDEN)]

    if work.empty:
        st.warning("No hay registros válidos para la correlación PC vs EGMA.")
        return

    work["Aciertos EGMA (%)"] = (work[COL_ACIERTOS_EGMA] * 100).round(0).astype(int)

    fig = px.scatter(
        work,
        x="Aciertos EGMA (%)",
        y=COL_PUNTAJE_PC,
        color=COL_CIUDAD,
        trendline="ols",
        title="Relación entre aciertos EGMA y puntaje de Pensamiento Computacional",
        color_discrete_map=CIUDAD_COLORES,
        category_orders={COL_CIUDAD: CIUDADES_ORDEN},
        labels={
            "Aciertos EGMA (%)": "Aciertos EGMA (%)",
            COL_PUNTAJE_PC: "Puntaje PC",
            COL_CIUDAD: "Ciudad",
        },
        opacity=0.65,
    )

    fig.update_layout(
        xaxis=dict(range=[-5, 105], title="Aciertos EGMA (%)"),
        yaxis=dict(range=[0, 55], title="Puntaje PC"),
        legend_title="Ciudad",
        template="plotly_white",
        margin=dict(t=100, b=40, l=60, r=40),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)

    with st.expander("Ver correlación de Pearson por ciudad"):
        filas = []
        for ciudad in CIUDADES_ORDEN:
            subset = work[work[COL_CIUDAD] == ciudad]
            if len(subset) < 2:
                continue
            r = subset[COL_PUNTAJE_PC].corr(subset["Aciertos EGMA (%)"])
            filas.append({"Ciudad": ciudad, "N": len(subset), "Pearson r": round(r, 4)})
        if filas:
            st.dataframe(pd.DataFrame(filas), hide_index=True)
        else:
            st.info("No hay suficientes datos para calcular la correlación.")
