import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.chart_config import get_chart_config


def get_category_orders():
    """Define los órdenes categóricos para variables ordinales"""
    return {
        # Variables demográficas
        "grado": [
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
            "Undécimo",
        ],
        "nivel": ["Primaria", "Secundaria"],
        "categoria_2024_base": ["Grupo Junior", "Grupo Senior", "Grupo Senior pro"],
        "categoria_2025_base": ["Grupo Junior", "Grupo Senior", "Grupo Senior pro"],
        "discapacidad": ["No", "Sí"],
        "sexo": ["Mujer", "Hombre"],
        "genero_par_experto_base": ["Mujer", "Hombre"],
        "cant_clases_pc": ["0", "1", "2", "3", "4", "5", "6+"],
        # Escalas Likert de acuerdo (5 niveles)
        "sentir_me_gusta_clase": [
            "Nada de acuerdo",
            "Poco de acuerdo",
            "Más o menos de acuerdo",
            "De acuerdo",
            "Muy de acuerdo",
        ],
        "sentir_atencion": [
            "Nada de acuerdo",
            "Poco de acuerdo",
            "Más o menos de acuerdo",
            "De acuerdo",
            "Muy de acuerdo",
        ],
        "sentir_emociona": [
            "Nada de acuerdo",
            "Poco de acuerdo",
            "Más o menos de acuerdo",
            "De acuerdo",
            "Muy de acuerdo",
        ],
        "sentir_espero_clase": [
            "Nada de acuerdo",
            "Poco de acuerdo",
            "Más o menos de acuerdo",
            "De acuerdo",
            "Muy de acuerdo",
        ],
        "hacer_participo": [
            "Nada de acuerdo",
            "Poco de acuerdo",
            "Más o menos de acuerdo",
            "De acuerdo",
            "Muy de acuerdo",
        ],
        "hacer_hago_dificiles": [
            "Nada de acuerdo",
            "Poco de acuerdo",
            "Más o menos de acuerdo",
            "De acuerdo",
            "Muy de acuerdo",
        ],
        "hacer_busco_respuesta": [
            "Nada de acuerdo",
            "Poco de acuerdo",
            "Más o menos de acuerdo",
            "De acuerdo",
            "Muy de acuerdo",
        ],
        # Escalas Likert de acuerdo (7 niveles - tipo Likert extendido)
        "dec_inf_conoce_carreras": [
            "Totalmente en desacuerdo",
            "En desacuerdo",
            "Neutro",
            "De acuerdo",
            "Totalmente de acuerdo",
        ],
        "dec_inf_consulta_entender": [
            "Totalmente en desacuerdo",
            "En desacuerdo",
            "Neutro",
            "De acuerdo",
            "Totalmente de acuerdo",
        ],
        "dec_inf_info_evaluar": [
            "Totalmente en desacuerdo",
            "En desacuerdo",
            "Neutro",
            "De acuerdo",
            "Totalmente de acuerdo",
        ],
        "dec_inf_confia_habilidades": [
            "Totalmente en desacuerdo",
            "En desacuerdo",
            "Neutro",
            "De acuerdo",
            "Totalmente de acuerdo",
        ],
        # Escalas numéricas
        "conceptos_identificar_importante": ["1", "2", "3", "4", "5"],
        "conceptos_usar_ideas": ["1", "2", "3", "4", "5"],
        "conceptos_dividir_problema": ["1", "2", "3", "4", "5"],
        "conceptos_pensar_pasos": ["1", "2", "3", "4", "5"],
        "conceptos_formas_diferentes": ["1", "2", "3", "4", "5"],
        "problemas_decisiones_datos": ["1", "2", "3", "4", "5"],
        "problemas_patrones": ["1", "2", "3", "4", "5"],
        "problemas_interpretar_info": ["1", "2", "3", "4", "5"],
        "problemas_arreglar": ["1", "2", "3", "4", "5"],
        "problemas_explicar_error": ["1", "2", "3", "4", "5"],
        "problemas_contar_solucion": ["1", "2", "3", "4", "5"],
        "problemas_escribir_pasos": ["1", "2", "3", "4", "5"],
    }

