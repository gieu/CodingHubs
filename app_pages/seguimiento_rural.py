import re
import urllib.parse

import pandas as pd
import plotly.express as px
import streamlit as st

from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import header
from utils.chart_config import get_chart_config


header("#282255")
chart_config = get_chart_config()

RURAL_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSV5EzdlBEDHngwEQtfM6L3ilW0Bj8oMtXB1ndPB5GNszQoYJjRKcS4utBO9akNQuxv_Fgj8V7SH9rp/pub?output=csv"

QUESTION_TEXTS = {
    "P1": "¿Esta semana ha utilizado el juego Biobots con los estudiantes?",
    "P2": "¿Podría compartir la razón por la que no ha podido implementarlo?",
    "P3": "¿Con qué grados ha utilizado el juego?",
    "P4": "¿Cuántas veces por semana ha utilizado el juego?",
    "P5": "En promedio, ¿cuánto tiempo tardó cada sesión de juego?",
    "P6": "¿Qué escenarios del juego ha implementado con los estudiantes?",
    "P7": "¿Qué fase del escenario jugado alcanzaron? (No aplica para el Escenario 1)",
    "P8": "¿Ha encontrado dificultades al usar el juego con los estudiantes?",
    "P9": "Durante la sesión, ¿identificó alguna fortaleza o resultado positivo del juego?",
    "P10": "En una escala del 1 al 5, siendo 1 muy bajo y 5 muy alto, ¿cómo calificaría el desempeño de los estudiantes en el juego?",
}

P3_GRADE_ORDER = [
    "Preescolar",
    "Jardín",
    "Primero",
    "Segundo",
    "Tercero",
    "Cuarto",
    "Quinto",
    "Sexto",
    "Séptimo",
    "Octavo",
    "Noveno",
    "Décimo",
    "Once",
    "Aula multigrado",
    "No responde",
]

P3_GRADE_ALIASES = {
    "aula multigrado": "Aula multigrado",
    "decimo": "Décimo",
    "décimo": "Décimo",
    "jardin": "Jardín",
    "jardín": "Jardín",
    "once": "Once",
    "preescolar": "Preescolar",
    "primero": "Primero",
    "segundo": "Segundo",
    "septimo": "Séptimo",
    "séptimo": "Séptimo",
    "sexto": "Sexto",
    "tercer": "Tercero",
    "tercero": "Tercero",
    "cuarto": "Cuarto",
    "quinto": "Quinto",
    "octavo": "Octavo",
    "noveno": "Noveno",
    "no responde": "No responde",
}


@st.cache_data(ttl=300)
def load_data(file):
    if isinstance(file, str) and file.startswith("http"):
        file = urllib.parse.quote(file, safe=":/?=&")
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    return df


def _plot_chart(container, fig, key=None):
    container.plotly_chart(
        fig,
        key=key,
        use_container_width=True,
        config=chart_config,
    )


def _clean_answer_series(series):
    return (
        series.astype("string")
        .str.strip()
        .replace({"": pd.NA, "NA": pd.NA, "na": pd.NA})
    )


def _numeric_series(series):
    return pd.to_numeric(
        series.astype("string").str.replace(",", ".", regex=False).str.strip(),
        errors="coerce",
    )


def _parse_call_dates(series):
    cleaned = series.astype("string").str.strip()
    dates = pd.to_datetime(cleaned, errors="coerce", dayfirst=True)

    for date_format in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
        missing = dates.isna() & cleaned.notna()
        if not missing.any():
            break
        dates.loc[missing] = pd.to_datetime(
            cleaned.loc[missing],
            errors="coerce",
            format=date_format,
        )

    return dates


