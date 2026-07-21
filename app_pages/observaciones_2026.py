"""Dashboard de observaciones de aula 2026 basado en el instrumento Biobots."""

import unicodedata
import urllib.parse

import pandas as pd
import plotly.express as px
import streamlit as st

from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import header
from utils.chart_config import get_chart_config


header("#282255")
CHART_CONFIG = get_chart_config()
SOURCE_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1iDpfEdvasjYuCqMZ9tlY0a5XOEjbF5qK/export?format=csv"
)

COLORS = {
    "blue": "#83C9FF",
    "blue_dark": "#0068C9",
    "purple": "#662482",
    "pink": "#e5007e",
    "deep_blue": "#23085a",
    "gray": "#A8B2BD",
    "light": "#EAF4FB",
    "text": "#2C3E50",
}

CONNECTION_COLORS = {
    "Sí, explícita": COLORS["blue_dark"],
    "Implícita o superficial": COLORS["pink"],
    "No": COLORS["gray"],
}


@st.cache_data(ttl=300)
def load_data(url):
    safe_url = urllib.parse.quote(url, safe=":/?=&")
    data = pd.read_csv(safe_url)
    data.columns = data.columns.str.strip()
    return data


def column(data, index):
    if index >= len(data.columns):
        raise KeyError(f"La fuente no contiene la columna esperada en la posición {index + 1}.")
    return data.iloc[:, index]


def normalize(value):
    text = unicodedata.normalize("NFKD", str(value))
    return " ".join(
        "".join(char for char in text if not unicodedata.combining(char))
        .lower()
        .strip()
        .split()
    )


def is_yes(series):
    return series.map(normalize).isin({"si", "sí", "yes", "true", "verdadero"})


def style_figure(fig, height=410):
    fig.update_layout(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial", color=COLORS["text"]),
        title=dict(font=dict(size=20, color=COLORS["deep_blue"]), x=0),
        margin=dict(l=45, r=25, t=80, b=45),
        hoverlabel=dict(bgcolor="white"),
        legend_title_text="",
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="#E8EEF3", zeroline=False)
    return fig


def plot(fig, key):
    st.plotly_chart(fig, width="stretch", config=CHART_CONFIG, key=key)


def percent_bar(labels, values, title, highlight=None):
    chart = pd.DataFrame({"Indicador": labels, "Porcentaje": values})
    chart["Etiqueta"] = chart["Porcentaje"].map(lambda value: f"{value:.1f}%")
    colors = [
        COLORS["pink"] if label == highlight else COLORS["blue_dark"]
        for label in chart["Indicador"]
    ]
    fig = px.bar(
        chart,
        x="Porcentaje",
        y="Indicador",
        orientation="h",
        text="Etiqueta",
        title=title,
    )
    fig.update_traces(marker_color=colors, textposition="outside", cliponaxis=False)
    fig.update_xaxes(title="Porcentaje de observaciones", ticksuffix="%", range=[0, 108])
    fig.update_yaxes(title="", categoryorder="array", categoryarray=labels[::-1])
    return style_figure(fig)


def multiselect_percent(data, indices, labels):
    total = len(data)
    values = []
    for index in indices:
        series = column(data, index)
        selected = series.notna() & ~series.map(normalize).isin({"", "0", "false", "no", "nan"})
        values.append(selected.sum() / total * 100 if total else 0)
    return labels, values


def insight_box(hallazgo, implicacion, accion):
    st.markdown(
        f"""
        <div style="background:#F5F9FC;border-left:5px solid {COLORS['pink']};
                    padding:15px 18px;margin:8px 0 24px;border-radius:0 8px 8px 0;color:{COLORS['text']}">
            <strong>Lectura para la acción</strong><br>
            <strong>Hallazgo:</strong> {hallazgo}<br>
            <strong>Implicación:</strong> {implicacion}<br>
            <strong>Acción:</strong> {accion}
        </div>
        """,
        unsafe_allow_html=True,
    )


st.title("Observaciones de aula 2026")
st.markdown(
    "<p style='font-size:1.12rem;color:#52606D'>Fortalecer el cierre pedagógico para convertir la experiencia con Biobots en aprendizaje explícito de pensamiento computacional.</p>",
    unsafe_allow_html=True,
)

