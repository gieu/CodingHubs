import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.chart_config import get_chart_config

# ── Columnas de identificación ─────────────────────────────────────────────

COL_SEDE        = "Datos de identificación/Nombre de la sede educativa"
COL_DANE        = "Datos de identificación/Código DANE de la sede educativa"
COL_DOCENTE     = "Datos de identificación/Nombre del docente"
COL_NUM_OBS     = "Número de Observacion"
COL_OBSERVADOR  = "Datos de identificación/Nombre del observador(a)"
COL_FECHA       = "Datos de identificación/Fecha de observación"

# ── Información básica ─────────────────────────────────────────────────────

COL_NINOS = "Información básica/¿Cuántos de los estudiantes son niños?"
COL_NINAS = "Información básica/¿Cuántos de los estudiantes son niñas?"
COL_GRADO = "Información básica/Selecciona los grados que estas observando en el aula."

# ── Organización antes del juego ───────────────────────────────────────────

COL_N_GRUPOS       = "Organización y preparación (Antes de jugar)/¿Cuántos grupos se organizan para usar el juego?"
COL_ESTU_POR_GRUPO = "Organización y preparación (Antes de jugar)/Aproximadamente, ¿cuántos estudiantes hay en cada uno de los grupos?"
COL_ESCENARIO      = "Organización y preparación (Antes de jugar)/Escenario de juego. ¿Cuál es el escenario a jugar?"

# ── Introducción al juego (multi-select binario) ───────────────────────────

COL_INTRO_NARRATIVA_MANUAL   = "Organización y preparación (Antes de jugar)/¿Cómo introdujo el/la docente el juego a los/las estudiantes?/Usó la narrativa del manual del juego"
COL_INTRO_NARRATIVA_ADAPTADA = "Organización y preparación (Antes de jugar)/¿Cómo introdujo el/la docente el juego a los/las estudiantes?/Usó una narrativa adaptada"
COL_INTRO_OBJETIVO           = "Organización y preparación (Antes de jugar)/¿Cómo introdujo el/la docente el juego a los/las estudiantes?/Explicó el objetivo del juego"
COL_INTRO_VOCAB_TECNICO      = "Organización y preparación (Antes de jugar)/¿Cómo introdujo el/la docente el juego a los/las estudiantes?/Usó vocabulario técnico del juego (losetas, biobots, programas, etc.)"
COL_INTRO_OTRO               = "Organización y preparación (Antes de jugar)/¿Cómo introdujo el/la docente el juego a los/las estudiantes?/Otro"

# ── Organización de grupos (single-select → columna texto) ─────────────────

COL_ORG_GRUPOS = "Organización y preparación (Antes de jugar)/ ¿Cómo se organizaron los grupos?"

# ── Materiales y guías del docente (Sí/No) ────────────────────────────────

COL_GUIA_INICIO      = "Organización y preparación (Antes de jugar)/¿El/la docente se apoya en la guía de inicio del juego para orientar la sesión?"
COL_GUIA_PEDAGOGICA  = "Organización y preparación (Antes de jugar)/¿El/la docente se apoya en la guía pedagógica del juego para orientar la sesión?"
COL_LIBRO_ESCENARIOS = "Organización y preparación (Antes de jugar)/¿El/la docente se apoya en el libro de escenarios del juego para orientar la sesión?"
COL_LIBRILLO_MAPAS   = "Organización y preparación (Antes de jugar)/¿El/la docente se apoya en el librillo de mapas del juego para orientar la sesión?"
COL_AFICHE           = "Organización y preparación (Antes de jugar)/¿El/la docente usó el afiche de apoyo visual para orientar la sesión?"
COL_MANUAL_CAP2      = "Organización y preparación (Antes de jugar)/¿El/la docente se apoya en el manual de algoritmos del juego para orientar la sesión? /Capítulo 2"

# ── Descripciones cualitativas (texto libre) ──────────────────────────────

