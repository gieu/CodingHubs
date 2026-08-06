import numpy as np
import pandas as pd
import plotly.express as px  # type: ignore
import plotly.graph_objects as go  # type: ignore
import streamlit as st
from constants.marco_constants import COLORS, CSV_URL, MAPPING


MOMENTOS_RADAR = ["pre_2023", "post_2023", "pre_2024", "post_2024", "post_2025", "nivel_2025"]


def centrar_texto(texto, tipo="h1"):
    """Centrar headers, subheaders y textos en Streamlit."""
    st.markdown(
        f"<{tipo} style='text-align: center;'>{texto}</{tipo}>", unsafe_allow_html=True
    )


def cargar_datos():
    """
    Carga los datos desde el archivo CSV publicado en Google Sheets.
    """
    return pd.read_csv(CSV_URL)


def obtener_opciones_codigos(df):
    """
    Genera las opciones de códigos de IE, combinando las opciones iniciales con los valores únicos de los códigos de IE.
    """
    opciones_codigos = ["Promedio", "Moda", "Mediana"] + [
        codigo
        for codigo in df["Código IE"].unique()
        if codigo not in ["Promedio", "Moda", "Mediana"]
    ]
    return opciones_codigos


def obtener_datos_pretest_posttest(datos_codigo):
    """
    Obtiene las series disponibles de un codigo de IE para el radar.
    """
    series = {}
    categorias = None

    for momento in MOMENTOS_RADAR:
        datos_momento = datos_codigo[datos_codigo["Momento"] == momento]
        if datos_momento.empty:
            continue

        valores = datos_momento.iloc[0, 2:]
        valores_numeric = valores.map(MAPPING)
        valores_numeric = pd.concat(
            [valores_numeric, pd.Series([valores_numeric.iloc[0]])],
            ignore_index=True,
        )

        series[momento] = valores_numeric
        if categorias is None:
            categorias = list(valores.index)

    if not series:
        return None, None

    return series, categorias


def crear_grafico_radar(series_momentos, categorias, codigo):
    """
    Crea un grafico de radar comparando los momentos disponibles.
    """
    fig = go.Figure()

    momentos_disponibles = [momento for momento in MOMENTOS_RADAR if momento in series_momentos]
    orden_dibujo = sorted(
        momentos_disponibles,
        key=lambda momento: series_momentos[momento].iloc[:-1].mean(),
        reverse=True,
    )

    for momento in orden_dibujo:
        color = COLORS[momento]
        fig.add_trace(
            go.Scatterpolar(
                r=series_momentos[momento].values,
                theta=categorias + [categorias[0]],
                fill="toself",
                name=momento.replace("_", " ").title(),
                line_color=color["line"],
                fillcolor=color["fill"],
                legendrank=MOMENTOS_RADAR.index(momento),
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 8],
                tickvals=list(MAPPING.values()),
                ticktext=list(MAPPING.keys()),
                tick0=0,
                dtick=1,
            ),
            angularaxis=dict(
                rotation=90,
                direction="clockwise",
            ),
        ),
        showlegend=True,
        title=f"Comparacion historica del Marco de Calidad para {codigo}",
        height=600,
    )

    return fig