try:
    data = load_data(SOURCE_URL)
    total = len(data)
    boys = pd.to_numeric(column(data, 11), errors="coerce").fillna(0).sum()
    girls = pd.to_numeric(column(data, 12), errors="coerce").fillna(0).sum()
    students = int(boys + girls)
    explicit = column(data, 122).map(normalize).eq("si").sum()
    explicit_pct = explicit / total * 100 if total else 0
    equal_roles = column(data, 65).map(normalize).str.contains("participaron por igual", na=False).sum()

    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("Observaciones", total)
    metric2.metric("Estudiantes observados", students)
    metric3.metric("Participación equitativa", f"{equal_roles / total * 100:.1f}%" if total else "0%")
    metric4.metric("Cierre explícito en PC", f"{explicit_pct:.1f}%")

    superficial = column(data, 122).map(normalize).str.contains("implicita|superficial", regex=True).sum()
    no_connection = column(data, 122).map(normalize).eq("no").sum()
    insight_box(
        f"solo {explicit} de {total} sesiones ({explicit_pct:.1f}%) cerraron con una conexión explícita al pensamiento computacional.",
        f"en {superficial} sesiones la conexión fue superficial y en {no_connection} no se realizó; la experiencia puede quedarse en el juego sin hacer visible el aprendizaje.",
        "incorporar una rutina breve de cierre con preguntas de reflexión, explicación del algoritmo y revisión de errores en cada sesión.",
    )

    tab_before, tab_during, tab_after = st.tabs(
        ["Antes de jugar", "Durante el juego", "Después del juego"]
    )

    with tab_before:
        scenario = column(data, 34).fillna("Sin información").astype(str)
        scenario_df = scenario.value_counts().rename_axis("Escenario").reset_index(name="Observaciones")
        scenario_df["Porcentaje"] = scenario_df["Observaciones"] / total * 100
        fig = px.bar(
            scenario_df,
            x="Escenario",
            y="Observaciones",
            text="Observaciones",
            color_discrete_sequence=[COLORS["blue_dark"]],
            title="El escenario 2 concentra la mayoría de las observaciones",
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_xaxes(title="")
        fig.update_yaxes(title="Número de observaciones", dtick=1)
        plot(style_figure(fig), "obs2026_scenarios")

        support_labels = [
            "Guía de inicio",
            "Guía pedagógica",
            "Libro de escenarios",
            "Manual de algoritmos",
            "Librillo de mapas",
            "Afiche de apoyo",
        ]
        support_indices = [71, 73, 75, 77, 84, 86]
        support_values = []
        for index in support_indices:
            normalized = column(data, index).map(normalize)
            if index == 77:
                used = ~normalized.str.contains("no uso", na=False)
            else:
                used = normalized.eq("si")
            support_values.append(used.sum() / total * 100)
        plot(
            percent_bar(
                support_labels,
                support_values,
                "Los materiales pedagógicos de apoyo se usan poco",
                highlight="Afiche de apoyo",
            ),
            "obs2026_support",
        )

    with tab_during:
        doubt_labels, doubt_values = multiselect_percent(
            data,
            [97, 98, 99, 100, 101],
            [
                "Reglas del juego",
                "Uso de materiales",
                "Lenguaje o vocabulario",
                "Secuencia del juego",
                "Sin dudas significativas",
            ],
        )
        plot(
            percent_bar(
                doubt_labels,
                doubt_values,
                "Las reglas son la principal fuente de dudas durante el juego",
                highlight="Reglas del juego",
            ),
            "obs2026_doubts",
        )

        monitoring_labels = [
            "Se desplaza para monitorear",
            "Aclara dudas en los grupos",
            "Motiva a identificar errores",
            "Realiza depuración con estudiantes",
        ]
        monitoring_values = [
            column(data, index).map(normalize).eq("siempre").sum() / total * 100
            for index in [115, 116, 117, 118]
        ]
        plot(
            percent_bar(
                monitoring_labels,
                monitoring_values,
                "El acompañamiento docente se observa de forma consistente",
            ),
            "obs2026_monitoring",
        )

    with tab_after:
        connection = column(data, 122).map(normalize).map(
            {
                "si": "Sí, explícita",
                "de forma implicita o superficial": "Implícita o superficial",
                "no": "No",
            }
        ).fillna("Sin información")
        connection_df = connection.value_counts().rename_axis("Conexión").reset_index(name="Observaciones")
        connection_df["Porcentaje"] = connection_df["Observaciones"] / total * 100
        connection_df["Etiqueta"] = connection_df.apply(
            lambda row: f"{row['Porcentaje']:.1f}% · n={row['Observaciones']}", axis=1
        )
        fig = px.bar(
            connection_df,
            x="Conexión",
            y="Porcentaje",
            color="Conexión",
            text="Etiqueta",
            color_discrete_map=CONNECTION_COLORS,
            title="El cierre rara vez hace explícito el pensamiento computacional",
            category_orders={"Conexión": ["Sí, explícita", "Implícita o superficial", "No"]},
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_xaxes(title="")
        fig.update_yaxes(title="Porcentaje de observaciones", ticksuffix="%", range=[0, 108])
        plot(style_figure(fig), "obs2026_connection")

        close_labels, close_values = multiselect_percent(
            data,
            [124, 125, 126, 127],
            [
                "Reflexión grupal",
                "Retroalimentación individual",
                "Metacognición",
                "Sin actividad de cierre",
            ],
        )
        plot(
            percent_bar(
                close_labels,
                close_values,
                "La reflexión grupal domina; la metacognición aún es limitada",
                highlight="Sin actividad de cierre",
            ),
            "obs2026_closure",
        )

    with st.expander("Ver datos y definiciones"):
        st.markdown(
            "- Los porcentajes usan como denominador las observaciones visibles en la fuente.\n"
            "- Las preguntas de selección múltiple pueden sumar más de 100%.\n"
            "- **Cierre explícito en PC:** respuesta ‘Sí’ a la conexión con habilidades de pensamiento computacional.\n"
            "- La fuente se actualiza automáticamente cada cinco minutos."
        )
        st.dataframe(data, width="stretch")

except Exception as exc:
    st.error("No fue posible cargar la fuente de observaciones 2026.")
    st.info("Verifique que el archivo continúe compartido y permita la exportación pública.")
    st.exception(exc)

st.markdown("---")
st.markdown(FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64), unsafe_allow_html=True)
