import unicodedata
import urllib.parse
import re

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import header
from utils.chart_config import get_chart_config


header("#2C3E50")
CHART_CONFIG = get_chart_config()

CONSOLIDADO_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1GX2clKbLTkcS9-2p8Tc3-v7Ypxka3WGiyiGm7nAeYCg/"
    "export?format=csv&gid=89776440"
)
SHEET_ID = "1rXvcxnxjMRuONbcpJ1yRoQG3GXRcGBfACxnSCQb2MJI"
GID = "0"
TEACHER_TRACKING_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
)
COLORS = {
    "blue": "#1DB2E8",
    "green": "#00A651",
    "orange": "#F39C12",
    "blue_dark": "#0D47A1",
    "text_dark": "#2C3E50",
    "muted": "#E3F2FD",
}

TREATMENT_NAMES = {
    "erika andrea lopez toro",
    "cristian andres giraldo ceballos",
    "luis enrique zapata valencia",
    "alexandra maria montes cardona",
    "mario andres gomez quintero",
    "jhon mauricio bustamante arias",
    "martha luz arias moreno",
    "luz elena buitrago zapata",
    "john alejandro sierra gonzales",
    "liliana constanza aristizabal serna",
}


@st.cache_data(ttl=300)
def load_consolidado(url):
    safe_url = urllib.parse.quote(url, safe=":/?=&")
    df = pd.read_csv(safe_url)
    df.columns = df.columns.str.strip()
    return df


def excel_column(df, letters):
    index = 0
    for char in letters.upper():
        index = index * 26 + ord(char) - ord("A") + 1
    zero_based = index - 1
    if zero_based >= len(df.columns):
        raise KeyError(f"La columna {letters} no existe en la fuente actual.")
    return df.columns[zero_based]


def numeric_column(df, letters):
    return pd.to_numeric(df[excel_column(df, letters)], errors="coerce").fillna(0)


def normalize_text(value):
    text = unicodedata.normalize("NFKD", str(value))
    return " ".join(
        "".join(char for char in text if not unicodedata.combining(char))
        .lower()
        .strip()
        .split()
    )


def clean_teacher_names(series):
    cleaned = series.astype("string").str.strip()
    cleaned = cleaned.replace({"": pd.NA, "NA": pd.NA, "na": pd.NA})
    cleaned = cleaned.where(cleaned != "Nombres completos docentes", pd.NA)
    return cleaned


def clean_p6_value(value):
    text = normalize_text(value)
    if text in {"", "nan", "na", "p6", "-"}:
        return None
    return text


def extract_scenarios_from_p6(value):
    text = clean_p6_value(value)
    if text is None:
        return set()

    scenarios = set()
    if "exploracion del juego" in text:
        scenarios.add("Exploración del juego")

    for number in re.findall(r"escenario\s*(\d+)", text):
        scenarios.add(f"Escenario {int(number)}")

    return scenarios


def scenario_sort_key(label):
    if label == "Exploración del juego":
        return (0, 0)
    if label.startswith("Escenario "):
        try:
            return (1, int(label.split(" ", 1)[1]))
        except (ValueError, IndexError):
            return (1, 999)
    return (2, 999)


def recognized_game(series):
    numeric = pd.to_numeric(series, errors="coerce").fillna(0).gt(0)
    categorical = series.map(normalize_text).isin({"si", "yes", "verdadero", "true"})
    return numeric | categorical