def box_plots(df, columnas, x_axis=None, color=None, clean_names=None):
    # -- Box Plots para Análisis de Escalas ---

    for escala in columnas:
        escala_clean = escala.replace("_", " ").title()
        x_axis_clean = x_axis.replace("_", " ").title() if x_axis else "Todos"
        color_clean = color.replace("_", " ").title() if color else "Ninguno"

        if clean_names:
            if x_axis:
                x_axis_clean = clean_names.get(x_axis, x_axis)
            if color:
                color_clean = clean_names.get(color, color)
            escala_clean = clean_names.get(escala, escala)

        st.markdown(f"#### Escala: {escala_clean}")
        if x_axis is None:  # Orientar box plot horizontal si no hay eje x
            fig = px.box(
                df,
                x=escala,
                color=color,
                title=f"Distribución de la escala {escala_clean}",
                labels={escala: escala_clean},
                notched=False,
                orientation="h",
            )

        else:
            fig = px.box(
                df,
                x=x_axis,
                y=escala,
                color=color,
                title=f"Distribución de la escala {escala_clean}",
                labels={x_axis: x_axis},
                notched=False,
            )

        if color:
            fig.update_layout(legend_title=color_clean)

        if x_axis:
            fig.update_xaxes(title=x_axis_clean)

        fig.update_yaxes(title=escala_clean)

        st.plotly_chart(fig, config=get_chart_config())

        with st.expander("Tamaños de muestra por grupo"):
            if all([color, x_axis]) and color == x_axis:
                tabla = (
                    df.groupby([x_axis])[escala]
                    .count()
                    .reset_index()
                    .set_index(x_axis)
                    .rename(columns={escala: "Tamaño de muestra"})
                )
            elif color and x_axis:
                tabla = (
                    df.groupby([x_axis, color])[escala]
                    .count()
                    .reset_index()
                    .pivot(index=x_axis, columns=color, values=escala)
                    .fillna(0)
                    .astype(int)
                )
            elif color:
                tabla = (
                    df.groupby(color)[escala]
                    .count()
                    .reset_index()
                    .set_index(color)
                    .rename(columns={escala: "Tamaño de muestra"})
                )
            elif x_axis:
                tabla = (
                    df.groupby(x_axis)[escala]
                    .count()
                    .reset_index()
                    .set_index(x_axis)
                    .rename(columns={escala: "Tamaño de muestra"})
                )
            else:
                tabla = pd.DataFrame({escala: [len(df[escala].dropna())]}).rename(
                    columns={escala: "Tamaño de muestra"}
                )

            # Rename columns using clean_names if provided
            if clean_names:
                tabla.reset_index(inplace=True)
                tabla = tabla.rename(
                    columns={col: clean_names.get(col, col) for col in tabla.columns}
                )

            st.dataframe(tabla)