COL_DESCRIBE_GUIA_INICIO       = "Organización y preparación (Antes de jugar)/Describe de qué forma los emplea o si presenta dificultades al apoyarse en los mismos."
COL_DESCRIBE_GUIA_PEDAGOGICA   = "Organización y preparación (Antes de jugar)/Describe de qué forma los emplea o si presenta dificultades al apoyarse en los mismos..1"
COL_DESCRIBE_LIBRO_ESCENARIOS  = "Organización y preparación (Antes de jugar)/Describe de qué forma los emplea o si presenta dificultades al apoyarse en los mismos..2"
COL_DESCRIBE_MANUAL_ALGORITMOS = "Organización y preparación (Antes de jugar)/Describe de qué forma los emplea o si presenta dificultades al apoyarse en los mismos..3"
COL_DESCRIBE_LIBRILLO_MAPAS    = "Organización y preparación (Antes de jugar)/Describe de qué forma los emplea o si presenta dificultades al apoyarse en los mismos..4"
COL_DESCRIBE_AFICHE            = "Organización y preparación (Antes de jugar)/Describe de qué forma los emplea o si presenta dificultades al apoyarse en los mismos..5"

# ── Explicación de reglas (multi-select binario) ───────────────────────────

COL_REGLAS_VERBAL           = "Durante el juego/Explicación de las reglas. ¿Cómo explicó el/la docente las reglas del juego? /Explica las reglas de manera verbal."
COL_REGLAS_TABLERO          = "Durante el juego/Explicación de las reglas. ¿Cómo explicó el/la docente las reglas del juego? /Apoya su explicación escribiendo las reglas en el tablero (ej. algoritmos, errores, etc)."
COL_REGLAS_MATERIALES_JUEGO = "Durante el juego/Explicación de las reglas. ¿Cómo explicó el/la docente las reglas del juego? /Usa materiales del juego para ejemplificar las reglas."

# ── Tipos de dudas (multi-select binario) ─────────────────────────────────

COL_DUDAS_REGLAS     = "Durante el juego/Tipos de dudas observadas en los/las estudiantes/Sobre las reglas del juego"
COL_DUDAS_MATERIALES = "Durante el juego/Tipos de dudas observadas en los/las estudiantes/Sobre el uso de materiales"
COL_DUDAS_SECUENCIA  = "Durante el juego/Tipos de dudas observadas en los/las estudiantes/Sobre la secuencia del juego"
COL_DUDAS_NINGUNA    = "Durante el juego/Tipos de dudas observadas en los/las estudiantes/No hubo dudas significativas"

# ── Vocabulario técnico (multi-select binario) ────────────────────────────

COL_TERM_BIOBOTS       = "Durante el juego/¿Qué términos del juego se mencionaron? /Biobots"
COL_TERM_LOSETAS       = "Durante el juego/¿Qué términos del juego se mencionaron? /Losetas"
COL_TERM_PROGRAMAR     = "Durante el juego/¿Qué términos del juego se mencionaron? /Programar"
COL_TERM_INSTRUCCIONES = "Durante el juego/¿Qué términos del juego se mencionaron? /Instrucciones"
COL_TERM_ALGORITMO     = "Durante el juego/¿Qué términos del juego se mencionaron? /Algoritmo"
COL_TERM_OTRO          = "Durante el juego/¿Qué términos del juego se mencionaron? /Otro"

COL_VOCAB_QUIEN = "Durante el juego/¿Quiénes utilizaron el vocabulario propio del juego?"

# ── Después del juego ──────────────────────────────────────────────────────

COL_TIEMPO_USO    = "Después del juego/Tiempo total en horas clase del juego. ¿Cuánto tiempo pasaron los estudiantes interactuando con el juego?  Tiempo de uso directo con el juego"
COL_PRIMERA_VEZ   = "Después del juego/¿Fue la primera vez que jugaron el escenario?"
COL_VECES_PREVIAS = "Después del juego/En caso de responder no, por favor indique el número de veces previas en que se ha jugado el escenario."
COL_CONEXION_PC   = "Después del juego/¿Se hizo una conexión explícita con habilidades de pensamiento computacional al finalizar el juego?"

# ── Tipo de cierre (multi-select binario) ─────────────────────────────────

COL_CIERRE_REFLEXION = "Después del juego/¿Qué tipo de espacio se usó para esta conexión? /Reflexión grupal guiada por el/la docente"
COL_CIERRE_RETROALIM = "Después del juego/¿Qué tipo de espacio se usó para esta conexión? /Retroalimentación individual"
COL_CIERRE_METACOG   = "Después del juego/¿Qué tipo de espacio se usó para esta conexión? /Espacio de metacognición (preguntas sobre lo que aprendieron o cómo lo resolvieron)"
COL_CIERRE_NINGUNO   = "Después del juego/¿Qué tipo de espacio se usó para esta conexión? /No se realizó ninguna actividad de cierre"

