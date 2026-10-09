"""Gráficas de observaciones 2026, calculadas sobre las respuestas disponibles."""

import re
import textwrap
import unicodedata
from uuid import uuid4

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.colors import qualitative, sequential

from utils.chart_config import get_chart_config


chart_config = {**get_chart_config(), "editable": False, "displaylogo": False}
MOMENT_COLORS = {"Pretest": "#636EFA", "Postest": "#EF553B"}
PRACTICE_COLORS = {"Pretest": "cornflowerblue", "Postest": "orchid"}
INSTANT = "Número de instantánea"


def _normalized(value):
    if pd.isna(value):
        return ""
    text = unicodedata.normalize("NFKD", str(value).strip().lower())
    return "".join(c for c in text if not unicodedata.combining(c))


def _response(value, checklist=False):
    """No confundir 0 con una casilla marcada ni un vacío con una respuesta No."""
    text = _normalized(value)
    if not text or text in {"nan", "none", "<na>"}:
        return False if checklist else pd.NA
    if text in {"1", "1.0", "true", "si", "yes"} or re.match(r"^si\b", text):
        return True
    if text in {"0", "0.0", "false", "no"}:
        return False
    if text.startswith(("no aplica", "no se puede", "no fue posible")):
        return False if checklist else pd.NA
    if not checklist and re.match(r"^(no|parcialmente)\b", text):
        return False
    return True if checklist else pd.NA


def _flag(df, column, checklist=False):
    if column not in df:
        return pd.Series(pd.NA, index=df.index, dtype="boolean")
    return df[column].map(lambda value: _response(value, checklist)).astype("boolean")


def _prepare(source):
    df = source.copy().reset_index(drop=True)
    df.columns = [str(column).strip() for column in df.columns]
    if "momento" not in df:
        df["momento"] = "Período disponible"
    else:
        df["momento"] = df["momento"].map(
            lambda value: {"pre": "Pretest", "pretest": "Pretest", "post": "Postest", "postest": "Postest"}.get(
                _normalized(value), str(value).strip() if pd.notna(value) else "Sin momento"
            )
        )
    return df


def _moments(df):
    values = df["momento"].drop_duplicates().tolist()
    return [m for m in ["Pretest", "Postest"] if m in values] + [
        m for m in values if m not in {"Pretest", "Postest"}
    ]


def _wrap(text, width=40):
    return "<br>".join(textwrap.wrap(str(text), width=width))


