import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.chart_config import get_chart_config


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