def _expanded_scenarios(df):
    columns = ["Escenario", "Tipo", "Nombres completos docentes", "Fecha_llamada"]
    if "P6" not in df.columns:
        return pd.DataFrame(columns=columns)

    records = []
    p6_clean = df.dropna(subset=["P6"]).copy()
    for _, row in p6_clean.iterrows():
        value = str(row["P6"]).strip()
        normalized = value.lower()
        categories = []

        if normalized in {"no responde", "n"}:
            categories.append(("No responde", "Sin respuesta"))
        else:
            nums = re.findall(r"\d+", value)
            categories.extend((f"Escenario {n}", "Juego") for n in nums)

            if re.search(r"exploraci[oó]n", normalized):
                categories.append(("Exploración del juego", "Exploración"))

            if re.search(r"repaso|inducci[oó]n", normalized):
                categories.append(("Repaso / inducción", "Repaso"))

            if not categories:
                categories.append(("Otro", "Otro"))

        for escenario, tipo in categories:
            records.append(
                {
                    "Escenario": escenario,
                    "Tipo": tipo,
                    "Nombres completos docentes": row.get("Nombres completos docentes"),
                    "Fecha_llamada": row.get("Fecha_llamada"),
                }
            )

    return pd.DataFrame(records, columns=columns)


def _sort_scenarios(series):
    return series.str.extract(r"(\d+)").iloc[:, 0].astype(float).fillna(999)


def _wrap_text(text, max_length=15):
    text = str(text)
    if len(text) <= max_length:
        return text

    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + len(current_line) <= max_length:
            current_line.append(word)
            current_length += len(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)

    if current_line:
        lines.append(" ".join(current_line))

    return "<br>".join(lines)


def _place_small_bar_labels_outside(fig, values=None, threshold=1):
    fallback_values = list(values) if values is not None else None
    for trace in fig.data:
        trace_values = (
            list(trace.y) if getattr(trace, "y", None) is not None else fallback_values
        )
        if not trace_values:
            continue
        trace.update(
            textposition=[
                "outside" if value <= threshold else "auto" for value in trace_values
            ],
            cliponaxis=False,
        )


def _p3_grade_mentions(df):
    if "P3" not in df.columns:
        return pd.DataFrame(columns=["Grado", "Menciones"])

    binary_rows = []
    values = _clean_answer_series(df["P3"])
    for value in values:
        row = {grade: 0 for grade in P3_GRADE_ORDER}
        if pd.notna(value):
            for item in str(value).split(","):
                normalized = item.strip().lower()
                grade = P3_GRADE_ALIASES.get(normalized)
                if grade:
                    row[grade] = 1
        binary_rows.append(row)

    binary_df = pd.DataFrame(binary_rows, columns=P3_GRADE_ORDER)
    long_df = binary_df.melt(var_name="Grado", value_name="Reportado")
    counts = (
        long_df[long_df["Reportado"].eq(1)]
        .groupby("Grado")
        .size()
        .reindex(P3_GRADE_ORDER, fill_value=0)
        .reset_index(name="Menciones")
    )
    return counts[counts["Menciones"].gt(0)]


def _simple_bar(df, column, title, x_title="", key=None):
    counts = df[column].dropna().value_counts().reset_index()
    counts.columns = [column, "Frecuencia"]
    if counts.empty:
        st.info(f"No hay respuestas registradas para {column}.")
        return

    fig = px.bar(
        counts,
        x=column,
        y="Frecuencia",
        text="Frecuencia",
        title=title,
        category_orders={column: counts[column].tolist()},
    )
    fig.update_layout(xaxis_title=x_title, yaxis_title="Frecuencia")
    _place_small_bar_labels_outside(fig, counts["Frecuencia"])
    _plot_chart(st, fig, key)