def bar_plots_categorical(df, columnas, color=None, clean_names=None):
    # -- Bar Plots para Análisis de Frecuencias Relativas ---

    for escala in columnas:
        if escala == color:
            continue  # Evitar gráficos redundantes

        escala_clean = escala.replace("_", " ").title()
        color_clean = color.replace("_", " ").title() if color else "Ninguno"

        if clean_names:
            if color:
                color_clean = clean_names.get(color, color)
            escala_clean = clean_names.get(escala, escala)

        st.markdown(f"#### Escala: {escala_clean}")

        # If color is specified, create a grouped frequency table
        if color:
            freq_table = (
                df.groupby([escala, color])[escala]
                .count()
                .reset_index(name="Frecuencia")
            )
            freq_table["Frecuencia Relativa"] = freq_table.groupby(color)[
                "Frecuencia"
            ].transform(lambda x: x / x.sum())
        else:
            freq_table = df[escala].value_counts().reset_index()
            freq_table.columns = [escala, "Frecuencia"]
            freq_table["Frecuencia Relativa"] = (
                freq_table["Frecuencia"] / freq_table["Frecuencia"].sum()
            )
        fig = px.bar(
            freq_table,
            x=escala,
            y="Frecuencia Relativa",
            barmode="group",
            color=color,
            text_auto=True,
            title=f"Frecuencia de {escala_clean}",
            labels={escala: escala_clean, "Frecuencia Relativa": "Frecuencia Relativa"},
            range_y=[0,1]
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_yaxes(tickformat=".1%")

        if color:
            fig.update_layout(legend_title=color_clean)

        fig.update_xaxes(title=escala_clean)
        fig.update_yaxes(title="Frecuencia Relativa")

        st.plotly_chart(fig, config=get_chart_config())

        with st.expander("Tabla de frecuencias"):
            clean_column_names = (
                {col: clean_names.get(col, col) for col in freq_table.columns}
                if clean_names
                else {}
            )

            if clean_column_names:
                freq_table = freq_table.rename(columns=clean_column_names)
            st.dataframe(freq_table)


def bar_plots_numerical(df, columnas, bins=10, color=None, clean_names=None):
    # -- Bar plots con promedios y desviaciones estándar como error bars ---

    for escala in columnas:
        if escala == color:
            continue  # Evitar gráficos redundantes
        escala_clean = escala.replace("_", " ").title()
        color_clean = color.replace("_", " ").title() if color else "Ninguno"

        if clean_names:
            if color:
                color_clean = clean_names.get(color, color)
            escala_clean = clean_names.get(escala, escala)
        st.markdown(f"#### Escala: {escala_clean}")

        # NOT AN HISTOGRAM, BUT A BAR PLOT WITH MEANS AND STD DEV AS ERROR BARS
        if color:
            stats_table = df.groupby(color)[escala].agg(["mean", "std"]).reset_index()
            error_y_minus = []

            for i, row in stats_table.iterrows():
                lower_error = row["mean"] - row["std"]
                if lower_error < 0:
                    error_y_minus.append(row["mean"])  # set to mean to avoid negative
                else:
                    error_y_minus.append(row["std"])

            fig = px.bar(
                stats_table,
                x=color,
                y="mean",
                error_y="std",
                error_y_minus=error_y_minus,
                title=f"Promedio y Desviación Estándar de {escala_clean} por {color_clean}",
                labels={color: color_clean, "mean": f"Promedio de {escala_clean}"},
            )
            fig.update_traces(textposition="outside")
        else:
            stats_table = pd.DataFrame(
                {"mean": [df[escala].mean()], "std": [df[escala].std()]}
            )
            # make std error bars not go below zero

            error_y_minus = []

            for i, row in stats_table.iterrows():
                lower_error = row["mean"] - row["std"]
                if lower_error < 0:
                    error_y_minus.append(0)  # set to mean to avoid negative
                else:
                    error_y_minus.append(row["std"])

            fig = px.bar(
                stats_table,
                x=[escala_clean],
                y="mean",
                error_y="std",
                error_y_minus=error_y_minus,
                title=f"Promedio y Desviación Estándar de {escala_clean}",
                labels={"mean": f"Promedio de {escala_clean}"},
            )
            fig.update_traces(textposition="outside")
        fig.update_yaxes(title=f"Promedio de {escala_clean}")
        st.plotly_chart(fig, config=get_chart_config())


def migracion_graficas(
    df, columna_entrada, columna_salida, clean_names=None, color_by=None
):
    df = df.copy()
    # Gráfica de migración entre dos escalas
    # Se mantuvo, pasan a, pasan a
    # BAR PLOT
    # Frecuencia relativa
    color_clean = clean_names.get(color_by, color_by) if clean_names else color_by

    def get_category_name(row):
        from_cat = row[columna_entrada]
        to_cat = row[columna_salida]
        if pd.notna(from_cat) and pd.notna(to_cat):
            if from_cat == to_cat:
                return "Se mantuvo en " + str(from_cat)
            else:
                return f"Pasa de {from_cat} a {to_cat}"
        return None

    df["Migración"] = df.apply(get_category_name, axis=1)
    migration_df = df.dropna(subset=["Migración"])

    if color_by:
        migration_df[color_by] = migration_df[color_by].astype(str)
        freq_table = (
            migration_df.groupby(["Migración", color_by])["Migración"]
            .count()
            .reset_index(name="Frecuencia")
        )
        freq_table["Frecuencia Relativa"] = freq_table.groupby("Migración")[
            "Frecuencia"
        ].transform(lambda x: x / x.sum())
        fig = px.bar(
            freq_table,
            y="Frecuencia Relativa",
            x="Migración",
            color=color_by,
            barmode="group",
            text_auto=True,
            title=f"Gráfica de migración entre {clean_names.get(columna_entrada, columna_entrada.replace('_', ' ').title())} y {clean_names.get(columna_salida, columna_salida.replace('_', ' ').title())} por {color_clean}",
            labels={
                "Migración": "Categoría",
                "Frecuencia Relativa": "Frecuencia Relativa",
            },
            range_y=[0,1]
        )
    else:
        freq_table = (
            migration_df["Migración"].value_counts().reset_index(name="Frecuencia")
        )
        freq_table["Frecuencia Relativa"] = (
            freq_table["Frecuencia"] / freq_table["Frecuencia"].sum()
        )
        fig = px.bar(
            freq_table,
            y="Frecuencia Relativa",
            x="Migración",
            text_auto=True,
            title=f"Gráfica de migración entre {clean_names.get(columna_entrada, columna_entrada.replace('_', ' ').title())} y {clean_names.get(columna_salida, columna_salida.replace('_', ' ').title())}",
            labels={
                "Migración": "Categoría",
                "Frecuencia Relativa": "Frecuencia Relativa",
            },
            range_y=[0,1]
        )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_yaxes(title="Frecuencia Relativa", tickformat=".0%")

    st.plotly_chart(fig, config=get_chart_config())

    with st.expander("Tabla de frecuencias"):
        clean_column_names = (
            {col: clean_names.get(col, col) for col in freq_table.columns}
            if clean_names
            else {}
        )

        if clean_column_names:
            freq_table = freq_table.rename(columns=clean_column_names)
        st.dataframe(freq_table)

def correlation_plot(df, columnas, clean_names=None):
    # Matriz de correlación para las columnas numéricas seleccionadas
    corr_matrix = df[columnas].corr()

    # Crear heatmap con Plotly
    fig = go.Figure(
        data=go.Heatmap(
            z=corr_matrix.values,
            x=[
                clean_names.get(col, col) if clean_names else col
                for col in corr_matrix.columns
            ],
            y=[
                clean_names.get(col, col) if clean_names else col
                for col in corr_matrix.index
            ],
            colorscale="RdBu",
            zmin=-1,
            zmax=1,
            colorbar=dict(title="Correlación"),
        )
    )

    fig.update_layout(
        title="Matriz de Correlación entre Escalas",
        xaxis_nticks=len(corr_matrix.columns),
        yaxis_nticks=len(corr_matrix.index),
        height=600,
    )

    st.plotly_chart(fig, config=get_chart_config(), key=random.random())


def scatter_plot(df, x_col, y_col, color=None, clean_names=None):
    x_clean = clean_names.get(x_col, x_col) if clean_names else x_col
    y_clean = clean_names.get(y_col, y_col) if clean_names else y_col
    color_clean = clean_names.get(color, color) if clean_names and color else color

    category_orders = get_category_orders()
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color,
        height=600,
        title=f"Diagrama de Dispersión entre {x_clean} y {y_clean}",
        labels={x_col: x_clean, y_col: y_clean},
        category_orders=category_orders,
    )

    if color:
        fig.update_layout(legend_title=color_clean)

    st.plotly_chart(fig, config=get_chart_config())
