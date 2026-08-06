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
SURVEY_SHEET_ID = "1Vm8uucHPZxwu2PMUx7sh7Tb4QsyVpUS5"
SURVEY_GID = "741262261"
SURVEY_URL = (
    f"https://docs.google.com/spreadsheets/d/{SURVEY_SHEET_ID}/export?format=csv&gid={SURVEY_GID}"
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
    "orange_dark": "#CC6600",
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


@st.cache_data(ttl=300)
def load_sheet_with_manual_header(url):
    safe_url = urllib.parse.quote(url, safe=":/?=&")
    raw = pd.read_csv(safe_url, header=None)
    if raw.empty or len(raw) < 3:
        raise ValueError("La fuente no tiene suficientes filas para aplicar encabezado y limpieza.")
    headers = raw.iloc[0].astype("string").str.strip()
    df = raw.iloc[1:].copy()
    df.columns = headers
    # Se elimina la fila 1 original, como fue solicitado.
    df = df.iloc[1:].reset_index(drop=True)
    df.columns = pd.Index([str(column).strip() for column in df.columns])
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


def item_label(column_name, prefix):
    label = str(column_name).strip()
    if label.startswith(prefix):
        label = label[len(prefix) :]
    label = label.lstrip("_-: ").replace("_", " ").strip()
    return label if label else str(column_name).strip()


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
    sessions = numeric_column(df, "CN").round().astype(int)
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
    sessions = numeric_column(df, "CN").round().astype(int)
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


def q11_stacked_chart(df):
    cols_q11 = [column for column in df.columns if str(column).startswith("Q11_")]
    if not cols_q11:
        return None

    orden_escala = [
        "Totalmente en desacuerdo",
        "En desacuerdo",
        "Neutra",
        "De acuerdo",
        "Totalmente de acuerdo",
    ]
    escala_lookup = {
        "totalmente en desacuerdo": "Totalmente en desacuerdo",
        "en desacuerdo": "En desacuerdo",
        "desacuerdo": "En desacuerdo",
        "neutra": "Neutra",
        "neutro": "Neutra",
        "neutral": "Neutra",
        "de acuerdo": "De acuerdo",
        "acuerdo": "De acuerdo",
        "totalmente de acuerdo": "Totalmente de acuerdo",
    }
    ordered_items = [str(column) for column in cols_q11]

    records = []
    for column in cols_q11:
        item = str(column)
        normalized = df[column].map(normalize_text)
        mapped = normalized.map(escala_lookup)
        valid = mapped.dropna()
        denominator = int(valid.shape[0])
        counts = valid.value_counts()
        for level in orden_escala:
            count = int(counts.get(level, 0))
            percentage = (count / denominator * 100) if denominator else 0
            records.append(
                {
                    "Item": item,
                    "Nivel": level,
                    "Porcentaje": percentage,
                    "n": count,
                    "denominador": denominator,
                }
            )

    chart_df = pd.DataFrame(records)
    fig = px.bar(
        chart_df,
        x="Porcentaje",
        y="Item",
        color="Nivel",
        orientation="h",
        category_orders={"Nivel": orden_escala, "Item": list(reversed(ordered_items))},
        color_discrete_map={
            "Totalmente en desacuerdo": COLORS["orange_dark"],
            "En desacuerdo": COLORS["orange"],
            "Neutra": COLORS["blue_dark"],
            "De acuerdo": COLORS["blue"],
            "Totalmente de acuerdo": COLORS["green"],
        },
        custom_data=["n", "denominador"],
        title="Q11: Afirmaciones relacionadas con la formación, los materiales y el acompañamiento",
    )
    fig.update_layout(barmode="stack", legend_title_text="")
    fig.update_traces(
        hovertemplate="%{y}<br>%{fullData.name}: %{x:.1f}% (n=%{customdata[0]}/%{customdata[1]})<extra></extra>",
    )
    pivot_q11 = (
        chart_df.pivot(index="Item", columns="Nivel", values="Porcentaje")
        .reindex(index=ordered_items, columns=orden_escala)
        .fillna(0)
    )
    for item in ordered_items:
        accumulated = 0.0
        for level in orden_escala:
            value = float(pivot_q11.loc[item, level])
            if value <= 0:
                continue
            fig.add_annotation(
                x=accumulated + value / 2,
                y=item,
                text=f"{value:.1f}%",
                showarrow=False,
                font=dict(size=10, color=COLORS["text_dark"]),
                bgcolor="rgba(255,255,255,0.82)",
                bordercolor="rgba(44,62,80,0.25)",
                borderwidth=1,
                borderpad=2,
            )
            accumulated += value
    fig.update_xaxes(title="Porcentaje de docentes según nivel marcado", ticksuffix="%", range=[0, 100])
    fig.update_yaxes(title="Items")
    return style_figure(fig, height=max(430, len(ordered_items) * 46))


def q20_stacked_chart(df):
    cols_q20 = [column for column in ["Q20_1", "Q20_2", "Q20_3"] if column in df.columns]
    if not cols_q20:
        return None

    # Orden semantico: de menor a mayor dificultad; "No aplica" queda al final.
    orden_escala = ["Muy Facil", "Facil", "Moderada", "Dificil", "Muy dificil", "No aplica"]
    escala_aliases = {
        "dificil": "Dificil",
        "difícil": "Dificil",
        "facil": "Facil",
        "fácil": "Facil",
        "moderada": "Moderada",
        "muy facil": "Muy Facil",
        "muy fácil": "Muy Facil",
        "muy dificil": "Muy dificil",
        "muy difícil": "Muy dificil",
        "no aplica": "No aplica",
    }
    item_labels = {
        "Q20_1": "Del escenario 2 al 3",
        "Q20_2": "Del escenario 3 al 4",
        "Q20_3": "Del escenario 4 al 5",
    }
    ordered_items = [item_labels.get(str(column), str(column)) for column in cols_q20]

    records = []
    for column in cols_q20:
        item = item_labels.get(str(column), str(column))
        normalized = df[column].map(normalize_text)
        mapped = normalized.map(escala_aliases)
        valid = mapped.dropna()
        denominator = int(valid.shape[0])
        counts = valid.value_counts()
        for level in orden_escala:
            count = int(counts.get(level, 0))
            percentage = (count / denominator * 100) if denominator else 0
            records.append(
                {
                    "Item": item,
                    "Nivel": level,
                    "Porcentaje": percentage,
                    "n": count,
                    "denominador": denominator,
                }
            )

    chart_df = pd.DataFrame(records)
    fig = px.bar(
        chart_df,
        x="Porcentaje",
        y="Item",
        color="Nivel",
        orientation="h",
        category_orders={"Nivel": orden_escala, "Item": ordered_items},
        color_discrete_map={
            "Dificil": COLORS["orange"],
            "Muy dificil": COLORS["orange_dark"],
            "Moderada": COLORS["blue_dark"],
            "Facil": COLORS["blue"],
            "Muy Facil": COLORS["green"],
            "No aplica": COLORS["muted"],
        },
        custom_data=["n", "denominador"],
        title="Q20: ¿Qué tan difícil fue la transición entre un escenario y el siguiente?",
    )
    fig.update_layout(barmode="stack", legend_title_text="")
    fig.update_traces(
        hovertemplate="%{y}<br>%{fullData.name}: %{x:.1f}% (n=%{customdata[0]}/%{customdata[1]})<extra></extra>",
    )
    pivot_q20 = (
        chart_df.pivot(index="Item", columns="Nivel", values="Porcentaje")
        .reindex(index=ordered_items, columns=orden_escala)
        .fillna(0)
    )
    for item in ordered_items:
        accumulated = 0.0
        for level in orden_escala:
            value = float(pivot_q20.loc[item, level])
            if value <= 0:
                continue
            fig.add_annotation(
                x=accumulated + value / 2,
                y=item,
                text=f"{value:.1f}%",
                showarrow=False,
                font=dict(size=10, color=COLORS["text_dark"]),
                bgcolor="rgba(255,255,255,0.82)",
                bordercolor="rgba(44,62,80,0.25)",
                borderwidth=1,
                borderpad=2,
            )
            accumulated += value
    fig.update_xaxes(title="Porcentaje de docentes según nivel marcado", ticksuffix="%", range=[0, 100])
    fig.update_yaxes(title="Items", categoryorder="array", categoryarray=ordered_items, autorange="reversed")
    return style_figure(fig, height=460)


def q25_stacked_chart(df):
    cols_q25 = [column for column in [f"Q25_{index}" for index in range(1, 8)] if column in df.columns]
    if not cols_q25:
        return None

    orden_escala = [
        "Totalmente en desacuerdo",
        "En desacuerdo",
        "Neutro",
        "De acuerdo",
        "Totalmente de acuerdo",
    ]
    escala_aliases = {
        "totalmente en desacuerdo": "Totalmente en desacuerdo",
        "en desacuerdo": "En desacuerdo",
        "desacuerdo": "En desacuerdo",
        "neutro": "Neutro",
        "neutra": "Neutro",
        "neutral": "Neutro",
        "de acuerdo": "De acuerdo",
        "acuerdo": "De acuerdo",
        "totalmente de acuerdo": "Totalmente de acuerdo",
    }
    ordered_items = [str(column) for column in cols_q25]

    records = []
    for column in cols_q25:
        item = str(column)
        normalized = df[column].map(normalize_text)
        mapped = normalized.map(escala_aliases)
        valid = mapped.dropna()
        denominator = int(valid.shape[0])
        counts = valid.value_counts()
        for level in orden_escala:
            count = int(counts.get(level, 0))
            percentage = (count / denominator * 100) if denominator else 0
            records.append(
                {
                    "Item": item,
                    "Nivel": level,
                    "Porcentaje": percentage,
                    "n": count,
                    "denominador": denominator,
                }
            )

    chart_df = pd.DataFrame(records)
    fig = px.bar(
        chart_df,
        x="Porcentaje",
        y="Item",
        color="Nivel",
        orientation="h",
        category_orders={"Nivel": orden_escala, "Item": list(reversed(ordered_items))},
        color_discrete_map={
            "Totalmente en desacuerdo": COLORS["orange_dark"],
            "En desacuerdo": COLORS["orange"],
            "Neutro": COLORS["blue_dark"],
            "De acuerdo": COLORS["blue"],
            "Totalmente de acuerdo": COLORS["green"],
        },
        custom_data=["n", "denominador"],
        title="Q25: Gráfica de percepciones sobre la implementación",
    )
    fig.update_layout(barmode="stack", legend_title_text="")
    fig.update_traces(
        hovertemplate="%{y}<br>%{fullData.name}: %{x:.1f}% (n=%{customdata[0]}/%{customdata[1]})<extra></extra>"
    )
    pivot_q25 = (
        chart_df.pivot(index="Item", columns="Nivel", values="Porcentaje")
        .reindex(index=ordered_items, columns=orden_escala)
        .fillna(0)
    )
    for item in ordered_items:
        accumulated = 0.0
        for level in orden_escala:
            value = float(pivot_q25.loc[item, level])
            if value <= 0:
                continue
            fig.add_annotation(
                x=accumulated + value / 2,
                y=item,
                text=f"{value:.1f}%",
                showarrow=False,
                font=dict(size=10, color=COLORS["text_dark"]),
                bgcolor="rgba(255,255,255,0.82)",
                bordercolor="rgba(44,62,80,0.25)",
                borderwidth=1,
                borderpad=2,
            )
            accumulated += value
    fig.update_xaxes(title="Porcentaje de docentes según nivel marcado", ticksuffix="%", range=[0, 100])
    fig.update_yaxes(title="Items")
    return style_figure(fig, height=max(430, len(ordered_items) * 46))


def marked_option(series):
    normalized = series.map(normalize_text)
    numeric_marked = pd.to_numeric(series, errors="coerce").gt(0).fillna(False)
    explicit_marked = normalized.isin(
        {"si", "sí", "yes", "true", "1", "x", "seleccionado", "checked", "marcada"}
    ).fillna(False)
    explicit_unmarked = normalized.isin(
        {"", "nan", "na", "n/a", "none", "-", "0", "no", "false", "null"}
    ).fillna(False)
    # En multirrespuesta de hojas de cálculo, una celda con texto suele significar opción marcada.
    text_present = normalized.ne("").fillna(False) & ~explicit_unmarked
    return numeric_marked | explicit_marked | text_present


Q18_LABELS = {
    "Q18_1": "Manejo del tiempo durante las sesiones",
    "Q18_6": "Gestión del aula durante la actividad",
    "Q18_7": "Acceso o disponibilidad de materiales",
    "Q18_9": "Dificultades socioemocionales de los estudiantes",
    "Q18_12": "Dificultades de atención y concentración de los estudiantes",
    "Q18_13": "Falta de tiempo disponible en el horario escolar",
    "Q18_14": "Otro",
    "Q18_15": "Ninguna",
}


def q18_column_sort_key(column_name):
    match = re.search(r"Q18_(\d+)$", str(column_name))
    if match:
        return int(match.group(1))
    return 999


def q18_label(column_name):
    code = str(column_name)
    if code in Q18_LABELS:
        return Q18_LABELS[code]
    # Si no hay mapeo explícito, conservamos el código para evitar etiquetas incorrectas.
    return code


def q18_frequency_chart(df):
    cols_q18 = sorted(
        [
            column
            for column in df.columns
            if str(column).startswith("Q18_") and not str(column).endswith("_TEXT")
        ],
        key=q18_column_sort_key,
    )
    if not cols_q18:
        return None, pd.DataFrame(columns=["Respuesta reportada", "Docentes"])

    valid_mask = pd.DataFrame({column: marked_option(df[column]) for column in cols_q18}).any(axis=1)
    denominator = int(valid_mask.sum())
    if denominator == 0:
        return None, pd.DataFrame(columns=["Respuesta reportada", "Docentes"])

    records = []
    for column in cols_q18:
        item = q18_label(column)
        count = int((marked_option(df[column]) & valid_mask).sum())
        if count == 0:
            continue
        percentage = count / denominator * 100
        records.append({"Item": item, "Porcentaje": percentage, "n": count})

    if not records:
        return None, pd.DataFrame(columns=["Respuesta reportada", "Docentes"])

    chart_df = pd.DataFrame(records).sort_values("Porcentaje", ascending=True)
    chart_df["Etiqueta"] = chart_df.apply(
        lambda row: f"{row['Porcentaje']:.1f}% · n={int(row['n'])}",
        axis=1,
    )
    fig = go.Figure()
    for _, row in chart_df.iterrows():
        fig.add_shape(
            type="line",
            x0=0,
            x1=float(row["Porcentaje"]),
            y0=row["Item"],
            y1=row["Item"],
            xref="x",
            yref="y",
            line=dict(color=COLORS["muted"], width=10),
            layer="below",
        )
    fig.add_trace(
        go.Scatter(
            x=chart_df["Porcentaje"],
            y=chart_df["Item"],
            mode="markers+text",
            text=chart_df["Etiqueta"],
            textposition="middle right",
            marker=dict(color=COLORS["blue"], size=13, line=dict(color="white", width=1)),
            customdata=chart_df[["n"]],
            hovertemplate="%{y}<br>%{x:.1f}% (n=%{customdata[0]})<extra></extra>",
            showlegend=False,
        )
    )
    fig.update_layout(
        title="Q18: ¿Qué factores dificultaron su avance en la implementación de escenarios del juego?"
    )
    fig.update_xaxes(
        title="Porcentaje de docentes",
        ticksuffix="%",
        range=[0, 100],
        showgrid=True,
        gridcolor="#E9EFF5",
    )
    fig.update_yaxes(title="Items")
    other_responses_df = pd.DataFrame(columns=["Respuesta reportada", "Docentes"])
    if "Q18_14" in cols_q18 and "Q18_14_TEXT" in df.columns:
        other_mask = marked_option(df["Q18_14"]) & valid_mask
        other_series = (
            df.loc[other_mask, "Q18_14_TEXT"]
            .astype("string")
            .str.strip()
            .replace({"": pd.NA, "nan": pd.NA, "NaN": pd.NA})
            .dropna()
        )
        if not other_series.empty:
            other_responses_df = (
                other_series.value_counts()
                .rename_axis("Respuesta reportada")
                .reset_index(name="Docentes")
            )
    return style_figure(fig, height=max(430, len(chart_df) * 42)), other_responses_df


st.title("Biobots 2026")
st.markdown(
    "<p style='font-size:1.15rem;color:#52606d'>Priorice el acompañamiento de docentes con baja implementación y acelere la secuencia hasta el escenario 3.</p>",
    unsafe_allow_html=True,
)

try:
    data = load_consolidado(CONSOLIDADO_URL)
    fig_line, treatment_count = accompaniment_lines(data)
    fig_goal, goals = goal_chart(data)
    perception_df = load_sheet_with_manual_header(SURVEY_URL)
    fig_q11 = q11_stacked_chart(perception_df)
    fig_q20 = q20_stacked_chart(perception_df)
    fig_q25 = q25_stacked_chart(perception_df)
    fig_q18, q18_other_responses = q18_frequency_chart(perception_df)

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

    st.subheader("Percepción sobre formación y barreras")
    if fig_q11 is not None:
        plot(fig_q11, "biobots_q11_stacked")
    else:
        st.info("No se encontraron columnas `Q11_*` en la fuente para construir la gráfica Q11.")
    if fig_q18 is not None:
        plot(fig_q18, "biobots_q18_frequency")
        if not q18_other_responses.empty:
            with st.expander("Ver respuestas abiertas de la opción 'Otro' (Q18_14_TEXT)"):
                st.dataframe(
                    q18_other_responses,
                    use_container_width=True,
                    hide_index=True,
                )
    else:
        st.info("No se encontraron columnas `Q18_*` en la fuente para construir la gráfica Q18.")
    if fig_q20 is not None:
        plot(fig_q20, "biobots_q20_stacked")
    else:
        st.info("No se encontraron columnas `Q20_1`, `Q20_2` y `Q20_3` para construir la gráfica Q20.")
    if fig_q25 is not None:
        plot(fig_q25, "biobots_q25_stacked")
    else:
        st.info("No se encontraron columnas `Q25_1` a `Q25_7` para construir la gráfica Q25.")

    with st.expander("Definiciones y fuente"):
        st.markdown(
            "- **Implementación inicial:** reconocimiento del juego o frecuencia mayor que cero en cualquier escenario.\n"
            "- **Secuencia hasta escenario 3:** armado y programación del escenario 2, y escenario 3, todos con frecuencia mayor que cero.\n"
            "- **Grupo tratamiento:** 10 docentes definidos en el requerimiento. Cada línea usa su propio denominador.\n"
            "- **Fuente:** `Seguimiento_Tutores_2026`, pestaña `Consolidado`; `BD. Seguimiento Manizales Docentes` (P4/P6); y hoja de encuesta (`gid=741262261`) para Q11, Q18, Q20 y Q25. Actualización en caché cada 5 minutos."
        )
except Exception as exc:
    st.error("No fue posible cargar el consolidado de Biobots.")
    st.exception(exc)

st.markdown("---")
st.markdown(FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64), unsafe_allow_html=True)
