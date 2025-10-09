import pandas as pd
import streamlit as st
import plotly.express as px
from utils.chart_config import get_chart_config
chart_config = get_chart_config()

def es_numerica(col, df):
    """Verifica si una columna es numérica."""
    try:
        return pd.api.types.is_numeric_dtype(df[col])
    except KeyError:
        return False

def aplicar_filtros(df, key_suffix=""):
    """Aplica filtros dinámicos al DataFrame."""
    df_filtrado = df.copy()
    with st.expander("Filtros de Datos (Opcional)", expanded=False):
        columnas_filtro = st.multiselect("Selecciona columnas para filtrar", df.columns, key=f"aplicar_filtros_columnas_{key_suffix}")
        for i, col in enumerate(columnas_filtro):
            if es_numerica(col, df):
                rango = st.slider(
                    f"Rango para {col}",
                    float(df[col].min()),
                    float(df[col].max()),
                    (float(df[col].min()), float(df[col].max())),
                    key=f"aplicar_filtros_rango_{col}_{i}_{key_suffix}"
                )
                df_filtrado = df_filtrado[(df_filtrado[col] >= rango[0]) & (df_filtrado[col] <= rango[1])]
            else:
                valores = df[col].dropna().unique().tolist()
                seleccionados = st.multiselect(f"Valores para {col}", valores, default=valores, key=f"aplicar_filtros_valores_{col}_{i}_{key_suffix}")
                df_filtrado = df_filtrado[df_filtrado[col].isin(seleccionados)]
    return df_filtrado