def heatmap(df, clean_column_names: dict = None, value_cols: list = None, codigo_ie_nombres: dict = None):
    """Genera un heatmap de las dimensiones evaluadas.
    con px.imshow de plotly.express."""
    df = df.copy()

    ordered_vals = ["1A", "1B", "2A", "2B", "3A", "3B", "4", "5"]

    df_long = df.astype(str).melt(
        id_vars="codigo_ie",
        value_vars=value_cols,
        var_name="variable",
        value_name="valor",
    )

    color_map = {
        "1A": "#fcb6ae",  # red 1
        "1B": "#fdc5b4",  # red 2
        "2A": "#fcd9b4",  # 3
        "2B": "#ffe8af",  # 4
        "3A": "#fcf3ab",  # 5
        "3B": "#f8f6ab",  # 6
        "4": "#d8edb2",  # 7
        "5": "#b2e4a4",  # green 8
    }

    # Build a discrete colorscale with flat segments (no interpolation)

    cat_to_int = {cat: i for i, cat in enumerate(ordered_vals)}

    df_long["valor_int"] = df_long["valor"].astype(str).map(cat_to_int)
    matrix = df_long.pivot(index="variable", columns="codigo_ie", values="valor_int")

    # Sort columns (codigo_ie) alphabetically
    matrix = matrix[sorted(matrix.columns)]
    
    # Replace codigo_ie with short names if provided
    if codigo_ie_nombres:
        matrix.columns = [codigo_ie_nombres.get(col, col) for col in matrix.columns]

    if clean_column_names:
        matrix.index = [clean_column_names.get(col, col) for col in matrix.index]

    # generate the normalized thresholds
    N = len(ordered_vals)  # 8
    thresholds = [i / N for i in range(N + 1)]  # 0/8 ... 8/8

    # build the discrete colorscale
    discrete_colorscale = []

    for i, cat in enumerate(ordered_vals):
        t0 = thresholds[i]
        t1 = thresholds[i + 1]
        rgb = color_map[cat]

        discrete_colorscale.append([t0, rgb])
        discrete_colorscale.append([t1, rgb])

    fig = px.imshow(
        matrix,
        color_continuous_scale=discrete_colorscale,
        aspect="auto",
        zmin=0,
        zmax=8,
    )

    N = len(ordered_vals)
    midpoints = [(2 * i + 1) / (2) for i in range(N)]

    fig.update_coloraxes(
        colorbar=dict(
            tickmode="array",
            tickvals=midpoints,
            ticktext=ordered_vals,
        )
    )

    fig.update_traces(
        xgap=0.5,
        ygap=0.5,
    )
    # Update color on hover to use categorical values
    hover_matrix = df_long.pivot(
        index="variable", columns="codigo_ie", values="valor"
    )
    hover_matrix = hover_matrix[sorted(hover_matrix.columns)]
    
    fig.update_traces(
        hovertemplate="Institución: %{x}<br>Escala: %{y}<br>Valor: %{customdata} <br><extra></extra>",
        customdata=hover_matrix.values,
    )

    fig.update_layout(
        width=1600,
        height=500,
        # margin=dict(l=280, r=40, t=80, b=10),
        title="Mapa de calor de escalas",
        xaxis_title="Institución Educativa",
        yaxis_title="Variable",
    )

    fig

    return fig


def grafica_estado(df, clean_names: dict = None):
    """Genera una gráfica de barras horizontales apiladas para el estado de implementación."""
    df = df.copy()
    cats = ["aumento", "igual", "alerta"]
    order = ["aumento", "igual", "alerta"]
    color_map = {
        "alerta": "#fcb6ae",
        "igual": "#fcf3ab",
        "aumento": "#b2e4a4",
    }

    df_long = df.assign(categoria=df[cats].idxmax(axis=1))[["codigo_ie", "categoria"]]

    # Map categories to integers starting at 1 (reserve 0 for empty/NaN)
    cat_to_int = {cat: i + 1 for i, cat in enumerate(order)}
    df_long["val"] = df_long["categoria"].map(cat_to_int)
    matrix = df_long.pivot(index="categoria", columns="codigo_ie", values="val")

    # Reindex to ensure all categories are present (even if empty)
    matrix = matrix.reindex(order, fill_value=0)

    # Sort columns (codigo_ie) alphabetically
    matrix = matrix[sorted(matrix.columns)]

    # Create category name matrix for hover
    # For each column (codigo_ie), fill all rows with the actual category value (the non-NaN one)
    category_matrix = df_long.pivot(
        index="categoria", columns="codigo_ie", values="categoria"
    )

    # Reindex to ensure all categories are present
    category_matrix = category_matrix.reindex(order)

    # Sort columns to match matrix
    category_matrix = category_matrix[sorted(category_matrix.columns)]

    # Fill NaN in each column with the non-NaN value from that column
    for col in category_matrix.columns:
        non_nan_val = category_matrix[col].dropna()
        if len(non_nan_val) > 0:
            category_matrix[col] = category_matrix[col].fillna(non_nan_val.iloc[0])
        else:
            category_matrix[col] = category_matrix[col].fillna("")

    # Fill NaN with 0 to represent empty cells in the numeric matrix
    matrix = matrix.fillna(0)

    # Build discrete colorscale: 0 → white, then each category gets its color
    # We have 4 values now: 0 (empty), 1 (alerta), 2 (igual), 3 (aumento)
    n_cats = len(order) + 1  # +1 for the empty/0 value
    thresholds = [i / n_cats for i in range(n_cats + 1)]

    colorscale = []
    # First segment: 0 → white
    colorscale.append([thresholds[0], "#ffffff"])
    colorscale.append([thresholds[1], "#ffffff"])

    # Remaining segments: map to categories in order
    for i, cat in enumerate(order):
        t0 = thresholds[i + 1]
        t1 = thresholds[i + 2]
        rgb = color_map[cat]
        colorscale.append([t0, rgb])
        colorscale.append([t1, rgb])

    fig = px.imshow(
        matrix,
        color_continuous_scale=colorscale,
        aspect="auto",
        zmin=0,
        zmax=n_cats - 1,
        title="Alertas",
    )

    fig.update_coloraxes(showscale=False)

    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Categoría: %{customdata}<extra></extra>",
        customdata=category_matrix.values,
    )

    fig.update_layout(
        yaxis=dict(
            title="Categoría",
            ticktext=[c.capitalize() for c in order],
            tickvals=list(range(len(order))),
        ),
        xaxis=dict(title="Código IE"),
        height=450,
    )

    fig.update_traces(
        xgap=0.3,
        ygap=0.3,
    )
    # Remove gridlines
    fig.update_xaxes(showgrid=False)

    return fig