# ── Paleta corporativa ────────────────────────────────────────────────────

AZUL_CLARO  = "#83C9FF"
AZUL_OSCURO = "#0068C9"
MORADO      = "#662482"
ROSA        = "#e5007e"
GRIS        = "#9CA3AF"

GRADO_COLORES = {"Cuarto": AZUL_CLARO, "Quinto": AZUL_OSCURO}
ESCENARIO_COLORES = {"Escenario 2": AZUL_CLARO, "Escenario 3": AZUL_OSCURO, "Otro": GRIS}
CONEXION_PC_COLORES = {"Sí": AZUL_OSCURO, "De forma implícita o superficial": MORADO, "No": GRIS}

# ── Helper: normalizar nombre de sede por código DANE ────────────────────


def _normalizar_sede(df: pd.DataFrame) -> pd.Series:
    """Devuelve una Serie con el nombre de sede más frecuente por código DANE."""
    if COL_DANE not in df.columns or COL_SEDE not in df.columns:
        return df[COL_SEDE]
    nombre_por_dane = (
        df.groupby(COL_DANE)[COL_SEDE]
        .agg(lambda x: x.value_counts().index[0])
    )
    return df[COL_DANE].map(nombre_por_dane)


def _validar_columnas(df: pd.DataFrame, columnas: list[str], nombre_grafico: str) -> bool:
    """Emite st.warning si faltan columnas. Retorna True si todo está OK."""
    faltantes = [c for c in columnas if c not in df.columns]
    if faltantes:
        st.warning(
            f"[{nombre_grafico}] Columnas faltantes: {', '.join(faltantes)}"
        )
        return False
    return True


def _frecuencias_binarias(df: pd.DataFrame, columnas: list[str], etiquetas: dict[str, str]) -> pd.DataFrame:
    """Suma columnas binarias (0/1) y devuelve DataFrame con Frecuencia y Porcentaje."""
    total = len(df)
    rows = []
    for col in columnas:
        if col in df.columns:
            freq = int(pd.to_numeric(df[col], errors="coerce").fillna(0).sum())
            rows.append({
                "Etiqueta": etiquetas.get(col, col),
                "Frecuencia": freq,
                "Porcentaje (%)": round(freq / total * 100, 1) if total > 0 else 0,
            })
    return pd.DataFrame(rows).sort_values("Frecuencia", ascending=True)


# ── Gráfica 1: Mariposa niños/niñas por sede ─────────────────────────────