def dashboard_seguimiento_region(df, region_name: str, key_suffix=""):
    df = df.copy()
    df.columns = df.columns.str.strip()
    df = df.replace({"": None, "NA": None, "na": None})

    if "Fecha_llamada" in df.columns:
        df["Fecha_llamada"] = _parse_call_dates(df["Fecha_llamada"])

    for column in [f"P{i}" for i in range(1, 11)] + ["Razones P2"]:
        if column in df.columns:
            df[column] = _clean_answer_series(df[column])

    total_calls = len(df)
    total_docentes = (
        df["Nombres completos docentes"].nunique()
        if "Nombres completos docentes" in df.columns
        else 0
    )
    total_sesiones = (
        int(_numeric_series(df["P4"]).dropna().sum()) if "P4" in df.columns else 0
    )
    promedio_sesiones = (
        _numeric_series(df["P5"]).dropna().mean() if "P5" in df.columns else 0
    )
    if pd.isna(promedio_sesiones):
        promedio_sesiones = 0

    st.title("Seguimiento Rural")
    st.subheader(f"Resumen Ejecutivo - {region_name}")

    resumen = [
        f"Se registraron **{total_calls} llamadas** correspondientes a **{total_docentes} docentes**."
    ]
    if total_sesiones > 0:
        resumen.append(
            f"En total se reportaron **{total_sesiones} sesiones implementadas**, "
            f"con un promedio de **{promedio_sesiones:.1f} minutos** por sesión."
        )
    else:
        resumen.append("Aún no se reportan sesiones implementadas en la región.")

    p6_expanded = _expanded_scenarios(df)
    if not p6_expanded.empty:
        top_escenarios = p6_expanded["Escenario"].value_counts().head(5).index.tolist()
        resumen.append(
            f"Los escenarios con mayor número de implementaciones fueron: {', '.join(top_escenarios)}. "
            "(Incluye repasos)"
        )

    if "P7" in df.columns:
        p7_respuestas = df["P7"].dropna()
        if p7_respuestas.empty:
            resumen.append(
                "No se reportaron respuestas sobre la fase alcanzada en los escenarios jugados."
            )
        else:
            resumen.append(
                f"Se identificaron **{len(p7_respuestas)} respuestas** sobre la fase alcanzada en los escenarios jugados."
            )

    if "P8" in df.columns:
        dificultades = df["P8"].dropna()
        if not dificultades.empty:
            resumen.append(
                f"Se registraron **{len(dificultades)} respuestas** sobre dificultades al usar el juego."
            )

    for punto in resumen:
        st.markdown(f"- {punto}")

    st.markdown("---")

    if "P1" in df.columns and "Nombres completos docentes" in df.columns:
        st.subheader(f"P1. {QUESTION_TEXTS['P1']}")

        p1_date_column = "Fecha_llamada"
        has_p1_dates = p1_date_column in df.columns
        df_sorted = (
            df.dropna(subset=[p1_date_column, "P1"]).sort_values(
                ["Nombres completos docentes", p1_date_column]
            )
            if has_p1_dates
            else pd.DataFrame()
        )
        if df_sorted.empty:
            p1_counts = df["P1"].dropna().value_counts().reset_index()
            p1_counts.columns = ["Respuesta", "Frecuencia"]
            if p1_counts.empty:
                st.info("No hay respuestas registradas para P1.")
            else:
                fig_p1_counts = px.bar(
                    p1_counts,
                    x="Respuesta",
                    y="Frecuencia",
                    text="Frecuencia",
                    title="Frecuencia de implementación",
                )
                _place_small_bar_labels_outside(fig_p1_counts, p1_counts["Frecuencia"])
                _plot_chart(st, fig_p1_counts, f"fig_p1_counts_{key_suffix}")
        else:
            iso_calendar = df_sorted[p1_date_column].dt.isocalendar()
            df_sorted["Anio"] = iso_calendar.year
            df_sorted["Semana"] = iso_calendar.week
            p1_time = (
                df_sorted.groupby(["Anio", "Semana", "P1"])
                .agg(
                    Frecuencia=("P1", "size"),
                    Fecha_inicio=(p1_date_column, "min"),
                    Fecha_fin=(p1_date_column, "max"),
                )
                .reset_index()
                .sort_values(["Anio", "Semana", "P1"])
            )
            if p1_time.empty:
                st.info("No hay datos suficientes para construir la frecuencia semanal.")
            else:
                p1_without_date = df[df["P1"].notna() & df[p1_date_column].isna()]
                p1_time["Semana_label"] = p1_time["Semana"].astype(str)
                p1_time["Rango_fechas"] = (
                    p1_time["Fecha_inicio"].dt.strftime("%d/%m/%Y")
                    + " - "
                    + p1_time["Fecha_fin"].dt.strftime("%d/%m/%Y")
                )
                week_order = p1_time["Semana_label"].drop_duplicates().tolist()
                if not p1_without_date.empty:
                    p1_no_date = (
                        p1_without_date.groupby("P1")
                        .size()
                        .reset_index(name="Frecuencia")
                    )
                    p1_no_date["Semana_label"] = "No recuerda"
                    p1_no_date["Rango_fechas"] = "No recuerda"
                    p1_time = pd.concat(
                        [
                            p1_time,
                            p1_no_date[
                                ["P1", "Frecuencia", "Semana_label", "Rango_fechas"]
                            ],
                        ],
                        ignore_index=True,
                    )
                    week_order.append("No recuerda")
                fig_p1_time = px.bar(
                    p1_time,
                    x="Semana_label",
                    y="Frecuencia",
                    text="Frecuencia",
                    hover_data=["Rango_fechas"],
                    color="P1",
                    title="Frecuencia semanal de implementación",
                    category_orders={"Semana_label": week_order},
                    height=500,
                )
                fig_p1_time.update_layout(xaxis_title="Semana", yaxis_title="Frecuencia")
                fig_p1_time.update_xaxes(
                    type="category",
                    categoryorder="array",
                    categoryarray=week_order,
                )
                _place_small_bar_labels_outside(fig_p1_time)
                _plot_chart(st, fig_p1_time, f"fig_p1_{key_suffix}")

    col1, col2 = st.columns(2)
    col1.subheader(f"P2. {QUESTION_TEXTS['P2']}")
    col2.subheader(f"P5. {QUESTION_TEXTS['P5']}")

    if "P2" in df.columns:
        reason_column = "Razones P2" if "Razones P2" in df.columns else "P2"
        p2_counts = df[reason_column].dropna().value_counts().reset_index()
        p2_counts.columns = ["Razón", "Cuenta"]
        col1.dataframe(p2_counts, use_container_width=True, hide_index=True)

    if "P5" in df.columns:
        p5_counts = _numeric_series(df["P5"]).dropna().reset_index(drop=True)
        p5_counts.name = "Duración (minutos)"
        if p5_counts.empty:
            col2.info("No hay duración registrada.")
        else:
            fig_p5 = px.histogram(
                p5_counts,
                x="Duración (minutos)",
                nbins=10,
                text_auto=True,
                title="Distribución de duración",
                labels={"count": "Frecuencia"},
            )
            fig_p5.update_layout(yaxis_title="Frecuencia")
            fig_p5.update_traces(textposition="outside", cliponaxis=False)
            _plot_chart(col2, fig_p5, f"fig_p5_{key_suffix}")

    if "P3" in df.columns:
        st.subheader(f"P3. {QUESTION_TEXTS['P3']}")
        p3_counts = _p3_grade_mentions(df)
        if p3_counts.empty:
            st.info("No hay grados registrados.")
        else:
            p3_counts["Grado_label"] = p3_counts["Grado"].map(
                lambda value: _wrap_text(value, max_length=12)
            )
            grade_order = [_wrap_text(value, max_length=12) for value in P3_GRADE_ORDER]
            fig_p3 = px.bar(
                p3_counts,
                x="Grado_label",
                y="Menciones",
                text="Menciones",
                title="Grados reportados en la implementación",
                category_orders={"Grado_label": grade_order},
            )
            fig_p3.update_layout(
                xaxis_title="Grado",
                yaxis_title="Menciones",
                height=500,
            )
            _place_small_bar_labels_outside(fig_p3, p3_counts["Menciones"])
            _plot_chart(st, fig_p3, f"fig_p3_{key_suffix}")

    if "P4" in df.columns:
        st.subheader(f"P4. {QUESTION_TEXTS['P4']}")

        required = ["P4", "Nombres completos docentes", "Fecha_llamada"]
        p4_df = df.dropna(subset=required).copy() if all(
            column in df.columns for column in required
        ) else pd.DataFrame()
        if not p4_df.empty:
            p4_df["P4"] = _numeric_series(p4_df["P4"])
            p4_df = p4_df.dropna(subset=["P4"])

        if p4_df.empty:
            p4_counts = (
                _numeric_series(df["P4"])
                .dropna()
                .astype(int)
                .value_counts()
                .sort_index()
                .reset_index()
            )
            p4_counts.columns = ["Sesiones por semana", "Frecuencia"]
            if p4_counts.empty:
                st.info("No hay datos suficientes para construir la gráfica de sesiones.")
            else:
                fig_p4_counts = px.bar(
                    p4_counts,
                    x="Sesiones por semana",
                    y="Frecuencia",
                    text="Frecuencia",
                    title="Distribución de sesiones por semana",
                )
                fig_p4_counts.update_xaxes(dtick=1)
                _place_small_bar_labels_outside(fig_p4_counts, p4_counts["Frecuencia"])
                _plot_chart(st, fig_p4_counts, f"fig_p4_counts_{key_suffix}")
        else:
            iso = p4_df["Fecha_llamada"].dt.isocalendar().copy()
            p4_df.loc[:, "Anio"] = iso.year
            p4_df.loc[:, "Semana"] = iso.week
            p4_df.loc[:, "Fecha_inicio"] = pd.to_datetime(
                p4_df["Anio"].astype(str) + "-W" + p4_df["Semana"].astype(str) + "-1",
                format="%G-W%V-%u",
            )
            p4_df.loc[:, "Fecha_fin"] = p4_df["Fecha_inicio"] + pd.Timedelta(days=6)

            plot_df = (
                p4_df.groupby(
                    [
                        "Nombres completos docentes",
                        "Anio",
                        "Semana",
                        "Fecha_inicio",
                        "Fecha_fin",
                    ],
                    as_index=False,
                )["P4"]
                .sum()
            )
            plot_df.loc[:, "P4_str"] = plot_df["P4"].round().astype(int).astype(str)

            totals_series = (
                plot_df.groupby("Nombres completos docentes")["P4"].sum().astype(int)
            )
            totals_dict = totals_series.to_dict()
            plot_df.loc[:, "Docente_con_total"] = plot_df[
                "Nombres completos docentes"
            ].map(lambda d: f"{d} (Total: {totals_dict.get(d, 0)})")
            ordered_docentes = list(totals_series.sort_values(ascending=False).index)
            ordered_labels = [
                f"{d} (Total: {totals_dict.get(d, 0)})" for d in ordered_docentes
            ]

            fig_timeline = px.timeline(
                plot_df,
                x_start="Fecha_inicio",
                x_end="Fecha_fin",
                y="Docente_con_total",
                color="P4_str",
                text="P4_str",
                category_orders={
                    "P4_str": sorted(plot_df["P4_str"].dropna().unique(), reverse=True),
                    "Docente_con_total": ordered_labels,
                },
            )

            week_ticks = (
                plot_df.groupby("Semana")[["Fecha_inicio", "Fecha_fin"]]
                .first()
                .assign(
                    mid=lambda d: d["Fecha_inicio"]
                    + (d["Fecha_fin"] - d["Fecha_inicio"]) / 2,
                )
            )

            fig_timeline.update_layout(
                xaxis=dict(
                    title="Semana de implementación",
                    tickmode="array",
                    tickvals=week_ticks["mid"].tolist(),
                    ticktext=week_ticks.index.astype(str).tolist(),
                ),
                yaxis_title="Docente",
                height=600,
                legend_title="Número de sesiones",
            )
            _plot_chart(st, fig_timeline, f"fig_p4_{key_suffix}")

    col_p6, col_p7 = st.columns(2)
    col_p6.subheader(f"P6. {QUESTION_TEXTS['P6']}")
    col_p7.subheader(f"P7. {QUESTION_TEXTS['P7']}")

    with col_p6:
        if p6_expanded.empty:
            st.info("No hay escenarios registrados.")
        else:
            p6_counts = (
                p6_expanded.groupby(["Escenario", "Tipo"])
                .size()
                .reset_index(name="Frecuencia")
                .sort_values(by="Escenario", key=_sort_scenarios)
            )
            p6_counts["Escenario_label"] = p6_counts["Escenario"].map(
                lambda value: _wrap_text(value, max_length=12)
            )
            scenario_order = [
                _wrap_text(value, max_length=12)
                for value in [
                    "Exploración del juego",
                    "Escenario 1",
                    "Escenario 2",
                    "Escenario 3",
                    "Escenario 4",
                    "Repaso / inducción",
                    "No responde",
                ]
            ]
            fig_p6 = px.bar(
                p6_counts,
                x="Escenario_label",
                y="Frecuencia",
                text="Frecuencia",
                title="Escenarios implementados",
                category_orders={"Escenario_label": scenario_order},
            )
            fig_p6.update_layout(xaxis_title="Escenario")
            _place_small_bar_labels_outside(fig_p6, p6_counts["Frecuencia"])
            _plot_chart(st, fig_p6, f"fig_p6_{key_suffix}")

    with col_p7:
        if "P7" not in df.columns:
            st.info("No existe la columna P7.")
        else:
            p7_counts = df["P7"].dropna().value_counts().reset_index()
            p7_counts.columns = ["Fase alcanzada", "Frecuencia"]
            if p7_counts.empty:
                st.info("No hay fases registradas.")
            else:
                fig_p7 = px.bar(
                    p7_counts,
                    x="Fase alcanzada",
                    y="Frecuencia",
                    text="Frecuencia",
                    title="Fases alcanzadas",
                    category_orders={
                        "Fase alcanzada": p7_counts["Fase alcanzada"].tolist()
                    },
                )
                fig_p7.update_layout(xaxis_title="", yaxis_title="Frecuencia")
                _place_small_bar_labels_outside(fig_p7, p7_counts["Frecuencia"])
                _plot_chart(st, fig_p7, f"fig_p7_{key_suffix}")

    col_p8, col_p9 = st.columns(2)
    col_p8.subheader(f"P8. {QUESTION_TEXTS['P8']}")
    col_p9.subheader(f"P9. {QUESTION_TEXTS['P9']}")

    with col_p8:
        if "P8" in df.columns:
            _simple_bar(df, "P8", "Dificultades reportadas", key=f"fig_p8_{key_suffix}")
        else:
            st.info("No existe la columna P8.")

    with col_p9:
        if "P9" in df.columns:
            _simple_bar(
                df,
                "P9",
                "Fortalezas o resultados positivos",
                key=f"fig_p9_{key_suffix}",
            )
        else:
            st.info("No existe la columna P9.")

    st.subheader(f"P10. {QUESTION_TEXTS['P10']}")

    if "P10" in df.columns:
        p10_values = _numeric_series(df["P10"]).dropna().astype(int)
        p10_counts = p10_values.value_counts().sort_index().reset_index()
        p10_counts.columns = ["Calificación", "Frecuencia"]
        if p10_counts.empty:
            st.info("No hay calificaciones registradas.")
        else:
            fig_p10 = px.bar(
                p10_counts,
                x="Calificación",
                y="Frecuencia",
                text="Frecuencia",
                title="Desempeño reportado por docentes",
                category_orders={"Calificación": [1, 2, 3, 4, 5]},
            )
            fig_p10.update_xaxes(dtick=1)
            _place_small_bar_labels_outside(fig_p10, p10_counts["Frecuencia"])
            _plot_chart(st, fig_p10, f"fig_p10_{key_suffix}")
    else:
        st.info("No existe la columna P10.")


try:
    df_rural = load_data(RURAL_CSV_URL)
    dashboard_seguimiento_region(df_rural, "Rural", key_suffix="rural")

    with st.expander("Ver datos completos"):
        private_columns = [
            col for col in ["Número telefónico docente"] if col in df_rural.columns
        ]
        st.dataframe(
            df_rural.drop(columns=private_columns),
            use_container_width=True,
            hide_index=True,
        )
except Exception as exc:
    st.error("No fue posible cargar el seguimiento rural.")
    st.exception(exc)


st.markdown("---")
formatted_footer = FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64)
st.markdown(formatted_footer, unsafe_allow_html=True)