def conteo_estado(df):
    """Genera un gráfico de barras con el conteo de colegios por estado de alerta."""
    df = df.copy()
    cats = ["alerta", "igual", "aumento"]
    color_map = {
        "alerta": "#fcb6ae",
        "igual": "#fcf3ab",
        "aumento": "#b2e4a4",
    }

    # Get the category with max value for each school
    df_long = df.assign(categoria=df[cats].idxmax(axis=1))

    # Count occurrences of each category
    counts = df_long["categoria"].value_counts().reindex(cats, fill_value=0)

    # Calculate percentages
    total = counts.sum()
    percentages = (counts / total * 100) if total > 0 else counts * 0

    # Create text labels with count and percentage
    text_labels = [
        f"{int(count)} ({pct:.1f}%)"
        for count, pct in zip(counts.values, percentages.values)
    ]

    # Create bar chart
    fig = px.bar(
        x=counts.index,
        y=counts.values,
        text=text_labels,
        title="Número de colegios por estado de alerta",
        labels={"x": "Estado", "y": "Número de colegios"},
    )

    # Apply colors to each bar
    fig.update_traces(
        marker_color=[color_map[cat] for cat in counts.index],
        textposition="outside",
        cliponaxis=False,
    )

    # Update x-axis labels to capitalize
    fig.update_xaxes(ticktext=[c.capitalize() for c in cats], tickvals=cats)

    fig.update_layout(
        xaxis_title="Estado",
        yaxis_title="Número de colegios",
        height=400,
        showlegend=False,
    )
    # anchor false

    return fig


def barras_pretest_postest(df, value_cols: dict = None):
    df = df.copy()
    ordered_vals = ["1A", "1B", "2A", "2B", "3A", "3B", "4", "5"]

    color_map = {
        "1A": "#fcb6ae",  # red 1
        "1B": "#fdc5b4",  # red 2
        "2A": "#fcd9b4",  # 3
        "2B": "#ffe8af",  # 4
        "3A": "#fcf3ab",  # 5
        "3B": "#f8f6ab",  # 6
        "4": "#d8edb2",  # 7
        "5": "#b2e4a4",  # green 8
    }

    df_long = df.melt(
        id_vars=[],
        value_vars=list(value_cols.keys()),
        var_name="Momento",
        value_name="Categoria",
    )

    df_long["Momento"] = df_long["Momento"].map(value_cols)

    # Convert Categoria to ordered categorical
    df_long["Categoria"] = pd.Categorical(
        df_long["Categoria"], ordered_vals, ordered=True
    )

    pct = (
        df_long.groupby(["Momento", "Categoria"])
        .size()
        .groupby(level=0, group_keys=False, observed=False)
        .apply(lambda x: x / x.sum())
        .reset_index()
        .rename(columns={0: "Porcentaje"})
    )

    fig = px.bar(
        pct,
        x="Porcentaje",
        y="Momento",
        color="Categoria",
        orientation="h",
        category_orders={"Categoria": ordered_vals},
        color_discrete_map=color_map,
    )
    fig.update_yaxes(
        categoryorder="array", categoryarray=list(value_cols.values())[::-1]
    )
    # format x axis as percentage
    fig.update_xaxes(tickformat=",.0%", dtick=0.1)
    fig.update_layout(
        barmode="stack",
        xaxis_title="Porcentaje de instituciones",
        yaxis_title="Momento",
        title="Distribución de puntajes por momento",
        legend_title="Categoría",
        legend_orientation="h",
        legend_y=1.15,
        legend_x=0.3,
    )
    return fig