def _show(fig):
    # Construir las trazas con listas evita arrays binarios incompatibles con
    # algunas versiones del frontend Streamlit y conserva los números reales.
    fig.update_layout(
        template="plotly_white", font=dict(color="#282255", size=13),
        title=dict(x=0, font=dict(size=17)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(l=25, r=35, t=125, b=55),
    )
    st.plotly_chart(fig, config=chart_config, width="stretch", key=str(uuid4()))


def _missing(title, columns):
    st.info(f"{title}: la fuente actual no contiene los campos {', '.join(columns)}.")


def _percent_rows(df, mapping, checklist=False):
    rows = []
    for moment in _moments(df):
        part = df[df["momento"] == moment]
        for column, label in mapping.items():
            if column not in part:
                continue
            responses = _flag(part, column, checklist)
            total = int(responses.notna().sum())
            if total:
                count = int(responses.fillna(False).sum())
                rows.append(dict(momento=moment, categoria=label, porcentaje=count / total * 100,
                                 cantidad=count, total=total))
    return pd.DataFrame(rows, columns=["momento", "categoria", "porcentaje", "cantidad", "total"])


def _bars(rows, title, colors=None, horizontal=True):
    if rows.empty:
        st.info(f"{title}: no hay respuestas disponibles para graficar.")
        return
    colors = colors or MOMENT_COLORS
    categories = rows["categoria"].drop_duplicates().tolist()
    fig = go.Figure()
    for index, moment in enumerate(_moments(rows)):
        part = rows[rows["momento"] == moment].set_index("categoria").reindex(categories)
        # No agregar un 0 a una categoría cuyo denominador no está disponible.
        values = [float(v) if pd.notna(v) else None for v in part["porcentaje"]]
        custom = [[int(row.cantidad), int(row.total), category]
                  if pd.notna(row.total) else [None, None, category]
                  for category, row in part.iterrows()]
        axis = {"x": values, "y": [_wrap(c) for c in categories], "orientation": "h"} if horizontal else {
            "x": [_wrap(c, 23) for c in categories], "y": values}
        fig.add_trace(go.Bar(
            **axis, name=moment, marker_color=colors.get(moment, qualitative.Plotly[index % 10]),
            text=[f"{v:.1f}%" if v is not None else "" for v in values],
            textposition="outside", cliponaxis=False, customdata=custom,
            hovertemplate="%{customdata[2]}<br>%{text}<br>Observaciones: %{customdata[0]} de %{customdata[1]}<extra>%{fullData.name}</extra>",
        ))
    fig.update_layout(title=_wrap(title, 70), barmode="group",
                      height=max(400, len(categories) * 55 + 210) if horizontal else 460,
                      legend_title_text="Momento")
    if horizontal:
        fig.update_xaxes(range=[0, 112], ticksuffix="%", title="Porcentaje de observaciones")
        fig.update_yaxes(autorange="reversed", title=None)
    else:
        fig.update_yaxes(range=[0, 112], ticksuffix="%", title="Porcentaje de observaciones")
        fig.update_xaxes(title=None)
    _show(fig)


def _categorical_rows(df, column):
    if column not in df:
        return pd.DataFrame(columns=["momento", "categoria", "porcentaje", "cantidad", "total"])
    clean = df.copy()
    clean[column] = clean[column].astype("string").str.strip().fillna("Sin dato").replace("", "Sin dato")
    rows = clean.groupby(["momento", column], observed=True).size().reset_index(name="cantidad")
    categories = clean[column].drop_duplicates().tolist()
    totals = clean.groupby("momento").size()
    combinations = pd.MultiIndex.from_product(
        [_moments(clean), categories], names=["momento", column]
    )
    rows = rows.set_index(["momento", column]).reindex(combinations, fill_value=0).reset_index()
    rows["total"] = rows["momento"].map(totals)
    rows["porcentaje"] = rows["cantidad"] / rows["total"] * 100
    return rows.rename(columns={column: "categoria"})


def instantaneas(instantaneas):
    st.subheader("Instantáneas")
    df = _prepare(instantaneas)
    if df.empty:
        st.info("No hay instantáneas en los datos seleccionados.")
        return
    if INSTANT not in df:
        _missing("Instantáneas", [INSTANT])
        return
    df[INSTANT] = pd.to_numeric(df[INSTANT], errors="coerce")
    invalid = int(df[INSTANT].isna().sum())
    df = df.dropna(subset=[INSTANT])
    # Some exported slots have a snapshot number but no form answers.
    answer_columns = [
        "¿Qué está haciendo el/la docente ahora?", "accion_docente_cat", "accion_docente_clean",
        "interaccion", "interaccion_det", "participacion", "escucha", "notas", "preguntas",
        "socializacion", "socializacion_quien", "distraccion", "no_involucrados",
        "uso_tech", "uso_tech_quien", "trabajo_ind", "trabajo_grupo", "liderazgo", "autonomia", "comentarios",
        "¿Están haciendo uso de herramientas computacionales?",
        "¿Quiénes están haciendo uso de herramientas computacionales?",
    ]
    available_answers = [c for c in answer_columns if c in df]
    empty_slots = 0
    if available_answers:
        has_answer = df[available_answers].apply(
            lambda column: column.notna() & column.astype("string").str.strip().ne("").fillna(False)
        ).any(axis=1)
        empty_slots = int((~has_answer).sum())
        df = df[has_answer].copy()
    if empty_slots:
        st.caption(f"Se excluyen {empty_slots} filas con número de instantánea pero sin respuestas del formulario.")
    if df.empty:
        st.info("No hay números de instantánea válidos para graficar.")
        return
    st.caption(f"{len(df)} instantáneas con respuestas. Se incluyen todos los números con registros disponibles. "
               "Los porcentajes usan el total de observaciones de cada instantánea y momento; los vacíos se muestran como Sin dato.")
    if invalid:
        st.caption(f"{invalid} registros sin número de instantánea quedan fuera de estos gráficos.")
    if "accion_docente_cat" in df:
        clean = df.copy()
        clean["accion_docente_cat"] = clean["accion_docente_cat"].fillna("Sin dato")
        categories = sorted(clean["accion_docente_cat"].unique().tolist())
        palette = {c: qualitative.Plotly[i % 10]
                   for i, c in enumerate(c for c in categories if c != "Sin dato")}
        palette["Sin dato"] = "#8D8D96"
        for moment in _moments(clean):
            part = clean[clean["momento"] == moment]
            numbers = sorted(part[INSTANT].unique().tolist())
            totals = part.groupby(INSTANT).size()
            counts = part.groupby([INSTANT, "accion_docente_cat"]).size()
            fig = go.Figure()
            for category in categories:
                values = [100 * counts.get((number, category), 0) / totals[number] for number in numbers]
                fig.add_trace(go.Scatter(x=numbers, y=values, mode="lines+markers", name=category,
                                         line=dict(color=palette[category]),
                                         customdata=[[int(counts.get((n, category), 0)), int(totals[n])] for n in numbers],
                                         hovertemplate="Instantánea %{x}<br>%{y:.1f}%<br>Observaciones: %{customdata[0]} de %{customdata[1]}<extra>%{fullData.name}</extra>"))
            fig.update_layout(title=f"Distribución porcentual de observaciones — {moment}", height=500)
            fig.update_yaxes(range=[0, 105], title="Porcentaje (%)")
            fig.update_xaxes(tickmode="array", tickvals=numbers, title="Instantánea")
            _show(fig)
    else:
        _missing("Distribución porcentual", ["accion_docente_cat"])

    if "accion_docente_clean" not in df:
        _missing("Acciones del docente", ["accion_docente_clean"])
        return
    df["accion_docente_clean"] = df["accion_docente_clean"].fillna("Sin dato")
    actions = sorted(df["accion_docente_clean"].unique().tolist())
    for moment in _moments(df):
        part = df[df["momento"] == moment]
        numbers = sorted(part[INSTANT].unique().tolist())
        counts = part.groupby(["accion_docente_clean", INSTANT]).size().unstack(fill_value=0)
        counts = counts.reindex(index=actions, columns=numbers, fill_value=0)
        totals = part.groupby(INSTANT).size().reindex(numbers)
        percentages = counts.div(totals, axis=1) * 100
        fig = go.Figure(go.Heatmap(
            x=numbers, y=[_wrap(a) for a in actions], z=percentages.to_numpy().tolist(),
            colorscale=sequential.Purples, zmin=0, zmax=100,
            customdata=counts.to_numpy().tolist(), texttemplate="%{z:.1f}%",
            colorbar=dict(title="Porcentaje"),
            hovertemplate="Acción: %{y}<br>Instantánea %{x}<br>%{z:.1f}%<br>Observaciones: %{customdata}<extra></extra>",
        ))
        fig.update_layout(title=_wrap(f"¿Qué está haciendo el docente? — {moment}", 70),
                          height=max(450, len(actions) * 38 + 170))
        fig.update_xaxes(tickmode="array", tickvals=numbers, title="Instantánea")
        fig.update_yaxes(autorange="reversed")
        _show(fig)


GENERAL_PRACTICES = {
    "objetivos_aprend": "Inicio: objetivos de aprendizaje",
    "conoc_previos": "Inicio: conocimientos previos",
    "conceptos_clave": "Inicio: conceptos clave",
    "vocabulario_comp": "Desarrollo: vocabulario adecuado",
    "conexion_vida": "Desarrollo: conexión con la vida diaria",
    "prep_material": "Desarrollo: preparación de materiales",
    "gestion_material": "Desarrollo: gestión de materiales",
    "valoracion_esfuerzo": "Desarrollo: valoración del esfuerzo",
    "apoyo_estudiantes": "Desarrollo: apoyo a estudiantes",
    "uso_grafico_anclaje": "Cierre: gráfico de anclaje",
    "metacognicion": "Cierre: metacognición y reflexión",
}



def _practice_comparison(rows):
    if rows.empty:
        st.info("No hay respuestas de prácticas para comparar.")
        return
    categories = rows["categoria"].drop_duplicates().tolist()
    moments = _moments(rows)
    fig = go.Figure()
    for category in categories:
        part = rows[rows["categoria"] == category]
        if {"Pretest", "Postest"}.issubset(set(part["momento"])):
            values = part.set_index("momento").loc[["Pretest", "Postest"], "porcentaje"].tolist()
            fig.add_trace(go.Scatter(x=values, y=[_wrap(category)] * 2,
                                    mode="lines", line=dict(color="lightgray", width=2),
                                    showlegend=False, hoverinfo="skip"))
    for moment in moments:
        part = rows[rows["momento"] == moment]
        fig.add_trace(go.Scatter(
            x=part["porcentaje"].tolist(), y=[_wrap(v) for v in part["categoria"]],
            mode="markers+text", name=moment,
            marker=dict(color=PRACTICE_COLORS.get(moment, "#636EFA"),
                        size=17 if moment == "Pretest" else 10,
                        symbol="circle-open" if moment == "Pretest" else "diamond",
                        line=dict(width=2)),
            text=[f"{v:.1f}%" for v in part["porcentaje"]],
            textposition="top left" if moment == "Pretest" else "bottom right",
            cliponaxis=False,
            customdata=part[["cantidad", "total"]].values.tolist(),
            hovertemplate="%{y}<br>%{x:.1f}%<br>Respuestas Sí: %{customdata[0]} de %{customdata[1]}<extra>%{fullData.name}</extra>",
        ))
    fig.update_layout(title="Porcentaje de observaciones con respuesta Sí en cada práctica",
                      height=max(600, len(categories) * 48 + 200))
    fig.update_xaxes(range=[-5, 112], ticksuffix="%", title="Porcentaje de respuestas válidas")
    fig.update_yaxes(categoryorder="array", categoryarray=[_wrap(c) for c in categories],
                     autorange="reversed", title=None)
    _show(fig)


def observaciones_generales(obs_generales):
    st.subheader("Observaciones Generales")
    df = _prepare(obs_generales)
    if df.empty:
        st.info("No hay observaciones generales en los datos seleccionados.")
        return
    st.caption(f"{len(df)} observaciones de clase. Los porcentajes de prácticas se calculan sobre respuestas válidas "
               "por práctica y momento. Parcialmente cuenta como respuesta distinta de Sí; los vacíos y No aplica se excluyen.")
    absent = [c for c in GENERAL_PRACTICES if c not in df]
    if absent:
        _missing("Prácticas generales no disponibles", absent)
    _practice_comparison(_percent_rows(df, GENERAL_PRACTICES))

    st.subheader("Uso de guías de aprendizaje")
    if "guia_pedagogica" not in df:
        _missing("Uso de guías", ["guia_pedagogica"])
        return
    guide_flag = _flag(df, "guia_pedagogica")
    guides = df.copy()
    guides["uso_guia"] = guide_flag.map({True: "Sí", False: "No"}).fillna("Sin dato / No aplica")
    _bars(_categorical_rows(guides, "uso_guia"), "Distribución de observaciones según uso de guías", horizontal=False)
    users = df[guide_flag.fillna(False)].copy()

    st.subheader("Grado observado vs Grado de guía")
    if all(c in users for c in ["grado", "grado_guia"]):
        grades = users.copy()
        for col in ["grado", "grado_guia"]:
            grades[col] = pd.to_numeric(grades[col].astype("string").str.extract(r"(\d+)", expand=False), errors="coerce")
        grades = grades.dropna(subset=["grado", "grado_guia"])
        if grades.empty:
            st.info("No hay observaciones con uso de guía y ambos grados registrados.")
        else:
            # Con muestras pequeñas una caja colapsa y oculta los datos; puntos
            # de tamaño proporcional permiten ver también los pares repetidos.
            st.caption(f"{len(grades)} observaciones con guía y ambos grados registrados. Círculo: Pretest; rombo: Postest. El tamaño indica cuántas observaciones coinciden.")
            counts = grades.groupby(["momento", "grado", "grado_guia"]).size().reset_index(name="cantidad")
            fig = go.Figure()
            for i, moment in enumerate(_moments(counts)):
                part = counts[counts["momento"] == moment]
                fig.add_trace(go.Scatter(
                    x=part["grado"].tolist(), y=part["grado_guia"].tolist(), mode="markers",
                    name=moment, marker=dict(color=MOMENT_COLORS.get(moment, qualitative.Plotly[i % 10]),
                                            size=(part["cantidad"] * 5 + (24 if moment == "Pretest" else 12)).tolist(),
                                            symbol="circle-open" if moment == "Pretest" else "diamond",
                                            line=dict(width=2), opacity=0.9),
                    customdata=part["cantidad"].tolist(),
                    hovertemplate="Grado observado %{x}<br>Grado de guía %{y}<br>Observaciones: %{customdata}<extra>%{fullData.name}</extra>"))
            fig.update_layout(title="Grado observado vs grado de guía", height=420)
            fig.update_xaxes(title="Grado observado", dtick=1)
            fig.update_yaxes(title="Grado de guía", dtick=1)
            _show(fig)
    else:
        _missing("Comparación de grados", [c for c in ["grado", "grado_guia"] if c not in users])

    st.subheader("Distribución de observaciones con uso de guías de aprendizaje")
    st.caption(f"{len(users)} observaciones con respuesta Sí al uso de guías. Cada distribución usa ese subconjunto por momento.")
    for column, label in {"sexo_docente": "Sexo del docente", "grado": "Grado observado", "asignatura": "Asignatura"}.items():
        if column not in users:
            _missing(label, [column])
            continue
        _bars(_categorical_rows(users, column), f"Observaciones con uso de guías por {label.lower()}")


PRIMM = {
    "Predecir": {"act_conectada_predecir": "Presenta código y pregunta qué hará"},
    "Ejecutar": {"act_conectada_ejecutar_replicar": "Replican código presentado", "act_conectada_ejecutar_entregar": "Ejecutan código entregado"},
    "Investigar": {"act_conectada_investigar_libre": "Exploración libre", "act_conectada_investigar_guiada": "Exploración guiada", "act_conectada_investigar_compartir": "Comparten hallazgos"},
    "Modificar": {"act_conectada_modificar_ind": "Cambios independientes", "act_conectada_modificar_docente": "Cambios liderados por docente", "act_conectada_modificar_apoyo": "Cambios con apoyo ocasional"},
    "Hacer": {"act_conectada_hacer_ind": "Reto individual", "act_conectada_hacer_apoyo": "Reto con apoyo", "act_conectada_hacer_replicar": "Replican solución del docente"},
}


def _group_detail(df, mapping, title, checklist=False):
    missing = [c for c in mapping if c not in df]
    if missing:
        _missing(title + " (campos no disponibles)", missing)
    _bars(_percent_rows(df, mapping, checklist), title)


def observaciones_ti(obs_generales):
    df = _prepare(obs_generales)
    st.subheader("Actividades conectadas y desconectadas")
    required = ["act_conectada_presente", "act_desconectada_presente"]
    if not all(c in df for c in required):
        _missing("Tipos de actividad", [c for c in required if c not in df])
        return
    connected = _flag(df, required[0])
    disconnected = _flag(df, required[1])
    classified = df[connected.notna() & disconnected.notna()].copy()
    if classified.empty:
        st.info("No hay respuestas sobre actividades TI en la fuente actual.")
        return
    def classify(index):
        c, d = bool(connected[index]), bool(disconnected[index])
        return "Ambas" if c and d else "Conectada" if c else "Desconectada" if d else "Ninguna"
    classified["tipo_actividad"] = [classify(i) for i in classified.index]
    st.caption(f"{len(classified)} observaciones con respuesta válida en ambos tipos de actividad. "
               "Se cuentan observaciones de clase, no docentes únicos.")
    _bars(_categorical_rows(classified, "tipo_actividad"), "Distribución de observaciones según tipo de actividad", horizontal=False)

    st.subheader("Prácticas en actividades desconectadas")
    disconnected_df = df[disconnected.fillna(False)].copy()
    st.caption(f"{len(disconnected_df)} observaciones con actividad desconectada. Cada práctica usa sus respuestas válidas.")
    _group_detail(disconnected_df, {
        "act_desconectada_compartir": "Estudiantes comparten la solución",
        "act_desconectada_cierre": "Onda semántica: cierre relacionado con el tema",
        "act_desconectada_eficacia": "Aplicación efectiva de conceptos o subhabilidades",
    }, "Prácticas en actividades desconectadas")

    st.subheader("Prácticas en actividades conectadas")
    connected_df = df[connected.fillna(False)].copy()
    st.caption(f"{len(connected_df)} observaciones con actividad conectada. Las casillas sin seleccionar cuentan como 0; "
               "cada observación se cuenta una vez por grupo PRIMM. Las categorías pueden coincidir.")
    group_df = connected_df[["momento"]].copy()
    group_map = {}
    for group, mapping in PRIMM.items():
        available = [c for c in mapping if c in connected_df]
        if available:
            group_df[group] = pd.concat([_flag(connected_df, c, True).fillna(False) for c in available], axis=1).any(axis=1)
            group_map[group] = group
    _bars(_percent_rows(group_df, group_map), "Observaciones por grupo PRIMM", horizontal=False)
    st.subheader("Distribución por práctica dentro de cada grupo PRIMM")
    for group, mapping in PRIMM.items():
        if group not in group_df:
            _missing(f"PRIMM: {group}", list(mapping))
            continue
        subset = connected_df[group_df[group]].copy()
        st.caption(f"{group}: {len(subset)} observaciones con al menos una práctica de este grupo.")
        _group_detail(subset, mapping, f"PRIMM — {group}: distribución por práctica", checklist=True)

    st.subheader("Estrategias conectadas")
    _group_detail(connected_df, {
        "estrategia_pares": "Programación por pares", "estrategia_parsons": "Preguntas de Parsons",
        "estrategia_vivo": "Programación en vivo", "estrategia_lectura": "Lectura de código",
        "estrategia_evaluacion": "Evaluación de pares", "estrategia_proyectos": "Aprendizaje basado en proyectos",
        "estrategia_diseno": "Pensamiento de diseño", "estrategia_tinkering": "Tinkering",
        "estrategia_ninguna": "No se observa ninguna estrategia",
    }, "Estrategias en observaciones con actividad conectada", checklist=True)


def observaciones_stem(obs_generales):
    df = _prepare(obs_generales)
    st.subheader("Subhabilidades y Weintrop")
    main = {"practicas_datos": "Prácticas de datos", "practicas_programacion": "Prácticas de programación",
            "simulaciones": "Simulaciones", "pensamiento_sistemico": "Pensamiento sistémico"}
    required = ["subhabilidades_comp", *main]
    if not all(c in df for c in required):
        _missing("Análisis STEM de subhabilidades y Weintrop", [c for c in required if c not in df])
        return
    sub = _flag(df, "subhabilidades_comp")
    flags = pd.concat([_flag(df, c) for c in main], axis=1)
    valid = sub.notna() & flags.notna().all(axis=1)
    complete = df[valid].copy()
    if complete.empty:
        st.info("No hay respuestas válidas de subhabilidades y Weintrop para graficar.")
        return
    weintrop = flags.fillna(False).any(axis=1)
    complete["tipo_practica"] = [
        "Ambas" if sub[i] and weintrop[i] else "Solo subhabilidades" if sub[i] else "Solo Weintrop" if weintrop[i] else "Ninguna"
        for i in complete.index]
    _bars(_categorical_rows(complete, "tipo_practica"), "Distribución de observaciones según tipo de práctica STEM", horizontal=False)
    st.subheader("Detalle de subhabilidades aplicadas")
    _group_detail(df[sub.fillna(False)].copy(), {
        "descomposicion": "Descomposición", "patrones": "Patrones", "algoritmico": "Pensamiento algorítmico",
        "depuracion": "Depuración", "abstraccion": "Abstracción", "logico": "Pensamiento lógico",
    }, "Subhabilidades en observaciones que las aplican")
    st.subheader("Detalle de prácticas de Weintrop aplicadas")
    _group_detail(df[weintrop].copy(), main, "Distribución general de prácticas de Weintrop")
    dimensions = {
        "practicas_datos": {"recoleccion_datos": "Recolección de datos", "patrones_datos": "Patrones en datos", "organizacion_datos": "Organización de datos", "visualizacion_datos": "Visualización de datos"},
        "practicas_programacion": {"descomposicion_prog": "Descomposición", "instrucciones_prog": "Instrucciones paso a paso", "codificacion": "Codificación", "depuracion_prog": "Depuración"},
        "simulaciones": {"uso_simuladores": "Uso de simuladores", "evaluacion_simulaciones": "Evaluación de simulaciones"},
        "pensamiento_sistemico": {"datos_numericos": "Datos numéricos", "relaciones_numericas": "Relaciones numéricas", "impacto_variables": "Impacto de variables"},
    }
    for column, mapping in dimensions.items():
        _group_detail(df[_flag(df, column).fillna(False)].copy(), mapping, f"{main[column]}: distribución por subpráctica")