def grafico_mariposa_ninos_ninas(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Barras horizontales mariposa: niños (izquierda) vs niñas (derecha) por sede educativa."""
    if chart_config is None:
        chart_config = get_chart_config()

    if not _validar_columnas(df, [COL_SEDE, COL_DANE, COL_NINOS, COL_NINAS], "mariposa_ninos_ninas"):
        return

    work = df[[COL_DANE, COL_SEDE, COL_NINOS, COL_NINAS]].copy()
    work["sede_norm"] = _normalizar_sede(work)
    work[COL_NINOS] = pd.to_numeric(work[COL_NINOS], errors="coerce").fillna(0).astype(int)
    work[COL_NINAS] = pd.to_numeric(work[COL_NINAS], errors="coerce").fillna(0).astype(int)

    resumen = (
        work.groupby("sede_norm", as_index=False)
        .agg(Niños=(COL_NINOS, "sum"), Niñas=(COL_NINAS, "sum"))
        .sort_values("Niños")
    )

    if resumen.empty:
        st.warning("No hay datos válidos para la gráfica de distribución por sede.")
        return

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Niños",
        y=resumen["sede_norm"],
        x=-resumen["Niños"],
        orientation="h",
        marker_color=AZUL_CLARO,
        text=resumen["Niños"],
        texttemplate="<b>%{text}</b>",
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="Niñas",
        y=resumen["sede_norm"],
        x=resumen["Niñas"],
        orientation="h",
        marker_color=AZUL_OSCURO,
        text=resumen["Niñas"],
        texttemplate="<b>%{text}</b>",
        textposition="outside",
    ))

    x_max = max(resumen["Niños"].max(), resumen["Niñas"].max()) * 1.3
    # Paso de tick limpio: ~5 divisiones por lado, redondeado al múltiplo de 5 más cercano
    raw_step = x_max / 5
    magnitude = 10 ** (len(str(int(raw_step))) - 1)
    step = max(5, int(round(raw_step / magnitude) * magnitude))
    pos_ticks = list(range(0, int(x_max) + step + 1, step))
    ticks_vals = sorted(set([-v for v in pos_ticks] + pos_ticks))
    ticks_text = [str(abs(v)) for v in ticks_vals]

    fig.update_layout(
        barmode="overlay",
        title="Distribución de estudiantes por sede educativa",
        xaxis=dict(
            title="Número de estudiantes",
            tickvals=ticks_vals,
            ticktext=ticks_text,
            range=[-x_max, x_max],
        ),
        yaxis=dict(title="Sede educativa"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        margin=dict(t=100, b=40, l=200, r=80),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)


# ── Gráfica 2: Distribución por grado ────────────────────────────────────


def grafico_distribucion_grado(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Barras verticales: número de observaciones por grado escolar (Cuarto / Quinto)."""
    if chart_config is None:
        chart_config = get_chart_config()

    if not _validar_columnas(df, [COL_GRADO], "distribucion_grado"):
        return

    conteos = df[COL_GRADO].value_counts().reset_index()
    conteos.columns = ["Grado", "Observaciones"]
    conteos["Color"] = conteos["Grado"].map(GRADO_COLORES).fillna(GRIS)

    if conteos.empty:
        st.warning("No hay datos válidos para la distribución por grado.")
        return

    fig = px.bar(
        conteos,
        x="Grado",
        y="Observaciones",
        color="Grado",
        color_discrete_map=GRADO_COLORES,
        text="Observaciones",
        title="Distribución de observaciones por grado escolar",
    )
    fig.update_traces(texttemplate="<b>%{text}</b>", textposition="outside")
    fig.update_layout(
        xaxis_title="Grado",
        yaxis_title="Número de observaciones",
        yaxis=dict(range=[0, conteos["Observaciones"].max() * 1.2]),
        showlegend=False,
        template="plotly_white",
        margin=dict(t=80, b=40, l=60, r=40),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)


# ── Gráfica 3: Treemap por sede ───────────────────────────────────────────


def grafico_treemap_sedes(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Treemap: número de observaciones por sede educativa (normalizada por DANE)."""
    if chart_config is None:
        chart_config = get_chart_config()

    if not _validar_columnas(df, [COL_SEDE, COL_DANE], "treemap_sedes"):
        return

    work = df[[COL_DANE, COL_SEDE]].copy()
    work["sede_norm"] = _normalizar_sede(work)

    conteos = work["sede_norm"].value_counts().reset_index()
    conteos.columns = ["Sede", "Observaciones"]

    if conteos.empty:
        st.warning("No hay datos válidos para el treemap de sedes.")
        return

    fig = px.treemap(
        conteos,
        path=["Sede"],
        values="Observaciones",
        color="Observaciones",
        color_continuous_scale=[[0, AZUL_CLARO], [1, AZUL_OSCURO]],
        title="Distribución de observaciones por sede educativa",
    )
    fig.update_traces(texttemplate="<b>%{label}</b><br>%{value} obs.", textfont_size=13)
    fig.update_layout(
        margin=dict(t=80, b=20, l=20, r=20),
        coloraxis_colorbar=dict(title="Observaciones"),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)


# ── Gráfica 4: Distribución por escenario ────────────────────────────────


def grafico_distribucion_escenario(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Barras verticales: número de observaciones por escenario jugado."""
    if chart_config is None:
        chart_config = get_chart_config()

    if not _validar_columnas(df, [COL_ESCENARIO], "distribucion_escenario"):
        return

    conteos = df[COL_ESCENARIO].str.strip().value_counts().reset_index()
    conteos.columns = ["Escenario", "Observaciones"]

    if conteos.empty:
        st.warning("No hay datos válidos para la distribución por escenario.")
        return

    fig = px.bar(
        conteos,
        x="Escenario",
        y="Observaciones",
        color="Escenario",
        color_discrete_map=ESCENARIO_COLORES,
        text="Observaciones",
        title="Distribución de observaciones por escenario jugado",
    )
    fig.update_traces(texttemplate="<b>%{text}</b>", textposition="outside")
    fig.update_layout(
        xaxis_title="Escenario",
        yaxis_title="Número de observaciones",
        yaxis=dict(range=[0, conteos["Observaciones"].max() * 1.2]),
        showlegend=False,
        template="plotly_white",
        margin=dict(t=80, b=40, l=60, r=40),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)


# ── Gráfica 5: Métodos de introducción al juego ───────────────────────────


def grafico_introduccion_juego(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Barras horizontales de frecuencia: métodos usados para introducir el juego (multi-select)."""
    if chart_config is None:
        chart_config = get_chart_config()

    cols = [COL_INTRO_OBJETIVO, COL_INTRO_VOCAB_TECNICO, COL_INTRO_NARRATIVA_MANUAL,
            COL_INTRO_NARRATIVA_ADAPTADA, COL_INTRO_OTRO]
    etiquetas = {
        COL_INTRO_OBJETIVO:           "Explicó el objetivo del juego",
        COL_INTRO_VOCAB_TECNICO:      "Usó vocabulario técnico",
        COL_INTRO_NARRATIVA_MANUAL:   "Usó narrativa del manual",
        COL_INTRO_NARRATIVA_ADAPTADA: "Usó narrativa adaptada",
        COL_INTRO_OTRO:               "Otro",
    }

    cols_presentes = [c for c in cols if c in df.columns]
    if not cols_presentes:
        st.warning("No se encontraron columnas de introducción al juego.")
        return

    data = _frecuencias_binarias(df, cols_presentes, etiquetas)

    fig = px.bar(
        data,
        y="Etiqueta",
        x="Frecuencia",
        orientation="h",
        text="Frecuencia",
        title="Métodos usados para introducir el juego",
        color_discrete_sequence=[AZUL_OSCURO],
    )
    fig.update_traces(texttemplate="<b>%{text}</b> (%{customdata[0]}%)", textposition="outside",
                      customdata=data[["Porcentaje (%)"]].values)
    fig.update_layout(
        xaxis_title="Número de observaciones",
        yaxis_title="",
        xaxis=dict(range=[0, len(df) * 1.25]),
        template="plotly_white",
        margin=dict(t=80, b=40, l=220, r=80),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)


# ── Gráfica 6: Organización de grupos ────────────────────────────────────


def grafico_organizacion_grupos(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Barras horizontales: cómo se organizaron los grupos (selección única)."""
    if chart_config is None:
        chart_config = get_chart_config()

    if not _validar_columnas(df, [COL_ORG_GRUPOS], "organizacion_grupos"):
        return

    conteos = df[COL_ORG_GRUPOS].str.strip().value_counts().reset_index()
    conteos.columns = ["Forma de organización", "Observaciones"]

    if conteos.empty:
        st.warning("No hay datos válidos para la organización de grupos.")
        return

    colores = [AZUL_CLARO, AZUL_OSCURO, MORADO, ROSA, GRIS]
    fig = px.bar(
        conteos,
        y="Forma de organización",
        x="Observaciones",
        orientation="h",
        text="Observaciones",
        color="Forma de organización",
        color_discrete_sequence=colores,
        title="¿Cómo se organizaron los grupos?",
    )
    fig.update_traces(texttemplate="<b>%{text}</b>", textposition="outside")
    fig.update_layout(
        xaxis_title="Número de observaciones",
        yaxis_title="",
        xaxis=dict(range=[0, conteos["Observaciones"].max() * 1.3]),
        showlegend=False,
        template="plotly_white",
        margin=dict(t=80, b=40, l=220, r=80),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)


# ── Gráfica 7: Materiales y guías del docente ────────────────────────────


def grafico_materiales_docente(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Barras horizontales: uso de materiales/guías del kit (columnas Sí/No o binarias)."""
    if chart_config is None:
        chart_config = get_chart_config()

    materiales = {
        COL_GUIA_INICIO:      "Guía de inicio",
        COL_GUIA_PEDAGOGICA:  "Guía pedagógica",
        COL_LIBRO_ESCENARIOS: "Libro de escenarios",
        COL_LIBRILLO_MAPAS:   "Librillo de mapas",
        COL_MANUAL_CAP2:      "Manual de algoritmos (Cap. 2)",
        COL_AFICHE:           "Afiche de apoyo visual",
    }

    rows = []
    total = len(df)
    for col, etiqueta in materiales.items():
        if col not in df.columns:
            continue
        serie = df[col]
        if serie.dtype == object:
            freq = int((serie.str.strip().str.lower() == "sí").sum())
        else:
            freq = int(pd.to_numeric(serie, errors="coerce").fillna(0).sum())
        rows.append({
            "Material": etiqueta,
            "Usaron (Sí)": freq,
            "No usaron": total - freq,
            "Porcentaje (%)": round(freq / total * 100, 1) if total > 0 else 0,
        })

    if not rows:
        st.warning("No se encontraron columnas de materiales y guías.")
        return

    data = pd.DataFrame(rows).sort_values("Usaron (Sí)", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Sí usaron",
        y=data["Material"],
        x=data["Usaron (Sí)"],
        orientation="h",
        marker_color=AZUL_OSCURO,
        text=[f"<b>{v}</b> ({p}%)" for v, p in zip(data["Usaron (Sí)"], data["Porcentaje (%)"])],
        textposition="inside",
        insidetextanchor="middle",
        hovertemplate="%{y}<br>Sí usaron: %{x}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="No usaron",
        y=data["Material"],
        x=data["No usaron"],
        orientation="h",
        marker_color=GRIS,
        text=[f"<b>{v}</b> ({round(v / total * 100, 1)}%)" for v in data["No usaron"]],
        textposition="inside",
        insidetextanchor="middle",
        hovertemplate="%{y}<br>No usaron: %{x}<extra></extra>",
    ))
    fig.update_layout(
        barmode="stack",
        title="Uso de materiales y guías del kit por el docente",
        xaxis_title="Número de observaciones",
        yaxis_title="",
        xaxis=dict(range=[0, total * 1.05]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        margin=dict(t=100, b=40, l=220, r=40),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)


# ── Gráfica 8: Métodos de explicación de reglas ───────────────────────────


def grafico_explicacion_reglas(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Barras horizontales de frecuencia: métodos usados para explicar las reglas (multi-select)."""
    if chart_config is None:
        chart_config = get_chart_config()

    cols = [COL_REGLAS_VERBAL, COL_REGLAS_MATERIALES_JUEGO, COL_REGLAS_TABLERO]
    etiquetas = {
        COL_REGLAS_VERBAL:           "Explica las reglas de manera verbal",
        COL_REGLAS_MATERIALES_JUEGO: "Usa materiales del juego para ejemplificar",
        COL_REGLAS_TABLERO:          "Escribe las reglas en el tablero",
    }

    cols_presentes = [c for c in cols if c in df.columns]
    if not cols_presentes:
        st.warning("No se encontraron columnas de explicación de reglas.")
        return

    data = _frecuencias_binarias(df, cols_presentes, etiquetas)

    fig = px.bar(
        data,
        y="Etiqueta",
        x="Frecuencia",
        orientation="h",
        text="Frecuencia",
        title="Métodos usados para explicar las reglas del juego",
        color_discrete_sequence=[AZUL_OSCURO],
    )
    fig.update_traces(texttemplate="<b>%{text}</b> (%{customdata[0]}%)", textposition="outside",
                      customdata=data[["Porcentaje (%)"]].values)
    fig.update_layout(
        xaxis_title="Número de observaciones",
        yaxis_title="",
        xaxis=dict(range=[0, len(df) * 1.25]),
        template="plotly_white",
        margin=dict(t=80, b=40, l=260, r=80),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)


# ── Gráfica 9: Tipos de dudas de los estudiantes ─────────────────────────


def grafico_dudas_estudiantes(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Barras horizontales de frecuencia: tipos de dudas observadas (multi-select)."""
    if chart_config is None:
        chart_config = get_chart_config()

    cols = [COL_DUDAS_REGLAS, COL_DUDAS_MATERIALES, COL_DUDAS_SECUENCIA, COL_DUDAS_NINGUNA]
    etiquetas = {
        COL_DUDAS_REGLAS:     "Sobre las reglas del juego",
        COL_DUDAS_MATERIALES: "Sobre el uso de materiales",
        COL_DUDAS_SECUENCIA:  "Sobre la secuencia del juego",
        COL_DUDAS_NINGUNA:    "No hubo dudas significativas",
    }

    cols_presentes = [c for c in cols if c in df.columns]
    if not cols_presentes:
        st.warning("No se encontraron columnas de tipos de dudas.")
        return

    data = _frecuencias_binarias(df, cols_presentes, etiquetas)

    fig = px.bar(
        data,
        y="Etiqueta",
        x="Frecuencia",
        orientation="h",
        text="Frecuencia",
        title="Tipos de dudas observadas en los estudiantes",
        color_discrete_sequence=[MORADO],
    )
    fig.update_traces(texttemplate="<b>%{text}</b> (%{customdata[0]}%)", textposition="outside",
                      customdata=data[["Porcentaje (%)"]].values)
    fig.update_layout(
        xaxis_title="Número de observaciones",
        yaxis_title="",
        xaxis=dict(range=[0, len(df) * 1.25]),
        template="plotly_white",
        margin=dict(t=80, b=40, l=240, r=80),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)


# ── Gráfica 10: Vocabulario técnico mencionado ────────────────────────────


def grafico_vocabulario_terminos(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Barras horizontales de frecuencia: términos técnicos mencionados (multi-select)."""
    if chart_config is None:
        chart_config = get_chart_config()

    cols = [COL_TERM_BIOBOTS, COL_TERM_LOSETAS, COL_TERM_INSTRUCCIONES,
            COL_TERM_ALGORITMO, COL_TERM_PROGRAMAR, COL_TERM_OTRO]
    etiquetas = {
        COL_TERM_BIOBOTS:       "Biobots",
        COL_TERM_LOSETAS:       "Losetas",
        COL_TERM_INSTRUCCIONES: "Instrucciones",
        COL_TERM_ALGORITMO:     "Algoritmo",
        COL_TERM_PROGRAMAR:     "Programar",
        COL_TERM_OTRO:          "Otro",
    }

    cols_presentes = [c for c in cols if c in df.columns]
    if not cols_presentes:
        st.warning("No se encontraron columnas de vocabulario técnico.")
        return

    data = _frecuencias_binarias(df, cols_presentes, etiquetas)

    fig = px.bar(
        data,
        y="Etiqueta",
        x="Frecuencia",
        orientation="h",
        text="Frecuencia",
        title="Términos técnicos del juego mencionados durante la sesión",
        color_discrete_sequence=[AZUL_OSCURO],
    )
    fig.update_traces(texttemplate="<b>%{text}</b> (%{customdata[0]}%)", textposition="outside",
                      customdata=data[["Porcentaje (%)"]].values)
    fig.update_layout(
        xaxis_title="Número de observaciones",
        yaxis_title="",
        xaxis=dict(range=[0, len(df) * 1.25]),
        template="plotly_white",
        margin=dict(t=80, b=40, l=160, r=80),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)


# ── Gráfica 11: Tiempo de uso con el juego ───────────────────────────────


def grafico_tiempo_uso(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Barras verticales: distribución del tiempo de uso directo con el juego."""
    if chart_config is None:
        chart_config = get_chart_config()

    if not _validar_columnas(df, [COL_TIEMPO_USO], "tiempo_uso"):
        return

    work = df[[COL_TIEMPO_USO]].copy()
    work[COL_TIEMPO_USO] = pd.to_numeric(work[COL_TIEMPO_USO], errors="coerce").abs()
    work = work.dropna(subset=[COL_TIEMPO_USO])
    work[COL_TIEMPO_USO] = work[COL_TIEMPO_USO].astype(int)

    if work.empty:
        st.warning("No hay datos válidos para la distribución de tiempo de uso.")
        return

    conteos = work[COL_TIEMPO_USO].value_counts().reset_index()
    conteos.columns = ["Horas de clase", "Observaciones"]
    conteos = conteos.sort_values("Horas de clase")

    colores_tiempo = {1: AZUL_CLARO, 2: AZUL_OSCURO}
    conteos["Color"] = conteos["Horas de clase"].map(colores_tiempo).fillna(GRIS)

    fig = px.bar(
        conteos,
        x="Horas de clase",
        y="Observaciones",
        text="Observaciones",
        color="Horas de clase",
        color_discrete_map=colores_tiempo,
        title="Tiempo de uso directo con el juego",
    )
    fig.update_traces(texttemplate="<b>%{text}</b>", textposition="outside")
    fig.update_layout(
        xaxis=dict(title="Horas de clase", tickmode="array", tickvals=conteos["Horas de clase"].tolist()),
        yaxis=dict(title="Número de observaciones", range=[0, conteos["Observaciones"].max() * 1.25]),
        showlegend=False,
        template="plotly_white",
        margin=dict(t=80, b=40, l=60, r=40),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)


# ── Gráfica 12: Primera vez jugando el escenario ─────────────────────────


def grafico_primera_vez(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Barras horizontales: si fue la primera vez que se jugó el escenario."""
    if chart_config is None:
        chart_config = get_chart_config()

    if not _validar_columnas(df, [COL_PRIMERA_VEZ], "primera_vez"):
        return

    conteos = df[COL_PRIMERA_VEZ].str.strip().value_counts().reset_index()
    conteos.columns = ["Primera vez", "Observaciones"]

    if conteos.empty:
        st.warning("No hay datos válidos para la gráfica de primera vez.")
        return

    orden = ["Sí", "No"]
    colores_pv = {"Sí": AZUL_CLARO, "No": AZUL_OSCURO}

    fig = px.bar(
        conteos,
        y="Primera vez",
        x="Observaciones",
        orientation="h",
        text="Observaciones",
        color="Primera vez",
        color_discrete_map=colores_pv,
        category_orders={"Primera vez": orden},
        title="¿Fue la primera vez que jugaron el escenario?",
    )
    fig.update_traces(texttemplate="<b>%{text}</b>", textposition="outside")
    fig.update_layout(
        xaxis_title="Número de observaciones",
        yaxis_title="",
        xaxis=dict(range=[0, conteos["Observaciones"].max() * 1.3]),
        showlegend=False,
        template="plotly_white",
        margin=dict(t=80, b=40, l=120, r=80),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)


# ── Gráfica 13: Conexión con pensamiento computacional ───────────────────


def grafico_conexion_pc(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Barras horizontales: tipo de conexión explícita con pensamiento computacional al finalizar."""
    if chart_config is None:
        chart_config = get_chart_config()

    if not _validar_columnas(df, [COL_CONEXION_PC], "conexion_pc"):
        return

    conteos = df[COL_CONEXION_PC].str.strip().value_counts().reset_index()
    conteos.columns = ["Tipo de conexión", "Observaciones"]

    if conteos.empty:
        st.warning("No hay datos válidos para la conexión con pensamiento computacional.")
        return

    fig = px.bar(
        conteos,
        y="Tipo de conexión",
        x="Observaciones",
        orientation="h",
        text="Observaciones",
        color="Tipo de conexión",
        color_discrete_map=CONEXION_PC_COLORES,
        title="Conexión con pensamiento computacional al finalizar la sesión",
    )
    fig.update_traces(texttemplate="<b>%{text}</b>", textposition="outside")
    fig.update_layout(
        xaxis_title="Número de observaciones",
        yaxis_title="",
        xaxis=dict(range=[0, conteos["Observaciones"].max() * 1.4]),
        showlegend=False,
        template="plotly_white",
        margin=dict(t=80, b=40, l=280, r=80),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)


# ── Gráfica 14: Tipo de espacio de cierre ────────────────────────────────


def grafico_cierre_actividad(df: pd.DataFrame, chart_config: dict | None = None) -> None:
    """Barras horizontales de frecuencia: tipo de espacio usado para el cierre (multi-select)."""
    if chart_config is None:
        chart_config = get_chart_config()

    cols = [COL_CIERRE_REFLEXION, COL_CIERRE_NINGUNO, COL_CIERRE_RETROALIM, COL_CIERRE_METACOG]
    etiquetas = {
        COL_CIERRE_REFLEXION: "Reflexión grupal guiada por el/la docente",
        COL_CIERRE_NINGUNO:   "No se realizó ninguna actividad de cierre",
        COL_CIERRE_RETROALIM: "Retroalimentación individual",
        COL_CIERRE_METACOG:   "Espacio de metacognición",
    }

    cols_presentes = [c for c in cols if c in df.columns]
    if not cols_presentes:
        st.warning("No se encontraron columnas del tipo de cierre.")
        return

    data = _frecuencias_binarias(df, cols_presentes, etiquetas)

    fig = px.bar(
        data,
        y="Etiqueta",
        x="Frecuencia",
        orientation="h",
        text="Frecuencia",
        title="Tipo de espacio usado para el cierre / conexión con PC",
        color_discrete_sequence=[AZUL_OSCURO],
    )
    fig.update_traces(texttemplate="<b>%{text}</b> (%{customdata[0]}%)", textposition="outside",
                      customdata=data[["Porcentaje (%)"]].values)
    fig.update_layout(
        xaxis_title="Número de observaciones",
        yaxis_title="",
        xaxis=dict(range=[0, len(df) * 1.3]),
        template="plotly_white",
        margin=dict(t=80, b=40, l=300, r=80),
    )

    st.plotly_chart(fig, width="stretch", config=chart_config)
