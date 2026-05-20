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

RURAL_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSV5EzdlBEDHngwEQtfM6L3ilW0Bj8oMtXB1ndPB5GNszQoYJjRKcS4utBO9akNQuxv_Fgj8V7SH9rp/pub?gid=1811707145&single=true&output=csv"


@st.cache_data(ttl=300)
def load_data(file):
    if isinstance(file, str) and file.startswith("http"):
        file = urllib.parse.quote(file, safe=":/?=&")
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    return df


def _plot_chart(container, fig, key):
    container.plotly_chart(
        fig,
        key=key,
        use_container_width=True,
        config=chart_config,
    )


def dashboard_seguimiento_region(df, region_name: str, key_suffix=""):
    df = df.replace({"": None, "NA": None, "na": None})

    if "Fecha_llamada" in df.columns:
        df["Fecha_llamada"] = pd.to_datetime(
            df["Fecha_llamada"], errors="coerce", format="%d/%m/%y"
        )
    if "P1" in df.columns:
        df["P1"] = df["P1"].astype("string").str.strip()
    if "P4" in df.columns:
        df["P4"] = pd.to_numeric(df["P4"], errors="coerce")
    if "P5" in df.columns:
        df["P5"] = pd.to_numeric(df["P5"], errors="coerce")

    total_calls = len(df)
    total_docentes = (
        df["Nombres completos docentes"].nunique()
        if "Nombres completos docentes" in df.columns
        else 0
    )
    total_sesiones = int(df["P4"].dropna().sum()) if "P4" in df.columns else 0
    promedio_sesiones = df["P5"].dropna().mean() if "P5" in df.columns else 0

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

    if "P6" in df.columns:
        p6_counts = df["P6"].dropna()
        if not p6_counts.empty:
            escenarios = []
            for val in p6_counts:
                nums = re.findall(r"\d+", str(val))
                if nums:
                    escenarios.extend([f"Escenario {n}" for n in nums])
                else:
                    escenarios.append("Otro")
            top_escenarios = pd.Series(escenarios).value_counts().head(5).index.tolist()
            resumen.append(
                "Los escenarios con mayor número de implementaciones fueron: "
                f"{', '.join(top_escenarios)}. (Incluye repasos)"
            )

    if "P8" in df.columns:
        p8_respuestas = df["P8"].astype("string").str.strip().dropna()
        if not p8_respuestas.empty:
            resumen.append(
                f"Se identificaron **{len(p8_respuestas)} respuestas** en P8 sobre "
                "dificultades al usar el juego con los estudiantes."
            )
        else:
            resumen.append(
                "No se reportaron respuestas en P8 sobre dificultades en el uso del juego."
            )

    if "P10" in df.columns:
        p10_respuestas = df["P10"].astype("string").str.strip().dropna()
        if not p10_respuestas.empty:
            resumen.append(
                f"Se registraron **{len(p10_respuestas)} respuestas** en P10 sobre "
                "fortalezas o resultados positivos del juego."
            )

    for punto in resumen:
        st.markdown(f"- {punto}")

    st.markdown("---")

    if (
        "P1" in df.columns
        and "Nombres completos docentes" in df.columns
        and "Fecha_llamada" in df.columns
    ):
        st.subheader("P1. ¿Esta semana ha utilizado el juego Biobots con los estudiantes?")

        df_sorted = df.dropna(subset=["Fecha_llamada"]).sort_values(
            ["Nombres completos docentes", "Fecha_llamada"]
        )
        df_sorted["Semana"] = df_sorted["Fecha_llamada"].dt.isocalendar().week
        p1_time = (
            df_sorted.groupby(["Semana", "P1", "Fecha_llamada"])
            .size()
            .reset_index(name="Frecuencia")
        )
        p1_time["Fecha_llamada"] = p1_time["Fecha_llamada"].dt.strftime("%d/%m/%Y")

        fig_p1_time = px.bar(
            p1_time,
            x="Semana",
            y="Frecuencia",
            text="Frecuencia",
            hover_data=["Fecha_llamada"],
            color="P1",
            title="Frecuencia semanal de implementación",
            height=500,
        )
        _plot_chart(st, fig_p1_time, f"fig_p1_{key_suffix}")

    col1, col2 = st.columns(2)
    col1.subheader("P2. ¿Podría compartir la razón por la que no ha podido implementarlo?")
    col2.subheader("P5. En promedio, ¿cuánto tiempo tardó cada sesión de juego?")

    if "P2" in df.columns:
        if "Razones P2" in df.columns:
            p2_counts = (
                df["Razones P2"]
                .astype("string")
                .str.strip()
                .dropna()
                .value_counts()
                .reset_index()
            )
            p2_counts.columns = ["Razón", "Cuenta"]
        else:
            p2_counts = df["P2"].value_counts(dropna=True).reset_index()
            p2_counts.columns = ["Razón", "Cuenta"]

        col1.dataframe(p2_counts, use_container_width=True, hide_index=True)

    if "P5" in df.columns:
        p5_counts = df["P5"].dropna().reset_index(drop=True)
        p5_counts.name = "Duración (minutos)"

        fig_p5 = px.histogram(
            p5_counts,
            x="Duración (minutos)",
            nbins=10,
            text_auto=True,
            title="Distribución de duración",
            labels={"count": "Frecuencia"},
        )
        fig_p5.update_layout(yaxis_title="Frecuencia")
        _plot_chart(col2, fig_p5, f"fig_p5_{key_suffix}")

    if "P3" in df.columns:
        st.subheader("P3. ¿Con qué grados ha utilizado el juego?")

        grados = []
        for value in df["P3"].dropna():
            partes = re.split(r",| y |/|;", str(value))
            grados.extend([parte.strip() for parte in partes if parte.strip()])

        if grados:
            p3_counts = (
                pd.Series(grados)
                .value_counts()
                .reset_index()
            )
            p3_counts.columns = ["Grado", "Frecuencia"]

            fig_p3 = px.bar(
                p3_counts,
                x="Grado",
                y="Frecuencia",
                text="Frecuencia",
                title="Grados con los que se ha utilizado el juego",
            )
            _plot_chart(st, fig_p3, f"fig_p3_{key_suffix}")
        else:
            st.info("No hay respuestas registradas para P3.")

    if (
        "P4" in df.columns
        and "Nombres completos docentes" in df.columns
        and "Fecha_llamada" in df.columns
    ):
        st.subheader("P4. ¿Cuántas veces por semana ha utilizado el juego?")

        p4_df = df.dropna(
            subset=["P4", "Nombres completos docentes", "Fecha_llamada"]
        ).copy()

        if not p4_df.empty:
            iso = p4_df["Fecha_llamada"].dt.isocalendar().copy()
            p4_df.loc[:, "Año"] = iso.year
            p4_df.loc[:, "Semana"] = iso.week
            p4_df.loc[:, "Fecha_inicio"] = pd.to_datetime(
                p4_df["Año"].astype(str) + "-W" + p4_df["Semana"].astype(str) + "-1",
                format="%G-W%V-%u",
            )
            p4_df.loc[:, "Fecha_fin"] = p4_df["Fecha_inicio"] + pd.Timedelta(days=6)

            plot_df = p4_df[
                [
                    "Nombres completos docentes",
                    "Fecha_inicio",
                    "Fecha_fin",
                    "P4",
                    "Semana",
                ]
            ].copy()
            plot_df.loc[:, "P4_str"] = plot_df["P4"].astype(int).astype(str)

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

            min_week = plot_df["Semana"].min()
            week_ticks = (
                plot_df.groupby("Semana")[["Fecha_inicio", "Fecha_fin"]]
                .first()
                .assign(
                    mid=lambda d: d["Fecha_inicio"]
                    + (d["Fecha_fin"] - d["Fecha_inicio"]) / 2,
                    relative=lambda d: d.index - min_week + 1,
                )
            )

            fig_timeline.update_layout(
                xaxis=dict(
                    title="Semana de implementación",
                    tickmode="array",
                    tickvals=week_ticks["mid"].tolist(),
                    ticktext=week_ticks["relative"].astype(str).tolist(),
                ),
                yaxis_title="Docente",
                height=600,
                legend_title="Número de sesiones",
            )
            _plot_chart(st, fig_timeline, f"fig_p4_{key_suffix}")
        else:
            st.info("No hay datos suficientes para graficar P4.")

    p6_expanded = pd.DataFrame()
    if "P6" in df.columns and "Nombres completos docentes" in df.columns:
        p6_clean = df.dropna(subset=["P6"]).copy()
        records = []
        for _, val in p6_clean.iterrows():
            val_str = str(val["P6"])
            tipo = (
                "Repaso"
                if re.search(r"repaso", val_str, flags=re.IGNORECASE)
                else "Juego"
            )
            nums = re.findall(r"\d+", val_str)
            escenarios = [f"Escenario {n}" for n in nums] if nums else ["Otro"]
            for esc in escenarios:
                records.append(
                    {
                        "Escenario": esc,
                        "Tipo": tipo,
                        "Nombres completos docentes": val["Nombres completos docentes"],
                        "Fecha_llamada": val.get("Fecha_llamada"),
                    }
                )
        p6_expanded = pd.DataFrame(records)

        col_p6a, col_p6b = st.columns(2)
        col_p6a.subheader(
            "P6. ¿Qué escenarios del juego ha implementado con los estudiantes?"
        )
        col_p6b.subheader(
            "P7. ¿Qué fase del escenario jugado alcanzaron? (No aplica para el Escenario 1)"
        )

        if not p6_expanded.empty:
            p6_counts = (
                p6_expanded.groupby(["Escenario", "Tipo"])
                .size()
                .reset_index(name="Frecuencia")
                .sort_values(
                    by="Escenario",
                    key=lambda s: pd.to_numeric(
                        s.str.extract(r"(\d+)").iloc[:, 0], errors="coerce"
                    ).fillna(999),
                )
            )

            fig_p6 = px.bar(
                p6_counts,
                x="Escenario",
                y="Frecuencia",
                color="Tipo",
                barmode="group",
                text="Frecuencia",
                title="Escenarios implementados",
                category_orders={"Tipo": ["Juego", "Repaso"]},
            )
            _plot_chart(col_p6a, fig_p6, f"fig_p6_{key_suffix}")
        else:
            col_p6a.info("No hay respuestas registradas para P6.")

        if "P7" in df.columns:
            p7_merged = df.dropna(subset=["P7"]).copy()
            p7_merged["P7"] = p7_merged["P7"].astype("string").str.strip()
            p7_merged["Tipo"] = p7_merged["P6"].map(
                lambda value: "Repaso"
                if pd.notna(value)
                and re.search(r"repaso", str(value), flags=re.IGNORECASE)
                else "Juego"
            )
            p7_fases_count = (
                p7_merged.groupby(["P7", "Tipo"])
                .size()
                .reset_index(name="Frecuencia")
                .sort_values("Frecuencia", ascending=False)
            )

            if p7_fases_count.empty:
                col_p6b.info("No hay respuestas registradas para P7.")
            else:
                fig_p7_scenario = px.bar(
                    p7_fases_count,
                    x="P7",
                    y="Frecuencia",
                    color="Tipo",
                    barmode="group",
                    text="Frecuencia",
                    title="Fase alcanzada por tipo de implementación",
                    category_orders={
                        "Tipo": ["Juego", "Repaso"],
                        "P7": p7_fases_count["P7"].tolist(),
                    },
                )
                fig_p7_scenario.update_layout(
                    xaxis_title="", yaxis_title="Frecuencia"
                )
                _plot_chart(col_p6b, fig_p7_scenario, f"fig_p7_{key_suffix}")

    col_dificultades, col_fortalezas = st.columns(2)

    if "P8" in df.columns:
        col_dificultades.subheader(
            "P8. ¿Ha encontrado dificultades al usar el juego con los estudiantes?"
        )
        p8_counts = (
            df["P8"]
            .astype("string")
            .str.strip()
            .dropna()
            .value_counts()
            .reset_index()
        )
        p8_counts.columns = ["Respuesta", "Frecuencia"]

        if p8_counts.empty:
            col_dificultades.info("No hay respuestas registradas para P8.")
        else:
            fig_p8 = px.bar(
                p8_counts,
                x="Respuesta",
                y="Frecuencia",
                text="Frecuencia",
                title="Dificultades reportadas",
            )
            _plot_chart(col_dificultades, fig_p8, f"fig_p8_{key_suffix}")

    if "P10" in df.columns:
        col_fortalezas.subheader(
            "P10. Durante la sesión, ¿identificó alguna fortaleza o resultado positivo del juego?"
        )
        p10_respuestas = (
            df["P10"]
            .astype("string")
            .str.strip()
            .dropna()
            .reset_index(drop=True)
            .to_frame(name="Fortaleza o resultado positivo")
        )

        if p10_respuestas.empty:
            col_fortalezas.info("No hay respuestas registradas para P10.")
        else:
            col_fortalezas.dataframe(
                p10_respuestas,
                use_container_width=True,
                hide_index=True,
            )

    if "P9" in df.columns:
        st.subheader("P9. ¿Cuáles han sido las principales dificultades?")

        columna = "Razones P9" if "Razones P9" in df.columns else "P9"
        p9_base = df.dropna(subset=[columna]).copy()

        if p9_base.empty:
            st.info("No hay respuestas registradas para P9.")
        elif p6_expanded.empty:
            p9_counts = (
                p9_base[columna]
                .astype("string")
                .str.strip()
                .value_counts()
                .reset_index()
            )
            p9_counts.columns = ["Dificultad", "Frecuencia"]
            st.dataframe(p9_counts, use_container_width=True, hide_index=True)
        else:
            p9_merged = pd.merge(
                p6_expanded,
                p9_base.reset_index(),
                left_on=["Nombres completos docentes", "Fecha_llamada"],
                right_on=["Nombres completos docentes", "Fecha_llamada"],
                how="inner",
            )

            p9_merged = (
                p9_merged.groupby([columna])
                .agg(
                    {
                        "Escenario": lambda x: ", ".join(sorted(x.unique())),
                        "Tipo": lambda x: ", ".join(sorted(x.unique())),
                    }
                )
                .reset_index()
            )

            p9_merged = p9_merged.sort_values(by=["Escenario", columna])[
                ["Escenario", "Tipo", columna]
            ]
            p9_merged = p9_merged.rename(columns={columna: "Dificultad"})
            st.dataframe(p9_merged, use_container_width=True, hide_index=True)


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