def style_figure(fig, height=430):
    fig.update_layout(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial", color=COLORS["text_dark"]),
        title=dict(font=dict(size=20, color=COLORS["text_dark"]), x=0),
        margin=dict(l=50, r=30, t=85, b=55),
        hoverlabel=dict(bgcolor="white"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="#E9EFF5", zeroline=False)
    return fig


def plot(fig, key):
    st.plotly_chart(fig, width="stretch", config=CHART_CONFIG, key=key)


def analysis_callout(hallazgo, implicacion, accion):
    st.markdown(
        f"""
        <div style="background:#F3F8FC;border-left:5px solid {COLORS['orange']};
                    padding:14px 18px;margin:-4px 0 28px;border-radius:0 8px 8px 0;color:#2C3E50">
            <strong>Lectura para la acción</strong><br>
            <span><strong>Hallazgo:</strong> {hallazgo}</span><br>
            <span><strong>Implicación:</strong> {implicacion}</span><br>
            <span><strong>Acción:</strong> {accion}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def implementation_distribution(df):
    sessions = numeric_column(df, "CS").round().astype(int)
    plot_df = (
        sessions.value_counts()
        .sort_index()
        .rename_axis("Sesiones")
        .reset_index(name="Docentes")
    )
    fig = px.bar(
        plot_df,
        x="Sesiones",
        y="Docentes",
        text="Docentes",
        color_discrete_sequence=[COLORS["blue"]],
        category_orders={"Sesiones": sorted(plot_df["Sesiones"].tolist())},
        title="Distribución de docentes según el número de sesiones de implementación realizadas",
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_xaxes(title="Número de sesiones de implementación", dtick=1)
    fig.update_yaxes(title="Número de docentes", dtick=1)
    return style_figure(fig)


def analyze_implementation_distribution(df):
    sessions = numeric_column(df, "CS").round().astype(int)
    median = float(sessions.median())
    maximum = int(sessions.max())
    zero_count = int(sessions.eq(0).sum())
    needs_impulse = int(sessions.le(2).sum())
    concentrated = int(sessions.between(3, 4).sum())
    hallazgo = (
        f"{concentrated} de {len(sessions)} docentes ({concentrated / len(sessions) * 100:.1f}%) se concentran entre 3 y 4 sesiones; "
        f"la mediana es {median:g} y el máximo {maximum}."
    )
    implicacion = (
        f"{needs_impulse} docentes ({needs_impulse / len(sessions) * 100:.1f}%) tienen 2 sesiones o menos, "
        f"incluido{'s' if zero_count != 1 else ''} {zero_count} sin implementación; este grupo concentra el rezago operativo."
    )
    accion = (
        f"priorizar a esos {needs_impulse} docentes para llevarlos a por lo menos 3 sesiones, empezando por quienes registran cero."
    )
    analysis_callout(hallazgo, implicacion, accion)


def accompaniment_lines(df):
    sessions = numeric_column(df, "BO").round().astype(int)
    names = df[excel_column(df, "G")].map(normalize_text)
    treatment_mask = names.isin(TREATMENT_NAMES)
    levels = range(int(sessions.max()) + 1)
    records = []
    for group, values in {
        "Todos los docentes": sessions,
        "Grupo tratamiento": sessions[treatment_mask],
    }.items():
        denominator = len(values)
        counts = values.value_counts()
        for level in levels:
            count = int(counts.get(level, 0))
            records.append(
                {"Sesiones": level, "Grupo": group, "Porcentaje": count / denominator * 100, "n": count}
            )
    line_df = pd.DataFrame(records)
    fig = px.line(
        line_df,
        x="Sesiones",
        y="Porcentaje",
        color="Grupo",
        markers=True,
        custom_data=["n"],
        color_discrete_map={
            "Todos los docentes": COLORS["blue"],
            "Grupo tratamiento": COLORS["orange"],
        },
        title="Frecuencia porcentual de sesiones de acompañamiento",
    )
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=9),
        hovertemplate="%{fullData.name}<br>%{x} sesiones: %{y:.1f}% (n=%{customdata[0]})<extra></extra>",
    )
    fig.update_xaxes(title="Número de sesiones de acompañamiento", dtick=1)
    fig.update_yaxes(title="Porcentaje de docentes", ticksuffix="%", range=[0, 105])
    fig.update_layout(legend_title_text="")
    return style_figure(fig), int(treatment_mask.sum())


def analyze_accompaniment(df):
    sessions = numeric_column(df, "BO").round().astype(int)
    names = df[excel_column(df, "G")].map(normalize_text)
    treatment = sessions[names.isin(TREATMENT_NAMES)]
    general_mean = sessions.mean()
    treatment_mean = treatment.mean()
    target = max(1, int(sessions.max()))
    general_target = sessions.ge(target).mean() * 100
    treatment_target = treatment.ge(target).mean() * 100
    difference = treatment_mean - general_mean
    direction = "por encima" if difference >= 0 else "por debajo"
    hallazgo = (
        f"el grupo tratamiento promedia {treatment_mean:.1f} sesiones frente a {general_mean:.1f} en el total "
        f"({abs(difference):.1f} {direction}); {treatment_target:.1f}% del tratamiento y {general_target:.1f}% del total "
        f"alcanzan {target} sesiones."
    )
    implicacion = (
        "las líneas usan denominadores distintos (10 y 22 docentes), de modo que la comparación válida es porcentual y no por conteos absolutos."
    )
    accion = (
        "concentrar las próximas sesiones en los docentes que aún no alcanzan el nivel máximo observado y revisar semanalmente "
        "si la brecha del grupo tratamiento se amplía o se cierra."
    )
    analysis_callout(hallazgo, implicacion, accion)


def goal_chart(df):
    recognition = recognized_game(df[excel_column(df, "AJ")])
    e2_assembly = numeric_column(df, "AL")
    e2_programming = numeric_column(df, "AS")
    e3 = numeric_column(df, "AZ")
    e4 = numeric_column(df, "BG")
    e5 = numeric_column(df, "BL")
    implemented = recognition | pd.concat(
        [e2_assembly, e2_programming, e3, e4, e5], axis=1
    ).gt(0).any(axis=1)
    completed_e3 = e2_assembly.gt(0) & e2_programming.gt(0) & e3.gt(0)
    total = len(df)
    goal_df = pd.DataFrame(
        {
            "Meta": ["Implementó el juego<br>al menos una vez", "Completó la secuencia<br>hasta el escenario 3"],
            "Indicador": ["Implementación inicial", "Secuencia completa"],
            "n": [int(implemented.sum()), int(completed_e3.sum())],
        }
    )
    goal_df["Porcentaje"] = goal_df["n"] / total * 100
    goal_df["Etiqueta"] = goal_df.apply(lambda row: f"{row['Porcentaje']:.1f}% · n={row['n']}", axis=1)
    fig = px.bar(
        goal_df,
        x="Meta",
        y="Porcentaje",
        color="Indicador",
        text="Etiqueta",
        color_discrete_map={
            "Implementación inicial": COLORS["blue"],
            "Secuencia completa": COLORS["green"],
        },
        title="Cumplimiento de metas de implementación",
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_xaxes(title="Meta de cumplimiento")
    fig.update_yaxes(title="Porcentaje de docentes", ticksuffix="%", range=[0, 110])
    fig.update_layout(legend_title_text="Indicador")
    return style_figure(fig), goal_df


def implementation_heatmap(df):
    values = pd.DataFrame(
        {
            "Escenario 2": numeric_column(df, "AL") + numeric_column(df, "AS"),
            "Escenario 3": numeric_column(df, "AZ"),
            "Escenario 4": numeric_column(df, "BG"),
            "Escenario 5": numeric_column(df, "BL"),
        }
    ).round().astype(int)
    values = values.sort_values(list(values.columns), ascending=False).reset_index(drop=True)
    fig = px.imshow(
        values,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=[
            [0, "#E3F2FD"],
            [0.45, COLORS["blue"]],
            [1, COLORS["blue_dark"]],
        ],
        labels={"x": "Escenario", "y": "Docentes", "color": "Implementaciones"},
        title="Frecuencia de implementación de escenarios por docente",
    )
    fig.update_traces(hovertemplate="%{x}<br>Docente %{y}: %{z} implementaciones<extra></extra>")
    fig.update_yaxes(title="Docentes", showticklabels=False)
    fig.update_xaxes(title="")
    return style_figure(fig, height=max(520, len(values) * 27))


def analyze_goals(goal_df, total):
    implemented = int(goal_df.iloc[0]["n"])
    completed = int(goal_df.iloc[1]["n"])
    gap = implemented - completed
    gap_pp = (gap / total * 100) if total else 0
    hallazgo = (
        f"{implemented} de {total} docentes implementaron al menos una vez, pero solo {completed} completaron la secuencia hasta el escenario 3."
    )
    implicacion = (
        f"existe una brecha de {gap} docentes ({gap_pp:.1f} puntos porcentuales) entre iniciar el juego y alcanzar la secuencia pedagógica esperada."
    )
    accion = (
        "identificar a quienes ya iniciaron pero no completaron armado, programación y escenario 3, y convertir ese grupo en la prioridad operativa."
    )
    analysis_callout(hallazgo, implicacion, accion)


def analyze_heatmap(df):
    scenario_values = pd.DataFrame(
        {
            "Escenario 2": numeric_column(df, "AL") + numeric_column(df, "AS"),
            "Escenario 3": numeric_column(df, "AZ"),
            "Escenario 4": numeric_column(df, "BG"),
            "Escenario 5": numeric_column(df, "BL"),
        }
    )
    active = scenario_values.gt(0).sum()
    weakest = active.idxmin()
    strongest = active.idxmax()
    hallazgo = (
        f"{strongest} tiene la mayor cobertura ({int(active[strongest])} docentes), mientras {weakest} presenta la menor "
        f"({int(active[weakest])} docentes)."
    )
    implicacion = (
        "la pérdida de intensidad hacia los escenarios posteriores permite ubicar el punto de la ruta donde se concentra el rezago, "
        "sin exponer identidades individuales."
    )
    accion = (
        f"orientar el siguiente ciclo de soporte a destrabar {weakest} y usar las celdas claras de cada fila como señal de seguimiento individual."
    )
    analysis_callout(hallazgo, implicacion, accion)


st.title("Biobots 2026")
st.markdown(
    "<p style='font-size:1.15rem;color:#52606d'>Priorice el acompañamiento de docentes con baja implementación y acelere la secuencia hasta el escenario 3.</p>",
    unsafe_allow_html=True,
)

try:
    data = load_consolidado(CONSOLIDADO_URL)
    fig_line, treatment_count = accompaniment_lines(data)
    fig_goal, goals = goal_chart(data)

    implemented_n = int(goals.iloc[0]["n"])
    sequence_n = int(goals.iloc[1]["n"])
    col1, col2, col3 = st.columns(3)
    col1.metric("Docentes participantes", len(data))
    col2.metric("Implementaron al menos una vez", f"{implemented_n} de {len(data)}")
    col3.metric("Completaron hasta escenario 3", f"{sequence_n} de {len(data)}")

    if treatment_count != len(TREATMENT_NAMES):
        st.warning(
            f"Se encontraron {treatment_count} de los {len(TREATMENT_NAMES)} docentes definidos para el grupo tratamiento."
        )

    st.subheader("Implementación y acompañamiento")
    plot(implementation_distribution(data), "biobots_distribution")
    analyze_implementation_distribution(data)
    plot(fig_line, "biobots_accompaniment")
    analyze_accompaniment(data)

    st.subheader("Metas y profundidad de implementación")
    plot(fig_goal, "biobots_goals")
    analyze_goals(goals, len(data))
    plot(implementation_heatmap(data), "biobots_heatmap")
    analyze_heatmap(data)

    st.subheader("Seguimiento de implementación por docente")
    try:
        teacher_data = load_consolidado(TEACHER_TRACKING_URL)

        if "Nombres completos docentes" in teacher_data.columns and "P4" in teacher_data.columns:
            teacher_df = teacher_data.copy()
            teacher_df["Nombres completos docentes"] = clean_teacher_names(
                teacher_df["Nombres completos docentes"]
            )
            teacher_df = teacher_df.dropna(subset=["Nombres completos docentes"])
            teacher_df["P4_numeric"] = pd.to_numeric(
                teacher_df["P4"].astype("string").str.strip(),
                errors="coerce",
            ).fillna(0)

            teacher_totals = (
                teacher_df.groupby("Nombres completos docentes")["P4_numeric"]
                .sum()
                .round()
                .astype(int)
            )

            num_teachers = len(teacher_totals)
            if num_teachers != 10:
                st.info(
                    f"Se encontraron {num_teachers} docentes en los datos. "
                    "El requerimiento esperaba 10 docentes."
                )

            freq_distribution = (
                teacher_totals.value_counts()
                .sort_index()
                .reset_index()
            )
            freq_distribution.columns = ["Sesiones", "Docentes"]

            if not freq_distribution.empty:
                fig_teacher = px.bar(
                    freq_distribution,
                    x="Sesiones",
                    y="Docentes",
                    text="Docentes",
                    color_discrete_sequence=[COLORS["blue"]],
                    title="Frecuencia de implementación del juego por docente (10 docentes)",
                )
                fig_teacher.update_traces(textposition="outside", cliponaxis=False)
                fig_teacher.update_xaxes(title="Número de sesiones de implementación", dtick=1)
                fig_teacher.update_yaxes(title="Número de docentes", dtick=1)
                plot(style_figure(fig_teacher), "biobots_teacher_p4_frequency")

                with st.expander("Ver detalle de sesiones por docente"):
                    teacher_detail = (
                        teacher_totals.sort_values(ascending=False)
                        .reset_index()
                    )
                    teacher_detail.columns = ["Docente", "Total de sesiones"]
                    st.dataframe(
                        teacher_detail,
                        use_container_width=True,
                        hide_index=True,
                    )
            else:
                st.info("No hay datos suficientes para construir la gráfica de frecuencia por docente.")
        else:
            st.warning("Las columnas requeridas ('Nombres completos docentes', 'P4') no se encuentran en la fuente de datos.")

        st.subheader("Docentes únicos por escenario implementado (P6)")
        if "Nombres completos docentes" in teacher_data.columns and "P6" in teacher_data.columns:
            p6_df = teacher_data.copy()
            p6_df["Nombres completos docentes"] = clean_teacher_names(
                p6_df["Nombres completos docentes"]
            )
            p6_df = p6_df.dropna(subset=["Nombres completos docentes"]).copy()
            p6_df["P6_clean"] = p6_df["P6"].map(clean_p6_value)
            p6_df = p6_df.dropna(subset=["P6_clean"]).copy()

            teacher_scenario_records = []
            for _, row in p6_df.iterrows():
                teacher_name = row["Nombres completos docentes"]
                raw_p6 = row["P6"]
                for scenario in extract_scenarios_from_p6(raw_p6):
                    teacher_scenario_records.append(
                        {"Docente": teacher_name, "Escenario": scenario}
                    )

            if teacher_scenario_records:
                teacher_scenario_df = (
                    pd.DataFrame(teacher_scenario_records)
                    .drop_duplicates(subset=["Docente", "Escenario"])
                )
                p6_counts = (
                    teacher_scenario_df.groupby("Escenario", as_index=False)
                    .size()
                    .rename(columns={"size": "Docentes"})
                )
                ordered_scenarios = sorted(
                    p6_counts["Escenario"].tolist(),
                    key=scenario_sort_key,
                )
                p6_counts["Escenario"] = pd.Categorical(
                    p6_counts["Escenario"],
                    categories=ordered_scenarios,
                    ordered=True,
                )
                p6_counts = p6_counts.sort_values("Escenario")

                fig_p6 = px.bar(
                    p6_counts,
                    x="Escenario",
                    y="Docentes",
                    text="Docentes",
                    color_discrete_sequence=[COLORS["blue"]],
                    category_orders={"Escenario": ordered_scenarios},
                    title="Número de docentes únicos que implementaron cada escenario",
                )
                fig_p6.update_traces(textposition="outside", cliponaxis=False)
                fig_p6.update_xaxes(title="Escenarios implementados")
                fig_p6.update_yaxes(title="Número de docentes", dtick=1)
                plot(style_figure(fig_p6), "biobots_teacher_p6_unique_scenarios")

                with st.expander("Ver detalle de docentes únicos por escenario"):
                    st.dataframe(
                        p6_counts,
                        use_container_width=True,
                        hide_index=True,
                    )
            else:
                st.info("No hay escenarios válidos en P6 para construir la gráfica.")
        else:
            st.warning("Las columnas requeridas ('Nombres completos docentes', 'P6') no se encuentran en la fuente de datos.")
    except Exception as teacher_exc:
        st.error("No fue posible cargar los datos de seguimiento de docentes.")
        st.exception(teacher_exc)

    with st.expander("Definiciones y fuente"):
        st.markdown(
            "- **Implementación inicial:** reconocimiento del juego o frecuencia mayor que cero en cualquier escenario.\n"
            "- **Secuencia hasta escenario 3:** armado y programación del escenario 2, y escenario 3, todos con frecuencia mayor que cero.\n"
            "- **Grupo tratamiento:** 10 docentes definidos en el requerimiento. Cada línea usa su propio denominador.\n"
            "- **Fuente:** `Seguimiento_Tutores_2026`, pestaña `Consolidado`, y `BD. Seguimiento Manizales Docentes` (P4/P6). Actualización en caché cada 5 minutos."
        )
except Exception as exc:
    st.error("No fue posible cargar el consolidado de Biobots.")
    st.exception(exc)

st.markdown("---")
st.markdown(FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64), unsafe_allow_html=True)
