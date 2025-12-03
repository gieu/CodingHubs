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
import os
DEPLOY_ENV = os.getenv("DEPLOY_ENV")
if DEPLOY_ENV == "prod":
    CSV_URL_1 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSTLuxj-RqePc75D27B2W46pcaZUZG3Zrzm7SrigMbvfW6GR8rSZNG5l-e7vsuaZA/pub?output=csv"
else:
    CSV_URL_1 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSTLuxj-RqePc75D27B2W46pcaZUZG3Zrzm7SrigMbvfW6GR8rSZNG5l-e7vsuaZA/pub?output=csv"

# --- Cargar Datos con Cache ---
@st.cache_data(ttl=600)
def load_data(file):
    df = pd.read_csv(file, low_memory=False)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data(CSV_URL_1)
    
    # Convertir columnas numéricas a tipo numérico
    columnas_numericas = ['puntaje_PC', 'conceptos_habilidades', 'problemas_comp', 'año_nacimiento']
    
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Limpiar y preparar datos - mantener el año para diferenciar post_2024 y post_2025
    # Crear una columna más legible para visualización
    df['momento_display'] = df['momento'].str.replace('_', ' ').str.title()
    
    # Normalizar nombres de grados (combinar variantes con y sin tilde)
    if 'grado' in df.columns:
        df['grado'] = df['grado'].replace({
            'Sexto  ': 'Sexto',
            'Septimo': 'Séptimo',
            'Decimo': 'Décimo',
            'Undecimo': 'Undécimo'
        })
    
    # Filtros
    st.header("🔍 Filtros")
    
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    
    with col_filtro1:
        # Filtro de sexo
        if 'sexo' in df.columns:
            sexos_disponibles = ['Todos', 'Comparar ambos'] + sorted(df['sexo'].dropna().unique().tolist())
            sexo_seleccionado = st.selectbox(
                "Seleccionar sexo:",
                options=sexos_disponibles,
                index=0,
                key='filtro_sexo'
            )
            
            # Aplicar filtro
            if sexo_seleccionado == 'Comparar ambos':
                comparar_sexos = True
            elif sexo_seleccionado != 'Todos':
                df = df[df['sexo'] == sexo_seleccionado]
                comparar_sexos = False
            else:
                comparar_sexos = False
    
    with col_filtro2:
        # Filtro de nivel
        if 'nivel' in df.columns:
            niveles_disponibles = ['Todos'] + sorted(df['nivel'].dropna().unique().tolist())
            nivel_seleccionado = st.selectbox(
                "Seleccionar nivel:",
                options=niveles_disponibles,
                index=0,
                key='filtro_nivel'
            )
            
            # Aplicar filtro
            if nivel_seleccionado != 'Todos':
                df = df[df['nivel'] == nivel_seleccionado]
    
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
    if 'sexo_seleccionado' in locals():
        if sexo_seleccionado == 'Comparar ambos':
            filtros_activos.append("**Sexo:** Comparando ambos")
        elif sexo_seleccionado != 'Todos':
            filtros_activos.append(f"**Sexo:** {sexo_seleccionado}")
    
    if 'nivel_seleccionado' in locals() and nivel_seleccionado != 'Todos':
        filtros_activos.append(f"**Nivel:** {nivel_seleccionado}")
    
    if filtros_activos:
        st.info("📊 Filtros aplicados: " + " | ".join(filtros_activos))
    
    st.markdown("---")
    
    # Métricas generales
    st.header("📈 Resumen General")
    
    if 'comparar_sexos' in locals() and comparar_sexos and 'sexo' in df.columns:
        sexos = sorted(df['sexo'].dropna().unique().tolist())
        
        for sexo in sexos:
            st.subheader(f"📊 {sexo}")
            df_sexo = df[df['sexo'] == sexo]
            
            col1, col2 = st.columns(2)
            
            with col1:
                total_instituciones = df_sexo['codigo_ie'].nunique()
                st.metric("Total Instituciones", total_instituciones)
            
            with col2:
                momentos_unicos = df_sexo['momento'].nunique()
                st.metric("Momentos de Medición", momentos_unicos)
            
            st.markdown("---")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            total_instituciones = df['codigo_ie'].nunique()
            st.metric("Total Instituciones", total_instituciones)
        
        with col2:
            momentos_unicos = df['momento'].nunique()
            st.metric("Momentos de Medición", momentos_unicos)
        
        st.markdown("---")
    
    # Análisis por momento
    st.header("📊 Evolución Temporal: Pre 2024 → Post 2024 → Post 2025")
    
    if 'comparar_sexos' in locals() and comparar_sexos and 'sexo' in df.columns:
        sexos = sorted(df['sexo'].dropna().unique().tolist())
        
        for sexo in sexos:
            st.subheader(f"📊 {sexo}")
            df_sexo = df[df['sexo'] == sexo]
            
            # Promedio por momento
            momento_stats = df_sexo.groupby('momento').agg({
                'puntaje_PC': 'mean',
                'conceptos_habilidades': 'mean',
                'problemas_comp': 'mean'
            }).round(2)

            # Ordenar por momento cronológico
            orden_momentos = ['pre_2024', 'post_2024', 'post_2025']
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
            'conceptos_habilidades': 'mean',
            'problemas_comp': 'mean'
        }).round(2)

        # Ordenar por momento cronológico
        orden_momentos = ['pre_2024', 'post_2024', 'post_2025']
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
        'conceptos_habilidades': 'Conceptos y Habilidades',
        'problemas_comp': 'Problemas Computacionales'
    }

    # Preparar datos una sola vez
    df_plot = df.copy()
    df_plot['momento_display'] = df_plot['momento'].str.replace('_', ' ').str.title()
    
    # Crear grid de 2 columnas para los box plots
    var_items = list(variables.items())
    for i in range(0, len(var_items), 2):
        col1, col2 = st.columns(2)
        
        with col1:
            var_col, var_name = var_items[i]
            
            # Si comparar_sexos está activo y existe la columna de género
            if 'comparar_sexos' in locals() and comparar_sexos and 'sexo' in df_plot.columns:
                if tipo_grafico == 'Violin Plot':
                    fig = px.violin(
                        df_plot,
                        x='momento_display',
                        y=var_col,
                        color='momento',
                        facet_col='sexo',
                        title=f'📊 {var_name}',
                        color_discrete_map={
                            'pre_2024': '#FF6B6B',
                            'post_2024': '#4ECDC4',
                            'post_2025': '#A8E6CF'
                        },
                        box=True,
                        points='outliers',
                        category_orders={'momento_display': ['Pre 2024', 'Post 2024', 'Post 2025']},
                        labels={'sexo': 'Género'},
                        violinmode='overlay'
                    )
                    fig.update_traces(width=0.8)
                else:
                    fig = px.box(
                        df_plot,
                        x='momento_display',
                        y=var_col,
                        color='momento',
                        facet_col='sexo',
                        title=f'📊 {var_name}',
                        color_discrete_map={
                            'pre_2024': '#FF6B6B',
                            'post_2024': '#4ECDC4',
                            'post_2025': '#A8E6CF'
                        },
                        points="outliers",
                        category_orders={'momento_display': ['Pre 2024', 'Post 2024', 'Post 2025']},
                        labels={'sexo': 'Género'}
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
                        category_orders={'momento_display': ['Pre 2024', 'Post 2024', 'Post 2025']},
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
                        category_orders={'momento_display': ['Pre 2024', 'Post 2024', 'Post 2025']}
                    )
            
            if tipo_grafico == 'Box Plot':
                fig.update_traces(width=0.6)
            
            # Ajustar altura si hay comparación de géneros
            altura = 450 if not ('comparar_sexos' in locals() and comparar_sexos) else 400
            
            # Si hay comparación de géneros, actualizar las etiquetas de las facetas
            if 'comparar_sexos' in locals() and comparar_sexos:
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
                
                # Si comparar_sexos está activo y existe la columna de género
                if 'comparar_sexos' in locals() and comparar_sexos and 'sexo' in df_plot.columns:
                    if tipo_grafico == 'Violin Plot':
                        fig = px.violin(
                            df_plot,
                            x='momento_display',
                            y=var_col,
                            color='momento',
                            facet_col='sexo',
                            title=f'📊 {var_name}',
                            color_discrete_map={
                                'pre_2024': '#FF6B6B',
                                'post_2024': '#4ECDC4',
                                'post_2025': '#A8E6CF'
                            },
                            box=True,
                            points='outliers',
                            category_orders={'momento_display': ['Pre 2024', 'Post 2024', 'Post 2025']},
                            labels={'sexo': 'Género'},
                            violinmode='overlay'
                        )
                        fig.update_traces(width=0.8)
                    else:
                        fig = px.box(
                            df_plot,
                            x='momento_display',
                            y=var_col,
                            color='momento',
                            facet_col='sexo',
                            title=f'📊 {var_name}',
                            color_discrete_map={
                                'pre_2024': '#FF6B6B',
                                'post_2024': '#4ECDC4',
                                'post_2025': '#A8E6CF'
                            },
                            points="outliers",
                            category_orders={'momento_display': ['Pre 2024', 'Post 2024', 'Post 2025']},
                            labels={'sexo': 'Género'}
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
                            category_orders={'momento_display': ['Pre 2024', 'Post 2024', 'Post 2025']},
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
                            category_orders={'momento_display': ['Pre 2024', 'Post 2024', 'Post 2025']}
                        )
                
                if tipo_grafico == 'Box Plot':
                    fig.update_traces(width=0.6)
                
                # Ajustar altura si hay comparación de géneros
                altura = 450 if not ('comparar_sexos' in locals() and comparar_sexos) else 400
                
                # Si hay comparación de géneros, actualizar las etiquetas de las facetas
                if 'comparar_sexos' in locals() and comparar_sexos:
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
    
    # Análisis por grado
    st.header("🏫 Análisis por Grado")
    
    if 'grado' in df.columns:
        if 'comparar_sexos' in locals() and comparar_sexos and 'sexo' in df.columns:
            sexos = sorted(df['sexo'].dropna().unique().tolist())
            
            for sexo in sexos:
                st.subheader(f"📊 {sexo}")
                df_sexo_grado = df[df['sexo'] == sexo]
                
                # Distribución por grado en cada momento
                st.markdown("**Distribución por Grado y Momento**")
                
                # Obtener conteos de todos los estudiantes por grado y momento
                grado_pre = df_sexo_grado[df_sexo_grado['momento'] == 'pre_2024'].groupby('grado').size()
                grado_post_2024 = df_sexo_grado[df_sexo_grado['momento'] == 'post_2024'].groupby('grado').size()
                grado_post_2025 = df_sexo_grado[df_sexo_grado['momento'] == 'post_2025'].groupby('grado').size()
                
                # Orden de grados
                orden_grados = ['Tercero', 'Cuarto', 'Quinto', 'Sexto', 'Séptimo', 'Octavo', 'Noveno', 'Décimo', 'Undécimo']
                
                fig_grado = go.Figure()
                if not grado_pre.empty:
                    fig_grado.add_trace(go.Bar(
                        name='Pre 2024',
                        x=grado_pre.index,
                        y=grado_pre.values,
                        marker_color='#FF6B6B'
                    ))
                if not grado_post_2024.empty:
                    fig_grado.add_trace(go.Bar(
                        name='Post 2024',
                        x=grado_post_2024.index,
                        y=grado_post_2024.values,
                        marker_color='#4ECDC4'
                    ))
                if not grado_post_2025.empty:
                    fig_grado.add_trace(go.Bar(
                        name='Post 2025',
                        x=grado_post_2025.index,
                        y=grado_post_2025.values,
                        marker_color='#A8E6CF'
                    ))
                fig_grado.update_layout(
                    barmode='group',
                    height=400,
                    plot_bgcolor='white',
                    paper_bgcolor='#f8f9fa',
                    xaxis_title="Grado",
                    yaxis_title="Cantidad de Estudiantes",
                    xaxis={'categoryorder': 'array', 'categoryarray': orden_grados}
                )
                st.plotly_chart(fig_grado, use_container_width=True, config=config)
                
                st.markdown("---")
        
        else:
            # Vista normal sin comparación de sexos
            st.subheader("Distribución por Grado y Momento")
            
            # Obtener conteos de todos los estudiantes por grado y momento
            grado_pre = df[df['momento'] == 'pre_2024'].groupby('grado').size()
            grado_post_2024 = df[df['momento'] == 'post_2024'].groupby('grado').size()
            grado_post_2025 = df[df['momento'] == 'post_2025'].groupby('grado').size()
            
            # Orden de grados
            orden_grados = ['Tercero', 'Cuarto', 'Quinto', 'Sexto', 'Séptimo', 'Octavo', 'Noveno', 'Décimo', 'Undécimo']
            
            fig_grado = go.Figure()
            if not grado_pre.empty:
                fig_grado.add_trace(go.Bar(
                    name='Pre 2024',
                    x=grado_pre.index,
                    y=grado_pre.values,
                    marker_color='#FF6B6B'
                ))
            if not grado_post_2024.empty:
                fig_grado.add_trace(go.Bar(
                    name='Post 2024',
                    x=grado_post_2024.index,
                    y=grado_post_2024.values,
                    marker_color='#4ECDC4'
                ))
            if not grado_post_2025.empty:
                fig_grado.add_trace(go.Bar(
                    name='Post 2025',
                    x=grado_post_2025.index,
                    y=grado_post_2025.values,
                    marker_color='#A8E6CF'
                ))
            fig_grado.update_layout(
                barmode='group',
                height=400,
                plot_bgcolor='white',
                paper_bgcolor='#f8f9fa',
                xaxis_title="Grado",
                yaxis_title="Cantidad de Estudiantes",
                xaxis={'categoryorder': 'array', 'categoryarray': orden_grados}
            )
            st.plotly_chart(fig_grado, use_container_width=True, config=config)
    
    st.markdown("---")
    
    # Análisis de mejora individual
    st.header("📈 Análisis de Cambios Individuales")
    
    if 'comparar_sexos' in locals() and comparar_sexos and 'sexo' in df.columns:
        sexos = sorted(df['sexo'].dropna().unique().tolist())
        
        for sexo in sexos:
            st.subheader(f"📊 {sexo}")
            df_sexo_cambios = df[df['sexo'] == sexo]
            
            # Crear dataframe pivot para calcular cambios
            df_pivot = df_sexo_cambios.pivot_table(
                index='codigo_ie',
                columns='momento',
                values=['puntaje_PC', 'conceptos_habilidades', 'problemas_comp']
            )
            
            # Tabs para diferentes comparaciones
            tab1, tab2, tab3 = st.tabs(["Pre → Post 2024", "Post 2024 → Post 2025", "Pre → Post 2025"])
            
            with tab1:
                st.markdown("**Cambios de Pre 2024 a Post 2024**")
                mejora_data = []
                for col in ['puntaje_PC', 'conceptos_habilidades', 'problemas_comp']:
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
                for col in ['puntaje_PC', 'conceptos_habilidades', 'problemas_comp']:
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
                for col in ['puntaje_PC', 'conceptos_habilidades', 'problemas_comp']:
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
            index='codigo_ie',
            columns='momento',
            values=['puntaje_PC', 'conceptos_habilidades', 'problemas_comp']
        )
        
        # Tabs para diferentes comparaciones
        tab1, tab2, tab3 = st.tabs(["Pre → Post 2024", "Post 2024 → Post 2025", "Pre → Post 2025"])
        
        with tab1:
            st.subheader("Cambios de Pre 2024 a Post 2024")
            mejora_data = []
            for col in ['puntaje_PC', 'conceptos_habilidades', 'problemas_comp']:
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
            for col in ['puntaje_PC', 'conceptos_habilidades', 'problemas_comp']:
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
            for col in ['puntaje_PC', 'conceptos_habilidades', 'problemas_comp']:
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
