import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import header
from utils.chart_config import get_chart_config

header()

# Configuración para gráficos editables
config = get_chart_config()

# URL del CSV


# https://docs.google.com/spreadsheets/d/1ehelZqVR8oI6JSZMhO7sk3JJAcZSX1dI/edit?usp=drive_link&ouid=100392150653930865831&rtpof=true&sd=true

CSV_URL_1 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ349dV0x3kD3lAFYsZ_HhjDNpFvwDH0vIA2At72cCPkQUfO1-cedpfcGSzL0LLaQ/pub?gid=1743755992&single=true&output=csv"

## datos desde 2023 "https://docs.google.com/spreadsheets/d/13KVWqDpj_FrMao2p1w6KG6aCGvLa8i4w/edit?usp=sharing&ouid=100392150653930865831&rtpof=true&sd=true"
CSV_URL_2 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTSPXfl_xqFVNqabjhLz9XLJKn8uDDTF9wNppiA0Uj-nvEir8ZC3Xrv_oD4FrrJLQ/pub?gid=464506416&single=true&output=csv"

# --- Cargar Datos con Cache ---
@st.cache_data(ttl=600)
def load_data(file):
    df = pd.read_csv(file, low_memory=False)
    df.columns = df.columns.str.strip()
    return df

try:
    csv = st.radio("Selecciona el conjunto de datos a analizar:", ("Datos 2024-2025", "Datos 2023 - 2025"))
    
    if csv == "Datos 2024-2025":
        df = load_data(CSV_URL_1)
    else:
        df = load_data(CSV_URL_2)
    
    # Convertir columnas numéricas a tipo numérico
    columnas_numericas = ['puntaje_PC', 'autoeficacia_pc', 
                          'autoeficacia_pedagogica', 'apoyo', 'frustracion', 
                          'redes_inter', 'trabajo_colaborativo']
    
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Limpiar y preparar datos - mantener el año para diferenciar post_2024 y post_2025
    # Crear una columna más legible para visualización
    df['momento_display'] = df['momento'].str.replace('_', ' ').str.title()
    
    # Filtros
    st.header("🔍 Filtros")
    
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    
    with col_filtro1:
        # Filtro de género
        if 'genero_par_experto_base' in df.columns:
            generos_disponibles = ['Todos', 'Comparar ambos'] + sorted(df['sexo_asistencia'].dropna().unique().tolist())
            genero_seleccionado = st.selectbox(
                "Seleccionar género:",
                options=generos_disponibles,
                index=0,
                key='filtro_genero'
            )
            
            # Aplicar filtro
            if genero_seleccionado == 'Comparar ambos':
                comparar_generos = True
            elif genero_seleccionado != 'Todos':
                df = df[df['genero_par_experto_base'] == genero_seleccionado]
                comparar_generos = False
            else:
                comparar_generos = False
    
    with col_filtro2:
        # Filtro de área docente
        if 'area_docente' in df.columns:
            areas_disponibles = ['Todas'] + sorted(df['area_docente'].dropna().unique().tolist())
            area_seleccionada = st.selectbox(
                "Seleccionar área docente:",
                options=areas_disponibles,
                index=0,
                key='filtro_area'
            )
            
            # Aplicar filtro
            if area_seleccionada != 'Todas':
                df = df[df['area_docente'] == area_seleccionada]
    
    with col_filtro3:
        # Selector de tipo de gráfico
        tipo_grafico = st.selectbox(
            "Tipo de visualización:",
            options=['Box Plot', 'Violin Plot'],
            index=0,
            key='tipo_grafico_distribucion'
        )
    
    # Mostrar información de filtros aplicados
    filtros_activos = []
    if 'genero_seleccionado' in locals():
        if genero_seleccionado == 'Comparar ambos':
            filtros_activos.append("**Género:** Comparando ambos")
        elif genero_seleccionado != 'Todos':
            filtros_activos.append(f"**Género:** {genero_seleccionado.title()}")
    
    if 'area_seleccionada' in locals() and area_seleccionada != 'Todas':
        filtros_activos.append(f"**Área Docente:** {area_seleccionada}")
    
    if filtros_activos:
        st.info("📊 Filtros aplicados: " + " | ".join(filtros_activos))
    
    st.markdown("---")
    
    # Métricas generales
    st.header("📈 Resumen General")
    
    if 'comparar_generos' in locals() and comparar_generos and 'genero_par_experto_base' in df.columns:
        generos = sorted(df['genero_par_experto_base'].dropna().unique().tolist())
        
        for genero in generos:
            st.subheader(f"📊 {genero.title()}")
            df_genero = df[df['genero_par_experto_base'] == genero]
            
            col1, col2 = st.columns(2)
            
            with col1:
                total_Pares = df_genero['cedula_asistencia'].nunique()
                st.metric("Total Pares", total_Pares)
            
            with col2:
                momentos_unicos = df_genero['momento'].nunique()
                st.metric("Momentos de Medición", momentos_unicos)
            
            st.markdown("---")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            total_Pares = df['cedula_asistencia'].nunique()
            st.metric("Total Pares", total_Pares)
        
        with col2:
            momentos_unicos = df['momento'].nunique()
            st.metric("Momentos de Medición", momentos_unicos)
        
        st.markdown("---")
    
    # Análisis por momento
    st.header("📊 Evolución Temporal")
    
    if 'comparar_generos' in locals() and comparar_generos and 'genero_par_experto_base' in df.columns:
        generos = sorted(df['genero_par_experto_base'].dropna().unique().tolist())
        
        for genero in generos:
            st.subheader(f"📊 {genero.title()}")
            df_genero = df[df['genero_par_experto_base'] == genero]
            
            # Promedio por momento
            momento_stats = df_genero.groupby('momento').agg({
                'puntaje_PC': 'mean',
                'autoeficacia_pc': 'mean',
                'autoeficacia_pedagogica': 'mean',
                'apoyo': 'mean',
                'frustracion': 'mean',
                'redes_inter': 'mean',
                'trabajo_colaborativo': 'mean'
            }).round(2)

            # Ordenar por momento cronológico
            orden_momentos = ['pre_2024', 'post_2024', 'post_2025']
            if csv != "Datos 2024-2025":
                orden_momentos = ['pre_2023', 'post_2023', 'pre_2024', 'post_2024', 'post_2025']
            # Filtrar solo los momentos que existen en el índice
            momentos_disponibles = [m for m in orden_momentos if m in momento_stats.index]
            if momentos_disponibles:
                momento_stats = momento_stats.loc[momentos_disponibles]
            
            st.markdown("**Promedios por Momento**")
            st.dataframe(momento_stats, use_container_width=True)
            st.markdown("---")
    else:
        # Promedio por momento
        momento_stats = df.groupby('momento').agg({
            'puntaje_PC': 'mean',
            'autoeficacia_pc': 'mean',
            'autoeficacia_pedagogica': 'mean',
            'apoyo': 'mean',
            'frustracion': 'mean',
            'redes_inter': 'mean',
            'trabajo_colaborativo': 'mean'
        }).round(2)

        # Ordenar por momento cronológico
        orden_momentos = ['pre_2024', 'post_2024', 'post_2025']
        if csv != "Datos 2024-2025":
            orden_momentos = ['pre_2023', 'post_2023', 'pre_2024', 'post_2024', 'post_2025']
        # Filtrar solo los momentos que existen en el índice
        momentos_disponibles = [m for m in orden_momentos if m in momento_stats.index]
        if momentos_disponibles:
            momento_stats = momento_stats.loc[momentos_disponibles]
        
        st.subheader("Promedios por Momento")
        st.dataframe(momento_stats, use_container_width=True)

    st.markdown("---")
    
    # Diagramas de bigotes
    st.header("📦 Diagramas de Distribución - Evolución Temporal")
    
    # Variables para los box plots con nombres más legibles
    variables = {
        'puntaje_PC': 'Puntaje PC',
        'autoeficacia_pc': 'Autoeficacia PC',
        'autoeficacia_pedagogica': 'Autoeficacia Pedagógica',
        'apoyo': 'Apoyo Percibido',
        'frustracion': 'Nivel de Frustración',
        'redes_inter': 'Redes Interpersonales',
        'trabajo_colaborativo': 'Trabajo Colaborativo'
    }

    # Preparar datos una sola vez
    df_plot = df.copy()
    df_plot['momento_display'] = df_plot['momento'].str.replace('_', ' ').str.title()
    momento_order = ['Pre 2024', 'Post 2024', 'Post 2025']
    if csv != "Datos 2024-2025":
        momento_order = ['Pre 2023', 'Post 2023', 'Pre 2024', 'Post 2024', 'Post 2025']
    
    # Crear grid de 2 columnas para los box plots
    var_items = list(variables.items())
    for i in range(0, len(var_items), 2):
        col1, col2 = st.columns(2)
        
        with col1:
            var_col, var_name = var_items[i]
            
            # Si comparar_generos está activo y existe la columna de género
            if 'comparar_generos' in locals() and comparar_generos and 'genero_par_experto_base' in df_plot.columns:
                if tipo_grafico == 'Violin Plot':
                    fig = px.violin(
                        df_plot,
                        x='momento_display',
                        y=var_col,
                        color='momento',
                        facet_col='genero_par_experto_base',
                        title=f'📊 {var_name}',
                        color_discrete_map={
                            'pre_2024': '#FF6B6B',
                            'post_2024': '#4ECDC4',
                            'post_2025': '#A8E6CF'
                        },
                        box=True,
                        points='outliers',
                        category_orders={'momento_display': momento_order},
                        labels={'genero_par_experto_base': 'Género'},
                        violinmode='overlay'
                    )
                    fig.update_traces(width=0.8)
                else:
                    fig = px.box(
                        df_plot,
                        x='momento_display',
                        y=var_col,
                        color='momento',
                        facet_col='genero_par_experto_base',
                        title=f'📊 {var_name}',
                        color_discrete_map={
                            'pre_2024': '#FF6B6B',
                            'post_2024': '#4ECDC4',
                            'post_2025': '#A8E6CF'
                        },
                        points="outliers",
                        category_orders={'momento_display': momento_order},
                        labels={'genero_par_experto_base': 'Género'}
                    )
            else:
                if tipo_grafico == 'Violin Plot':
                    fig = px.violin(
                        df_plot,
                        x='momento_display',
                        y=var_col,
                        color='momento',
                        title=f'📊 {var_name}',
                        color_discrete_map={
                            'pre_2024': '#FF6B6B',
                            'post_2024': '#4ECDC4',
                            'post_2025': '#A8E6CF'
                        },
                        box=True,
                        points='outliers',
                        category_orders={'momento_display': momento_order},
                        violinmode='overlay'
                    )
                    fig.update_traces(width=0.8)
                else:
                    fig = px.box(
                        df_plot,
                        x='momento_display',
                        y=var_col,
                        color='momento',
                        title=f'📊 {var_name}',
                        color_discrete_map={
                            'pre_2024': '#FF6B6B',
                            'post_2024': '#4ECDC4',
                            'post_2025': '#A8E6CF'
                        },
                        points="outliers",
                        category_orders={'momento_display': momento_order}
                    )
            
            if tipo_grafico == 'Box Plot':
                fig.update_traces(width=0.6)
            
            # Ajustar altura si hay comparación de géneros
            altura = 450 if not ('comparar_generos' in locals() and comparar_generos) else 400
            
            # Si hay comparación de géneros, actualizar las etiquetas de las facetas
            if 'comparar_generos' in locals() and comparar_generos:
                fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1].title(), y=0.975))
            
            fig.update_layout(
                showlegend=False,
                height=altura,
                xaxis_title="",
                yaxis_title="",
                font=dict(size=12, color='#2c3e50'),
                plot_bgcolor='white',
                paper_bgcolor='#f8f9fa',
                margin=dict(t=60, b=40, l=60, r=20),
                title=dict(
                    font=dict(size=16, color='#2c3e50', family='Arial, sans-serif'),
                    x=0.5,
                    xanchor='center'
                ),
                xaxis=dict(
                    showgrid=False,
                    tickfont=dict(size=11, color='#5a6c7d'),
                    linecolor='#dee2e6',
                    linewidth=1
                ),
                yaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='#e9ecef',
                    tickfont=dict(size=11, color='#5a6c7d'),
                    linecolor='#dee2e6',
                    linewidth=1
                ),
                boxgap=0.2,
                boxgroupgap=0.1
            )
            st.plotly_chart(fig, use_container_width=True, config=config)
        
        if i + 1 < len(var_items):
            with col2:
                var_col, var_name = var_items[i + 1]
                
                # Si comparar_generos está activo y existe la columna de género
                if 'comparar_generos' in locals() and comparar_generos and 'genero_par_experto_base' in df_plot.columns:
                    if tipo_grafico == 'Violin Plot':
                        fig = px.violin(
                            df_plot,
                            x='momento_display',
                            y=var_col,
                            color='momento',
                            facet_col='genero_par_experto_base',
                            title=f'📊 {var_name}',
                            color_discrete_map={
                                'pre_2024': '#FF6B6B',
                                'post_2024': '#4ECDC4',
                                'post_2025': '#A8E6CF'
                            },
                            box=True,
                            points='outliers',
                            category_orders={'momento_display': momento_order},
                            labels={'genero_par_experto_base': 'Género'},
                            violinmode='overlay'
                        )
                        fig.update_traces(width=0.8)
                    else:
                        fig = px.box(
                            df_plot,
                            x='momento_display',
                            y=var_col,
                            color='momento',
                            facet_col='genero_par_experto_base',
                            title=f'📊 {var_name}',
                            color_discrete_map={
                                'pre_2024': '#FF6B6B',
                                'post_2024': '#4ECDC4',
                                'post_2025': '#A8E6CF'
                            },
                            points="outliers",
                            category_orders={'momento_display': momento_order},
                            labels={'genero_par_experto_base': 'Género'}
                        )
                else:
                    if tipo_grafico == 'Violin Plot':
                        fig = px.violin(
                            df_plot,
                            x='momento_display',
                            y=var_col,
                            color='momento',
                            title=f'📊 {var_name}',
                            color_discrete_map={
                                'pre_2024': '#FF6B6B',
                                'post_2024': '#4ECDC4',
                                'post_2025': '#A8E6CF'
                            },
                            box=True,
                            points='outliers',
                            category_orders={'momento_display': momento_order},
                            violinmode='overlay'
                        )
                        fig.update_traces(width=0.8)
                    else:
                        fig = px.box(
                            df_plot,
                            x='momento_display',
                            y=var_col,
                            color='momento',
                            title=f'📊 {var_name}',
                            color_discrete_map={
                                'pre_2024': '#FF6B6B',
                                'post_2024': '#4ECDC4',
                                'post_2025': '#A8E6CF'
                            },
                            points="outliers",
                            category_orders={'momento_display': momento_order}
                        )
                
                if tipo_grafico == 'Box Plot':
                    fig.update_traces(width=0.6)
                
                # Ajustar altura si hay comparación de géneros
                altura = 450 if not ('comparar_generos' in locals() and comparar_generos) else 400
                
                # Si hay comparación de géneros, actualizar las etiquetas de las facetas
                if 'comparar_generos' in locals() and comparar_generos:
                    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1].title(), y=0.975))
                
                fig.update_layout(
                    showlegend=False,
                    height=altura,
                    xaxis_title="",
                    yaxis_title="",
                    font=dict(size=12, color='#2c3e50'),
                    plot_bgcolor='white',
                    paper_bgcolor='#f8f9fa',
                    margin=dict(t=60, b=40, l=60, r=20),
                    title=dict(
                        font=dict(size=16, color='#2c3e50', family='Arial, sans-serif'),
                        x=0.5,
                        xanchor='center'
                    ),
                    xaxis=dict(
                        showgrid=False,
                        tickfont=dict(size=11, color='#5a6c7d'),
                        linecolor='#dee2e6',
                        linewidth=1
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridwidth=1,
                        gridcolor='#e9ecef',
                        tickfont=dict(size=11, color='#5a6c7d'),
                        linecolor='#dee2e6',
                        linewidth=1
                    ),
                    boxgap=0.2,
                    boxgroupgap=0.1
                )
                st.plotly_chart(fig, use_container_width=True, config=config)
    
    st.markdown("---")
    
    # Análisis de Categorías y Transiciones
    st.header("🏆 Análisis por Categorías")
    
    if 'categoria_2024_base' in df.columns and 'categoria_2025_base' in df.columns:
        # Análisis de transiciones de categoría
        df_categorias = df[df['momento'].isin(['post_2024', 'post_2025'])].copy()
        
        # Si comparar_generos está activo, mostrar gráficos separados por género
        if 'comparar_generos' in locals() and comparar_generos and 'genero_par_experto_base' in df.columns:
            generos = sorted(df['genero_par_experto_base'].dropna().unique().tolist())
            
            for genero in generos:
                st.subheader(f"📊 {genero.title()}")
                df_genero = df[df['genero_par_experto_base'] == genero]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Distribución por categoría en cada momento
                    st.markdown("**Distribución por Categoría**")
                    
                    # Obtener conteos únicos de participantes por categoría y momento
                    cat_pre_2024 = df_genero[df_genero['momento'] == 'pre_2024'].groupby('categoria_2024_base')['cedula_asistencia'].nunique()
                    cat_post_2024 = df_genero[df_genero['momento'] == 'post_2024'].groupby('categoria_2024_base')['cedula_asistencia'].nunique()
                    cat_post_2025 = df_genero[df_genero['momento'] == 'post_2025'].groupby('categoria_2025_base')['cedula_asistencia'].nunique()
                    
                    fig_cat = go.Figure()
                    fig_cat.add_trace(go.Bar(
                        name='Pre 2024',
                        x=cat_pre_2024.index,
                        y=cat_pre_2024.values,
                        marker_color='#FF6B6B'
                    ))
                    fig_cat.add_trace(go.Bar(
                        name='Post 2024',
                        x=cat_post_2024.index,
                        y=cat_post_2024.values,
                        marker_color='#4ECDC4'
                    ))
                    fig_cat.add_trace(go.Bar(
                        name='Post 2025',
                        x=cat_post_2025.index,
                        y=cat_post_2025.values,
                        marker_color='#A8E6CF'
                    ))
                    fig_cat.update_layout(
                        barmode='group',
                        height=350,
                        plot_bgcolor='white',
                        paper_bgcolor='#f8f9fa',
                        xaxis_title="",
                        yaxis_title="Cantidad de Participantes Únicos"
                    )
                    st.plotly_chart(fig_cat, use_container_width=True, config=config)
                
                with col2:
                    # Matriz de transiciones
                    st.markdown("**Transiciones de Categoría 2024→2025**")
                    transiciones = df_genero.groupby(['categoria_2024_base', 'categoria_2025_base']).size().reset_index(name='count')
                    
                    if not transiciones.empty:
                        # Crear listas únicas de nodos
                        nodos_origen = transiciones['categoria_2024_base'].unique().tolist()
                        nodos_destino = transiciones['categoria_2025_base'].unique().tolist()
                        todos_nodos = nodos_origen + [n for n in nodos_destino if n not in nodos_origen]
                        
                        fig_sankey = go.Figure(data=[go.Sankey(
                            node=dict(
                                pad=15,
                                thickness=20,
                                label=todos_nodos,
                                color='#4ECDC4'
                            ),
                            link=dict(
                                source=[todos_nodos.index(x) for x in transiciones['categoria_2024_base']],
                                target=[todos_nodos.index(x) for x in transiciones['categoria_2025_base']],
                                value=transiciones['count']
                            ),
                            textfont=dict(color='black', size=14, family='Arial, sans-serif')
                        )])
                        fig_sankey.update_layout(
                            height=350, 
                            paper_bgcolor='#f8f9fa',
                            font=dict(size=14, color='black', family='Arial, sans-serif')
                        )
                        st.plotly_chart(fig_sankey, use_container_width=True, config=config)
                    else:
                        st.info(f"No hay datos de transiciones para {genero}")
                
                st.markdown("---")
        
        else:
            # Vista normal sin comparación de géneros
            col1, col2 = st.columns(2)
            
            with col1:
                # Distribución por categoría en cada momento
                st.subheader("Distribución por Categoría")
                
                # Obtener conteos únicos de participantes por categoría y momento
                cat_pre_2024 = df[df['momento'] == 'pre_2024'].groupby('categoria_2024_base')['cedula_asistencia'].nunique()
                cat_post_2024 = df[df['momento'] == 'post_2024'].groupby('categoria_2024_base')['cedula_asistencia'].nunique()
                cat_post_2025 = df[df['momento'] == 'post_2025'].groupby('categoria_2025_base')['cedula_asistencia'].nunique()
                
                fig_cat = go.Figure()
                fig_cat.add_trace(go.Bar(
                    name='Pre 2024',
                    x=cat_pre_2024.index,
                    y=cat_pre_2024.values,
                    marker_color='#FF6B6B'
                ))
                fig_cat.add_trace(go.Bar(
                    name='Post 2024',
                    x=cat_post_2024.index,
                    y=cat_post_2024.values,
                    marker_color='#4ECDC4'
                ))
                fig_cat.add_trace(go.Bar(
                    name='Post 2025',
                    x=cat_post_2025.index,
                    y=cat_post_2025.values,
                    marker_color='#A8E6CF'
                ))
                fig_cat.update_layout(
                    barmode='group',
                    height=350,
                    plot_bgcolor='white',
                    paper_bgcolor='#f8f9fa',
                    xaxis_title="",
                    yaxis_title="Cantidad de Participantes Únicos"
                )
                st.plotly_chart(fig_cat, use_container_width=True, config=config)
            
            with col2:
                # Matriz de transiciones
                st.subheader("Transiciones de Categoría 2024→2025")
                transiciones = df.groupby(['categoria_2024_base', 'categoria_2025_base']).size().reset_index(name='count')
                
                if not transiciones.empty:
                    # Crear listas únicas de nodos
                    nodos_origen = transiciones['categoria_2024_base'].unique().tolist()
                    nodos_destino = transiciones['categoria_2025_base'].unique().tolist()
                    todos_nodos = nodos_origen + [n for n in nodos_destino if n not in nodos_origen]
                    
                    fig_sankey = go.Figure(data=[go.Sankey(
                        node=dict(
                            pad=15,
                            thickness=20,
                            label=todos_nodos,
                            color='#4ECDC4'
                        ),
                        link=dict(
                            source=[todos_nodos.index(x) for x in transiciones['categoria_2024_base']],
                            target=[todos_nodos.index(x) for x in transiciones['categoria_2025_base']],
                            value=transiciones['count']
                        ),
                        textfont=dict(color='black', size=14, family='Arial, sans-serif')
                    )])
                fig_sankey.update_layout(
                    height=350, 
                    paper_bgcolor='#f8f9fa',
                    font=dict(size=14, color='black', family='Arial, sans-serif')
                )
                st.plotly_chart(fig_sankey, use_container_width=True, config=config)    
    st.markdown("---")
    
    # Análisis de mejora individual
    st.header(" 📈 Análisis de Cambios Individuales")
    
    if 'comparar_generos' in locals() and comparar_generos and 'genero_par_experto_base' in df.columns:
        generos = sorted(df['genero_par_experto_base'].dropna().unique().tolist())
        
        for genero in generos:
            st.subheader(f"📊 {genero.title()}")
            df_genero = df[df['genero_par_experto_base'] == genero]
            
            # Crear dataframe pivot para calcular cambios
            df_pivot = df_genero.pivot_table(
                index='cedula_asistencia',
                columns='momento',
                values=['puntaje_PC', 'autoeficacia_pc', 'autoeficacia_pedagogica', 'apoyo', 'frustracion', 'redes_inter', 'trabajo_colaborativo']
            )
            
            # Tabs para diferentes comparaciones
            tab1, tab2, tab3 = st.tabs(["Pre → Post 2024", "Post 2024 → Post 2025", "Pre → Post 2025"])
            
            with tab1:
                st.markdown("**Cambios de Pre 2024 a Post 2024**")
                mejora_data = []
                for col in ['puntaje_PC', 'autoeficacia_pc', 'autoeficacia_pedagogica', 'apoyo', 'frustracion', 'redes_inter', 'trabajo_colaborativo']:
                    if ('post_2024' in df_pivot[col].columns) and ('pre_2024' in df_pivot[col].columns):
                        cambio = df_pivot[col]['post_2024'] - df_pivot[col]['pre_2024']
                        mejoraron = (cambio > 0).sum()
                        empeoraron = (cambio < 0).sum()
                        sin_cambio = (cambio == 0).sum()
                        
                        mejora_data.append({
                            'Variable': col,
                            'Mejoraron': mejoraron,
                            'Empeoraron': empeoraron,
                            'Sin Cambio': sin_cambio
                        })
                
                if mejora_data:
                    df_mejora = pd.DataFrame(mejora_data)
                    st.dataframe(df_mejora, use_container_width=True)
                else:
                    st.info("No hay datos suficientes para esta comparación")
            
            with tab2:
                st.markdown("**Cambios de Post 2024 a Post 2025**")
                mejora_data = []
                for col in ['puntaje_PC', 'autoeficacia_pc', 'autoeficacia_pedagogica', 'apoyo', 'frustracion', 'redes_inter', 'trabajo_colaborativo']:
                    if ('post_2025' in df_pivot[col].columns) and ('post_2024' in df_pivot[col].columns):
                        cambio = df_pivot[col]['post_2025'] - df_pivot[col]['post_2024']
                        mejoraron = (cambio > 0).sum()
                        empeoraron = (cambio < 0).sum()
                        sin_cambio = (cambio == 0).sum()
                        
                        mejora_data.append({
                            'Variable': col,
                            'Mejoraron': mejoraron,
                            'Empeoraron': empeoraron,
                            'Sin Cambio': sin_cambio
                        })
                
                if mejora_data:
                    df_mejora = pd.DataFrame(mejora_data)
                    st.dataframe(df_mejora, use_container_width=True)
                else:
                    st.info("No hay datos suficientes para esta comparación")
            
            with tab3:
                st.markdown("**Cambios totales de Pre 2024 a Post 2025**")
                mejora_data = []
                for col in ['puntaje_PC', 'autoeficacia_pc', 'autoeficacia_pedagogica', 'apoyo', 'frustracion', 'redes_inter', 'trabajo_colaborativo']:
                    if ('post_2025' in df_pivot[col].columns) and ('pre_2024' in df_pivot[col].columns):
                        cambio = df_pivot[col]['post_2025'] - df_pivot[col]['pre_2024']
                        mejoraron = (cambio > 0).sum()
                        empeoraron = (cambio < 0).sum()
                        sin_cambio = (cambio == 0).sum()
                        
                        mejora_data.append({
                            'Variable': col,
                            'Mejoraron': mejoraron,
                            'Empeoraron': empeoraron,
                            'Sin Cambio': sin_cambio
                        })
                
                if mejora_data:
                    df_mejora = pd.DataFrame(mejora_data)
                    st.dataframe(df_mejora, use_container_width=True)
                else:
                    st.info("No hay datos suficientes para esta comparación")
            
            st.markdown("---")
    
    else:
        # Crear dataframe pivot para calcular cambios
        df_pivot = df.pivot_table(
            index='cedula_asistencia',
            columns='momento',
            values=['puntaje_PC','autoeficacia_pc', 'autoeficacia_pedagogica', 'apoyo', 'frustracion', 'redes_inter', 'trabajo_colaborativo']
        )
        
        # Tabs para diferentes comparaciones
        tab1, tab2, tab3 = st.tabs(["Pre → Post 2024", "Post 2024 → Post 2025", "Pre → Post 2025"])
        
        with tab1:
            st.subheader("Cambios de Pre 2024 a Post 2024")
            mejora_data = []
            for col in ['puntaje_PC','autoeficacia_pc', 'autoeficacia_pedagogica', 'apoyo', 'frustracion', 'redes_inter', 'trabajo_colaborativo']:
                if ('post_2024' in df_pivot[col].columns) and ('pre_2024' in df_pivot[col].columns):
                    cambio = df_pivot[col]['post_2024'] - df_pivot[col]['pre_2024']
                    mejoraron = (cambio > 0).sum()
                    empeoraron = (cambio < 0).sum()
                    sin_cambio = (cambio == 0).sum()
                    
                    mejora_data.append({
                        'Variable': col,
                        'Mejoraron': mejoraron,
                        'Empeoraron': empeoraron,
                        'Sin Cambio': sin_cambio
                    })
            
            if mejora_data:
                df_mejora = pd.DataFrame(mejora_data)
                st.dataframe(df_mejora, use_container_width=True)
            else:
                st.info("No hay datos suficientes para esta comparación")
        
        with tab2:
            st.subheader("Cambios de Post 2024 a Post 2025")
            mejora_data = []
            for col in ['puntaje_PC', 'autoeficacia_pc', 'autoeficacia_pedagogica', 'apoyo', 'frustracion', 'redes_inter', 'trabajo_colaborativo']:
                if ('post_2025' in df_pivot[col].columns) and ('post_2024' in df_pivot[col].columns):
                    cambio = df_pivot[col]['post_2025'] - df_pivot[col]['post_2024']
                    mejoraron = (cambio > 0).sum()
                    empeoraron = (cambio < 0).sum()
                    sin_cambio = (cambio == 0).sum()
                    
                    mejora_data.append({
                        'Variable': col,
                        'Mejoraron': mejoraron,
                        'Empeoraron': empeoraron,
                        'Sin Cambio': sin_cambio
                    })
            
            if mejora_data:
                df_mejora = pd.DataFrame(mejora_data)
                st.dataframe(df_mejora, use_container_width=True)
            else:
                st.info("No hay datos suficientes para esta comparación")
        
        with tab3:
            st.subheader("Cambios totales de Pre 2024 a Post 2025")
            mejora_data = []
            for col in ['puntaje_PC', 'autoeficacia_pc', 'autoeficacia_pedagogica', 'apoyo', 'frustracion', 'redes_inter', 'trabajo_colaborativo']:
                if ('post_2025' in df_pivot[col].columns) and ('pre_2024' in df_pivot[col].columns):
                    cambio = df_pivot[col]['post_2025'] - df_pivot[col]['pre_2024']
                    mejoraron = (cambio > 0).sum()
                    empeoraron = (cambio < 0).sum()
                    sin_cambio = (cambio == 0).sum()
                    
                    mejora_data.append({
                        'Variable': col,
                        'Mejoraron': mejoraron,
                        'Empeoraron': empeoraron,
                        'Sin Cambio': sin_cambio
                    })
            
            if mejora_data:
                df_mejora = pd.DataFrame(mejora_data)
                st.dataframe(df_mejora, use_container_width=True)
            else:
                st.info("No hay datos suficientes para esta comparación")
    
    st.markdown("---")
    
    # Tabla de datos completa
    st.header("📋 Datos Completos")
    st.dataframe(df, use_container_width=True)
    
    

except Exception as e:
    st.error(f"Error al cargar los datos: {str(e)}")
    st.info("Por favor, verifica que el enlace del CSV sea correcto y esté accesible.")


st.markdown("---")
st.write("© 2025 Colombia Programa - Ministerio de Tecnologías de la Información y las Comunicaciones (MinTIC)")

# Formatear el HTML con las imágenes convertidas a base64
formatted_footer = FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64)

# Mostrar el footer en Streamlit
st.markdown(formatted_footer, unsafe_allow_html=True)