def graficador (df, key_suffix=""):
    # Selección del tipo de gráfico
    chart_type = st.radio("Tipo de Gráfico", ["Barras", "Dispersión", "Cajas", "Línea", "Histograma"], key=f"chart_type_{key_suffix}")

    # Selección de categoría y columna para el eje X
    col_x = st.selectbox("Selecciona una columna para el eje X", df.columns, key=f"col_x_{key_suffix}")

    # Selección de categoría y columna para el eje Y
    col_y = st.selectbox("Variable para el eje Y", df.columns, key=f"col_y_{key_suffix}")

    if col_x == col_y:
        st.warning("La variable para el eje X y el eje Y no pueden ser la misma. Por favor, selecciona columnas diferentes.")
        st.stop()


    # Agrupar los selectboxes en una sola fila
    col1, col2, col3 = st.columns(3)

    with col1:
        facet_col = st.selectbox("Dividir en columnas por (opcional)", ["Ninguna"] + [col for col in df.columns if col != col_y], key=f"facet_col_{key_suffix}")

    with col2:
        facet_row = st.selectbox("Dividir en filas por (opcional)", ["Ninguna"] + [col for col in df.columns if col != col_y], key=f"facet_row_{key_suffix}")

    with col3:
        col_color = st.selectbox("Agrupar por color (opcional)", ["Ninguna"] + [col for col in df.columns if col != col_y], key=f"col_color_{key_suffix}")


    def es_numerica(col, df):
        try:
            return pd.api.types.is_numeric_dtype(df[col])
        except KeyError:
            return False

    # --- Filtros dinámicos ---
    df_filtrado = df.copy()

    with st.expander("Filtros de Datos (Opcional)", expanded=False):
        columnas_filtro = st.multiselect("Selecciona columnas para filtrar", df.columns, key=f"columnas_filtro_{key_suffix}")
        for i, col in enumerate(columnas_filtro):
            if es_numerica(col, df):
                rango = st.slider(f"Rango para {col}", float(df[col].min()), float(df[col].max()), (float(df[col].min()), float(df[col].max())), key=f"rango_{col}_{i}_{key_suffix}")
                df_filtrado = df_filtrado[(df_filtrado[col] >= rango[0]) & (df_filtrado[col] <= rango[1])]
            else:
                valores = df[col].dropna().unique().tolist()
                seleccionados = st.multiselect(f"Valores para {col}", valores, default=valores, key=f"valores_{col}_{i}_{key_suffix}")
                df_filtrado = df_filtrado[df_filtrado[col].isin(seleccionados)]


    # Validación extra de variable Y para gráficos numéricos
    if chart_type in ["Dispersión", "Línea", "Cajas"]:
        if not es_numerica(col_y, df):
            st.warning(f"La variable Y '{col_y}' debería ser numérica para el gráfico seleccionado.")
            st.stop()

    # --- Preparar datos para gráficos ---
    df_plot = df_filtrado.copy()

    if chart_type == "Barras":
        opciones_agregacion = ["Cuenta",  "Cuenta de únicos"]
        if es_numerica(col_y, df):
            opciones_agregacion.insert(1, "Promedio")  # Solo agregar 'Promedio' si es numérica
            opciones_agregacion.insert(2, "Suma" ) 
        metodo_agregacion = st.selectbox("Método de agregación", opciones_agregacion, key=f"metodo_agregacion_{key_suffix}")
        aggfunc = {"Promedio": "mean","Suma": "sum", "Cuenta": "count", "Cuenta de únicos": "nunique"}[metodo_agregacion]
        indices=[facet_col,facet_row, col_color, col_x]#contiene todos los datos de los filtros que no sea ninguna ni eje y
        indices=set(indices).difference(set(["Ninguna"]))#elimina los valores de ninguna
        indices=list(indices)
        df_plot = pd.pivot_table(df_filtrado, values=col_y, index=indices, aggfunc=aggfunc).reset_index()


        # Verificar que las columnas seleccionadas existen en el DataFrame después de pivot_table
        if col_y not in df_plot.columns:
            st.error(f"La columna '{col_y}' no se encuentra en los datos después de aplicar pivot_table. Por favor, selecciona otra columna.")
            st.stop()

        # Selección del tipo de barra (barmode)
        barmode = st.selectbox("Tipo de barra", ["grupo", "apilado", "superpuesto", "relativo"])
        barmode_dict = {"grupo": "group", "apilado": "stack", "superpuesto": "overlay", "relativo": "relative"}
        if st.checkbox("Ver barras horizontales"):
            orientation = 'h'
            invertir = True
        else:
            orientation = 'v'
            invertir = False
        
        if st.checkbox("Visualizar frecuencia relativa"):
            columna_total = st.multiselect("Relativo respecto a:", ["Total"] + indices)
            if len(columna_total) == 0:
                st.warning("Por favor, selecciona una columna para calcular la frecuencia relativa.")
                st.stop()
            if len(columna_total) > 1 and "Total" in columna_total:
                st.warning("Selección errónea. Si desea ver el porcentaje respecto al Total, elimine los demás valores seleccionados, de lo contrario, elimine 'Total' para elegir una combinación personalizada")
                st.stop()
            if columna_total[0] == "Total":
                total = df_plot[col_y].sum()
                df_plot["Frecuencia"] = df_plot[col_y] / total
            elif columna_total == "Preguntas":
                arreglo_indices = [columna_total]
                if facet_row is not None:
                    arreglo_indices.append(facet_row)
                if facet_col is not None:
                    arreglo_indices.append(facet_col)
                total = df_plot.pivot_table(index=list(set(arreglo_indices)),
                                            values=col_y,
                                            aggfunc='sum').rename(columns={col_y: "TOTAL"}).reset_index()
                df_plot = df_plot.merge(total, on=list(set(arreglo_indices)))
                df_plot["Frecuencia"] = df_plot[col_y] / df_plot["TOTAL"]
            else:
                total = df_plot.pivot_table(index=columna_total,
                                            values=col_y,
                                            aggfunc='sum').rename(columns={col_y: "TOTAL"}).reset_index()
                df_plot = df_plot.merge(total, on=columna_total)
                df_plot["Frecuencia"] = df_plot[col_y] / df_plot["TOTAL"]
            visualizarFrecuencia=True
        else:
            visualizarFrecuencia=False

    # Selección de colores
    color_palettes = {
        "Plotly": px.colors.qualitative.Plotly,
        "Viridis": px.colors.sequential.Viridis,
        "Cividis": px.colors.sequential.Cividis,
        "Inferno": px.colors.sequential.Inferno,
        "Magma": px.colors.sequential.Magma,
        "Plasma": px.colors.sequential.Plasma,
        "Turbo": px.colors.sequential.Turbo,
        "G10": px.colors.qualitative.G10,
        "T10": px.colors.qualitative.T10,
        "Alphabet": px.colors.qualitative.Alphabet,
        "Dark24": px.colors.qualitative.Dark24,
        "Light24": px.colors.qualitative.Light24,
        "Set1": px.colors.qualitative.Set1,
        "Pastel1": px.colors.qualitative.Pastel1,
        "Set2": px.colors.qualitative.Set2,
        "Pastel2": px.colors.qualitative.Pastel2,
        "Set3": px.colors.qualitative.Set3,
        "Antique": px.colors.qualitative.Antique,
        "Bold": px.colors.qualitative.Bold,
        "D3": px.colors.qualitative.D3,
        "Prism": px.colors.qualitative.Prism,
        "Safe": px.colors.qualitative.Safe,
        "Vivid": px.colors.qualitative.Vivid
    }

    color_palette = st.selectbox("Paleta de colores", list(color_palettes.keys()))
    color_sequence = color_palettes[color_palette]

    category_order = {}

    if chart_type in ["Barras", "Cajas", "Histograma"]:
        valores_unicos = df[col_x].dropna().unique().tolist()
        with st.expander("Orden de categorías (Opcional)", expanded=False):
            category_order[col_x] = st.multiselect("Ordena las categorías", options=valores_unicos, default=valores_unicos)



    if df_plot.empty:
        st.warning("No hay datos disponibles después de aplicar los filtros. Ajusta los filtros.")

    # Verificar que las columnas seleccionadas existen en el DataFrame
    if col_y not in df_plot.columns:
        st.error(f"La columna '{col_y}' no se encuentra en los datos filtrados. Por favor, selecciona otra columna.")

    with st.expander("Vista previa de datos filtrados", expanded=False):
        st.dataframe(df_plot.dropna().head(1000))

    title = f"{chart_type}: {col_x} vs {col_y}"
    color_param = None if col_color == "Ninguna" else col_color
    if col_color == "Ninguna":
        col_color = None

    # Configuración de facetas
    facet_col_param = None if facet_col == "Ninguna" else facet_col
    facet_row_param = None if facet_row == "Ninguna" else facet_row

    if chart_type == "Barras":
        if visualizarFrecuencia:
            fig = px.bar(
                df_plot,
                x=col_x if orientation == 'v' else "Frecuencia",
                y="Frecuencia" if orientation == 'v' else col_x,
                color=col_color,
                title=title,
                barmode=barmode_dict[barmode],
                color_discrete_sequence=color_sequence,
                facet_col=facet_col_param,
                facet_row=facet_row_param,
                category_orders=category_order,
                orientation=orientation,
                text="Frecuencia"
            )
            fig.update_traces(texttemplate='%{text:.2%}', textposition='outside')
            fig.update_layout(yaxis_tickformat=',.0%' if orientation == 'v' else None,
                            xaxis_tickformat=',.0%' if orientation == 'h' else None)
        else:
            # Crear gráfico de barras absoluto
            fig = px.bar(
                df_plot,
                x=col_x if orientation == 'v' else col_y,
                y=col_y if orientation == 'v' else col_x,
                color=col_color,
                title=title,
                barmode=barmode_dict[barmode],
                color_discrete_sequence=color_sequence,
                facet_col=facet_col_param,
                facet_row=facet_row_param,
                category_orders=category_order,
                orientation=orientation
            )
        # fig = px.bar(
        #     df_plot,
        #     x=col_x if orientation == 'v' else col_y,
        #     y=col_y if orientation == 'v' else col_x,
        #     color=col_color,
        #     title=title,
        #     barmode=barmode_dict[barmode],
        #     color_discrete_sequence=color_sequence,
        #     facet_col=facet_col_param,
        #     facet_row=facet_row_param,
        #     category_orders=category_order,
        #     orientation=orientation
        # )

    elif chart_type == "Dispersión":
        fig = px.scatter(df_plot, x=col_x, y=col_y, color=color_param, title=title, color_discrete_sequence=color_sequence, facet_col=facet_col_param, facet_row=facet_row_param)
    elif chart_type == "Cajas":
        fig = px.box(df_plot, x=col_x, y=col_y, color=color_param, title=title, color_discrete_sequence=color_sequence, facet_col=facet_col_param, facet_row=facet_row_param,category_orders=category_order)
    elif chart_type == "Línea":
        fig = px.line(df_plot, x=col_x, y=col_y, color=color_param, title=title, color_discrete_sequence=color_sequence, facet_col=facet_col_param, facet_row=facet_row_param)
    elif chart_type == "Histograma":
        # Selección del tipo de barra (barmode) para histograma
        barmode = st.selectbox("Tipo de barra", ["grupo", "superpuesto", "relativo"], key=f"barmode_{key_suffix}")
        barmode_dict = {"grupo": "group", "superpuesto": "overlay", "relativo": "relative"}
        fig = px.histogram(df_plot, x=col_x, color=color_param, title=title, barmode=barmode_dict[barmode], color_discrete_sequence=color_sequence, facet_col=facet_col_param, facet_row=facet_row_param,category_orders=category_order)

    st.plotly_chart(fig, use_container_width=True, config=chart_config)
