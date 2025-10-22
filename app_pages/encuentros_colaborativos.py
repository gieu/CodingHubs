import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from actions.chart_actions import graficador
from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import LOGO_NAVBAR_BASE64, HIDE_STREAMLIT_STYLE, NAVBAR_TEMPLATE, generar_css_personalizado
from utils.chart_config import get_chart_config
from constants.header_constants import header
# ==========================================
# CONFIGURACIÓN INICIAL
# ==========================================
chart_config = get_chart_config()

# ==========================================
# PALETA DE COLORES ESTÁNDAR
# ==========================================
# Colores principales del proyecto Colombia Programa
COLOR_PALETTE = {
    # Colores primarios
    'primary': '#1DB2E8',      # Azul principal
    'secondary': '#00A651',    # Verde Colombia
    'accent': '#FFB400',       # Amarillo Colombia
    'dark': '#2C3E50',         # Azul oscuro
    
    # Colores para gráficas
    'bar_single': '#1DB2E8',   # Azul para barras individuales
    'bar_positive': '#00A651', # Verde para valores positivos
    'bar_negative': '#E74C3C', # Rojo para valores negativos
    'pie_colors': ['#1DB2E8', '#00A651', '#FFB400', '#E74C3C', '#9B59B6', '#F39C12'],
    
    # Escalas de colores continuas
    'blue_scale': ['#E3F2FD', '#BBDEFB', '#90CAF9', '#64B5F6', '#42A5F5', '#2196F3', '#1E88E5', '#1976D2', '#1565C0', '#0D47A1'],
    'green_scale': ['#E8F5E8', '#C8E6C8', '#A5D6A7', '#81C784', '#66BB6A', '#4CAF50', '#43A047', '#388E3C', '#2E7D32', '#1B5E20'],
    # Colores categóricos
    'categorical': [
        '#1DB2E8',  # Azul
        '#00A651',  # Verde
        '#FFB400',  # Amarillo
        '#E74C3C',  # Rojo
        '#9B59B6',  # Morado
        '#F39C12',  # Naranja
        '#34495E',  # Gris azulado
        '#16A085',  # Verde azulado
        '#E67E22',  # Naranja oscuro
        '#8E44AD'   # Morado oscuro
    ],
    
    # Colores especiales
    'success': '#27AE60',      # Verde éxito
    'warning': '#F39C12',      # Naranja advertencia
    'danger': '#E74C3C',       # Rojo peligro
    'info': '#3498DB',         # Azul información
    
    # Colores para tipos de datos específicos
    'gender_colors': {
        'Masculino': "#119713",
        'Femenino': "#FA960B",
        'Otro': '#9C27B0'
    },
    'yes_no_colors': {
        'Sí': '#00A651',
        'No': '#E74C3C'
    }
}

# Escalas de colores para Plotly
PLOTLY_COLOR_SCALES = {
    'primary': [[0, '#E3F2FD'], [1, '#1DB2E8']],
    'success': [[0, '#E8F5E8'], [1, '#00A651']],
    'warning': [[0, '#FFF8E1'], [1, '#FFB400']],
    'viridis_custom': ['#440154', '#482777', '#3F4A8A', '#31678E', '#26838F', '#1F9D8A', '#6CCE5A', '#B6DE2B', '#FEE825']
}

# Ocultar elementos de Streamlit
st.markdown(HIDE_STREAMLIT_STYLE, unsafe_allow_html=True)

# Generar el CSS personalizado con el color deseado
color_fondo_navbar = "#00A651"  # Verde para distinguir esta página
custom_css = generar_css_personalizado(color_fondo_navbar)

# Aplicar el CSS en Streamlit
st.markdown(custom_css, unsafe_allow_html=True)

# Crear navbar
header()
# ==========================================
# CARGA DE DATOS
# ==========================================
# URL del CSV

@st.cache_data(ttl=600)
def load_data(file):
    """Cargar datos desde URL"""
    try:
        df = pd.read_csv(file, encoding='utf-8')
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return pd.DataFrame()

# ==========================================
# FUNCIONES DE DASHBOARDS ENFOCADOS EN COLABORACIÓN
# ==========================================

def hallazgos_generales():
    st.markdown("---")
    st.header("📊 Mapa de Calor - Conductas-Momentos")
    
    # Selector de fase al inicio
    st.subheader("🔍 Selección de Fase")
    
    # Cargar datos temporalmente para obtener las fases disponibles
    url="https://docs.google.com/spreadsheets/d/e/2PACX-1vQzYORLJ_nV7qv_vP2hrWmdV8Sm2rOpQPSNH9WLKJkJoHyfIOgBsrJu-uh-6_MYDg/pub?output=csv"
    df_temp = load_data(url)
    
    if not df_temp.empty and 'Fase' in df_temp.columns:
        fases_disponibles = sorted(df_temp['Fase'].dropna().unique())
        # Agregar opción "Todas las fases"
        opciones_fase = ["Todas las fases"] + list(fases_disponibles)
        
        fase_seleccionada = st.selectbox(
            "Selecciona la fase a analizar:",
            options=opciones_fase,
            help="Escoge la fase específica que deseas analizar en todos los gráficos, o selecciona 'Todas las fases' para incluir ambas"
        )
        
        st.markdown("---")
        st.info(f"📋 **Análisis para: {fase_seleccionada}**")
    else:
        st.warning("No se encontró la columna 'Fase' en los datos o los datos están vacíos.")
        return
    
    # Cargar y filtrar datos por fase seleccionada
    df = load_data(url)
    if not df.empty and 'Fase' in df.columns:
        if fase_seleccionada == "Todas las fases":
            # No filtrar, mantener todas las fases
            df = df.copy()
        else:
            # Filtrar por la fase específica seleccionada
            df = df[df['Fase'] == fase_seleccionada].copy()
    else:
        st.error("No se pudo filtrar por fase. Verifica que los datos contengan la columna 'Fase'.")
        return
    
    if df.empty:
        st.warning("No hay datos válidos para el mapa de calor.")
        return
    
    # Verificar que las columnas necesarias existen
    required_columns = ['Número de momento', 'tipo', 'participante', 'Conducta']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"Columnas faltantes en los datos: {missing_columns}")
        st.info("Las columnas disponibles son: " + ", ".join(df.columns.tolist()))
        return
    
    # Limpiar espacios en blanco en la columna Conducta
    df['Conducta'] = df['Conducta'].astype(str).str.strip()
    
    # Filtrar INCLUYENDO solo las Conductas específicas
    Conductas_permitidas = ['Transferencia de la experticia', 'Instrucción centrada en el estudiante', 'Enfoque de género']
    df_filtered = df[
        (df['Conducta'].isin(Conductas_permitidas))
    ].copy()
    
    # Filtrar para que solo aparezca un Encuentro único por cada tipo y número de momento
    df_filtered = df_filtered.drop_duplicates(subset=['Encuentro', 'tipo', 'Número de momento','Fase'])
    if df_filtered.empty:
        st.warning("No hay datos válidos después de aplicar los filtros.")
        st.info(f"Valores únicos en 'Conducta' (limpiados): {df['Conducta'].unique().tolist()}")
        st.info(f"Conductas buscadas: {Conductas_permitidas}")
        return
    # Usar directamente la columna "Número de momento"
    # Crear una tabla de frecuencias para el mapa de calor
    heatmap_data = df_filtered.groupby(['Número de momento', 'tipo']).size().reset_index(name='Frecuencia')
    
    # Crear tabla pivote para el mapa de calor
    pivot_data = heatmap_data.pivot(index='tipo', columns='Número de momento', values='Frecuencia').fillna(0)
    
    if pivot_data.empty:
        st.warning("No hay suficientes datos para generar el mapa de calor.")
        return
    

    # Generar mapa de calor
    fig_heatmap = px.imshow(
        pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        color_continuous_scale=COLOR_PALETTE['green_scale'],
        title="Frecuencia de Conductas por Momento",
        labels=dict(x="Momento", y="Conductas", color="Frecuencia"),
        aspect="auto"
    )
    
    # Personalizar el diseño
    fig_heatmap.update_layout(
        height=700, 
        yaxis_title="Conductas",
        font=dict(size=16),  # Aumentar tamaño de fuente general
        xaxis=dict(
            tickmode='array',
            tickvals=list(pivot_data.columns),
            ticktext=[str(int(x)) for x in pivot_data.columns],
            dtick=1, 
            tickfont=dict(size=14)  # Tamaño específico para labels del eje X
        ),
        yaxis=dict(
            tickfont=dict(size=14)  # Tamaño específico para labels del eje Y
        ),
        title=dict(
            font=dict(size=18)  # Tamaño del título
        )
    )
    
    # Añadir valores en las celdas
    fig_heatmap.update_traces(
        text=pivot_data.values,
        texttemplate="%{text}",
        textfont={"size": 14}
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True, config=chart_config)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras: Frecuencia por momento (Conductas específicas)
        freq_por_momento = df_filtered.groupby('Número de momento').size().reset_index(name='Total_Observaciones')
        
        # Calcular el total general para obtener porcentajes
        total_general = freq_por_momento['Total_Observaciones'].sum()
        freq_por_momento['Porcentaje'] = (freq_por_momento['Total_Observaciones'] / total_general * 100).round(1)
        
        fig_bar_momentos = px.bar(
            freq_por_momento,
            x='Número de momento',
            y='Porcentaje',
            title="Porcentaje de conductas observadas por momento",
            labels={'Número de momento': 'Número de Momento', 'Porcentaje': 'Porcentaje (%)'},
            color='Porcentaje',
            color_continuous_scale=COLOR_PALETTE['green_scale'],
            text='Porcentaje'
        )
        fig_bar_momentos.update_traces(texttemplate='%{text}%', textposition='outside')
        fig_bar_momentos.update_layout(
            showlegend=False, 
            height=400,
            xaxis=dict(
            tickmode='linear',
            dtick=1  # Mostrar solo números enteros
            ),
            yaxis=dict(
            title="Porcentaje (%)",
            range=[0, max(freq_por_momento['Porcentaje']) * 1.1]
            )
        )
        st.plotly_chart(fig_bar_momentos, use_container_width=True, config=chart_config)
    with col2:
        # Gráfico de barras: Frecuencia por tipo (Conductas específicas)
        freq_por_tipo = df_filtered.groupby('tipo').size().reset_index(name='Total_Observaciones').sort_values('Total_Observaciones', ascending=True)
        
        fig_bar_tipos = px.bar(
            freq_por_tipo,
            x='Total_Observaciones',
            y='tipo',
            title="Frecuencia Total por Conducta",
            labels={'Total_Observaciones': 'Cantidad de Observaciones', 'tipo': 'Conducta'},
            color='Total_Observaciones',
            color_continuous_scale=COLOR_PALETTE['green_scale'],
            orientation='h',
            text='Total_Observaciones'
        )
        fig_bar_tipos.update_traces(texttemplate='%{text}', textposition='outside')
        fig_bar_tipos.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_bar_tipos, use_container_width=True, config=chart_config)
    
    
    df_puntos = df[ 
        (df['Conducta'].isin(['Transferencia de la experticia']))
    ].copy()
    
    # Gráfica de líneas: Momento vs Porcentaje de Encuentros por Participante
    st.subheader(" Análisis de Líneas: Transferencia de la Experticia por Participante y Momento")
    
    if not df_puntos.empty and 'Encuentro' in df_puntos.columns and 'participante' in df_puntos.columns and 'tipo' in df_puntos.columns:
        # Calcular el porcentaje por momento, participante y tipo
        max_encuentros = 9
        porcentaje_por_participante = []
        
        # Obtener todos los participantes únicos
        participantes_unicos = df_puntos['participante'].unique()
        tipos_unicos = df_puntos['tipo'].unique()
        momentos_completos = range(1, 5)  # Asegurar que tenemos todos los momentos del 1 al 9
        
        for tipo in tipos_unicos:
            for participante in participantes_unicos:
                df_subset = df_puntos[(df_puntos['participante'] == participante) & (df_puntos['tipo'] == tipo)]
                
                # Procesar TODOS los momentos, incluso si no hay datos
                for momento in momentos_completos: 
                    if not df_subset.empty and momento in df_subset['Número de momento'].values:
                        # Hay datos para este momento
                        encuentros_en_momento = df_subset[df_subset['Número de momento'] == momento]['Encuentro'].nunique()
                        porcentaje = round((encuentros_en_momento / max_encuentros) * 100, 1)
                        total_obs = len(df_subset[df_subset['Número de momento'] == momento])
                    else:
                        # No hay datos para este momento, usar 0
                        encuentros_en_momento = 0
                        porcentaje = 0.0
                        total_obs = 0
                    
                    porcentaje_por_participante.append({
                        'Participante': participante,
                        'Momento': momento,
                        'Tipo': tipo,
                        'Porcentaje_Encuentros': porcentaje,
                        'Encuentros_Activos': encuentros_en_momento,
                        'Total_Observaciones': total_obs
                    })
        
        df_lineas = pd.DataFrame(porcentaje_por_participante)
        
        if not df_lineas.empty:
            # Crear gráfico de líneas con facet_col
            fig_lineas = px.line(
                df_lineas,
                x='Momento',
                y='Porcentaje_Encuentros',
                color='Participante',
                facet_col='Tipo',
                title="Evolución del Porcentaje de Encuentros con Transferencia de Experticia por Participante y Tipo",
                labels={
                    'Momento': 'Momento',
                    'Porcentaje_Encuentros': 'Porcentaje de Encuentros (%)',
                    'Participante': 'Tipo de Participante',
                    'Tipo': 'Tipo de Comportamiento'
                },
                color_discrete_sequence=COLOR_PALETTE['categorical'],
                markers=True,
                hover_data=['Encuentros_Activos', 'Total_Observaciones']
            )
            
            # Personalizar el gráfico
            fig_lineas.update_traces(
                line=dict(width=3),
                marker=dict(size=8, line=dict(width=2, color='white'))
            )
            
            fig_lineas.update_layout(
                height=400,
                xaxis=dict(
                    tickmode='linear',
                    dtick=1,
                    title="Momento"
                ),
                yaxis=dict(
                    title="Porcentaje de Encuentros (%)",
                    range=[0, 100]
                ),
                legend=dict(
                    title="Tipo de Participante",
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.02
                ),
                hovermode='x unified'
            )
            
            # Actualizar títulos de facetas para mejor presentación
            fig_lineas.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            
            st.plotly_chart(fig_lineas, use_container_width=True, config=chart_config)
            
            # Mostrar tabla de datos y estadísticas
            
            st.subheader("📊 Datos por Tipo y Participante")
            
            # Obtener tipos únicos
            tipos_unicos = df_lineas['Tipo'].unique()
            num_tipos = len(tipos_unicos)
            
            # Distribuir en columnas según el número de tipos
            if num_tipos == 1:
                # Solo una tabla, usar todo el ancho
                tipo = tipos_unicos[0]
                st.write(f"**{tipo}:**")
                df_tipo = df_lineas[df_lineas['Tipo'] == tipo]
                tabla_tipo = df_tipo.pivot(index='Momento', columns='Participante', values='Porcentaje_Encuentros').fillna(0).round(1)
                st.dataframe(tabla_tipo, use_container_width=True)
            elif num_tipos == 2:
                # Dos columnas
                col1, col2 = st.columns(2)
                for i, tipo in enumerate(tipos_unicos):
                    with (col1 if i == 0 else col2):
                        st.write(f"**{tipo}:**")
                        df_tipo = df_lineas[df_lineas['Tipo'] == tipo]
                        tabla_tipo = df_tipo.pivot(index='Momento', columns='Participante', values='Porcentaje_Encuentros').fillna(0).round(1)
                        st.dataframe(tabla_tipo, use_container_width=True)
            elif num_tipos == 3:
                # Tres columnas
                col1, col2, col3 = st.columns(3)
                columnas = [col1, col2, col3]
                for i, tipo in enumerate(tipos_unicos):
                    with columnas[i]:
                        st.write(f"**{tipo}:**")
                        df_tipo = df_lineas[df_lineas['Tipo'] == tipo]
                        tabla_tipo = df_tipo.pivot(index='Momento', columns='Participante', values='Porcentaje_Encuentros').fillna(0).round(1)
                        st.dataframe(tabla_tipo, use_container_width=True)
            else:
                # Más de 3 tipos: usar 2 columnas y distribuir
                col1, col2 = st.columns(2)
                for i, tipo in enumerate(tipos_unicos):
                    with (col1 if i % 2 == 0 else col2):
                        st.write(f"**{tipo}:**")
                        df_tipo = df_lineas[df_lineas['Tipo'] == tipo]
                        tabla_tipo = df_tipo.pivot(index='Momento', columns='Participante', values='Porcentaje_Encuentros').fillna(0).round(1)
                        st.dataframe(tabla_tipo, use_container_width=True)
                        if i % 2 == 1 or i == len(tipos_unicos) - 1:  # Añadir espacio después de cada fila
                            st.write("")
        else:
            st.warning("No se pudieron calcular los porcentajes por participante y momento.")
    else:
        st.warning("No hay datos disponibles para 'Transferencia de la experticia' o faltan las columnas necesarias ('Encuentro', 'participante' o 'tipo').")
   
   
    url_2="https://docs.google.com/spreadsheets/d/e/2PACX-1vT7ngk1_bT8zj18I7yzTKeI74316aXaUvKgyx8ww8OzjL0l1_1ewFwcJqW3hBFyuw/pub?output=csv"
    df_2 = load_data(url_2)

    if df_2.empty:
        st.warning("No hay datos válidos para docentes por sexo.")
        return
    
    # Filtrar por fase seleccionada
    if 'Fase' in df_2.columns:
        if fase_seleccionada == "Todas las fases":
            # No filtrar, mantener todas las fases
            df_2 = df_2.copy()
        else:
            df_2 = df_2[df_2['Fase'] == fase_seleccionada].copy()
    else:
        st.warning("La columna 'Fase' no está disponible en el segundo conjunto de datos.")
        return
    # Verificar que las columnas necesarias existen
    required_columns = ['Número de momento', 'tipo', 'participante', 'Conducta']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"Columnas faltantes en los datos: {missing_columns}")
        st.info("Las columnas disponibles son: " + ", ".join(df_2.columns.tolist()))
        return
    
    # Limpiar espacios en blanco en la columna Conducta
    df_2['Conducta'] = df_2['Conducta'].astype(str).str.strip()

    # Y INCLUYENDO solo las Conductas específicas
    Conductas_permitidas = ['Transferencia de la experticia', 'Instrucción centrada en el estudiante', 'Enfoque de género']
    df_filtered_genero = df_2[
        (df_2['Conducta'].isin(Conductas_permitidas))
    ].copy()
    
    # Verificar si existe la columna 'sexo'
    if 'sexo' not in df_filtered_genero.columns:
        st.warning("La columna 'sexo' no está disponible en los datos.")
        st.info("Las columnas disponibles son: " + ", ".join(df_filtered_genero.columns.tolist()))
        return
    
    st.subheader("📊 Participación por Conducta y Género")
    
    col1, col2 = st.columns(2)

    with col1:
        # Calcular porcentaje de participación por tipo y género
        if not df_filtered_genero.empty:
            # Limpiar y estandarizar valores de género y participante
            df_filtered_genero['sexo'] = df_filtered_genero['sexo'].astype(str).str.strip().str.title()
            df_filtered_genero['participante'] = df_filtered_genero['participante'].astype(str).str.strip()
            
            # Obtener total de participantes únicos por tipo, género y participante
            participacion_por_tipo_genero = df_filtered_genero.groupby(['tipo', 'sexo'])['nombre'].nunique().reset_index()
            participacion_por_tipo_genero.columns = ['Tipo', 'Género', 'Participantes_Únicos']
            
            # Calcular total de participantes únicos por tipo y participante (para calcular porcentajes)
            total_por_tipo_participante = df_filtered_genero.groupby(['tipo'])['nombre'].nunique().reset_index()
            total_por_tipo_participante.columns = ['Tipo', 'Total_Participantes']
            
            # Fusionar datos para calcular porcentajes
            participacion_con_total = participacion_por_tipo_genero.merge(total_por_tipo_participante, on=['Tipo'])
            participacion_con_total['Porcentaje_Participacion'] = (
                participacion_con_total['Participantes_Únicos'] / 
                participacion_con_total['Total_Participantes'] * 100
            )
            
            # Crear gráfico de barras agrupadas
            fig_barras_genero = px.bar(
                participacion_con_total,
                x='Tipo',
                y='Porcentaje_Participacion',
                color='Género',
                title="Participación por Conducta y Género y todos los Participantes",
                labels={
                    'Porcentaje_Participacion': 'Porcentaje de Participación (%)',
                    'Tipo': 'Tipo de Conducta',
                    'Género': 'Género'
                },
                color_discrete_map=COLOR_PALETTE['gender_colors'],
                text='Porcentaje_Participacion',
                barmode='group'
            )
            
            # Personalizar el gráfico
            fig_barras_genero.update_traces(
                texttemplate='%{text:.1f}%',
                textposition='outside'
            )
            
            fig_barras_genero.update_layout(
                height=600,
                xaxis_title="Tipo de Conducta",
                yaxis_title="Porcentaje de Participación (%)",
                legend=dict(
                    title="Género",
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.02
                ),
                font=dict(size=12),
                yaxis=dict(range=[0, max(participacion_con_total['Porcentaje_Participacion']) * 1.1])
            )
            
            st.plotly_chart(fig_barras_genero, use_container_width=True, config=chart_config)
           
        
        else:
            st.warning("No hay datos válidos para crear la gráfica de participación por género.")

    with col2:
            # Calcular porcentaje de participación por tipo y género
        if not df_filtered_genero.empty:
            # Limpiar y estandarizar valores de género y participante
            df_filtered_genero['sexo'] = df_filtered_genero['sexo'].astype(str).str.strip().str.title()
            df_filtered_genero['participante'] = df_filtered_genero['participante'].astype(str).str.strip()
            
            # Obtener total de participantes únicos por tipo, género y participante
            participacion_por_tipo_genero = df_filtered_genero.groupby(['tipo', 'sexo', 'participante'])['nombre'].nunique().reset_index()
            participacion_por_tipo_genero.columns = ['Tipo', 'Género', 'Participante', 'Participantes_Únicos']
            
            # Calcular total de participantes únicos por tipo y participante (para calcular porcentajes)
            total_por_tipo_participante = df_filtered_genero.groupby(['tipo', 'participante'])['nombre'].nunique().reset_index()
            total_por_tipo_participante.columns = ['Tipo', 'Participante', 'Total_Participantes']
            
            # Fusionar datos para calcular porcentajes
            participacion_con_total = participacion_por_tipo_genero.merge(total_por_tipo_participante, on=['Tipo', 'Participante'])
            participacion_con_total['Porcentaje_Participacion'] = (
                participacion_con_total['Participantes_Únicos'] / 
                participacion_con_total['Total_Participantes'] * 100
            )
            
            # Crear gráfico de barras agrupadas
            fig_barras_genero = px.bar(
                participacion_con_total,
                x='Tipo',
                y='Porcentaje_Participacion',
                color='Género',
                title="Participación por Conducta y Género dividido por Participantes",
                labels={
                    'Porcentaje_Participacion': 'Porcentaje de Participación (%)',
                    'Tipo': 'Tipo de Conducta',
                    'Género': 'Género'
                },
                facet_row='Participante',
                color_discrete_map=COLOR_PALETTE['gender_colors'],
                text='Porcentaje_Participacion',
                barmode='group'
            )
            
            # Personalizar el gráfico
            fig_barras_genero.update_traces(
                texttemplate='%{text:.1f}%',
                textposition='outside'
            )
            
            fig_barras_genero.update_layout(
                height=600,
                xaxis_title="Tipo de Conducta",
                yaxis_title="Porcentaje de Participación (%)",
                legend=dict(
                    title="Género",
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.02
                ),
                font=dict(size=12),
                yaxis=dict(range=[0, max(participacion_con_total['Porcentaje_Participacion']) * 1.1])
            )
            
            st.plotly_chart(fig_barras_genero, use_container_width=True, config=chart_config)
            
        else:
            st.warning("No hay datos válidos para crear la gráfica de participación por género.")
    
    url_3="https://docs.google.com/spreadsheets/d/e/2PACX-1vSq4YCoKLIOBuBJGv-V4FwZLccdOOFYRjkrNsKrkME7tFeRSC15J2FFD2GjwgbwPg/pub?output=csv"
    df_3 = load_data(url_3)
    
    if not df_3.empty:
        # Filtrar por fase seleccionada
        if 'Fase' in df_3.columns:
            if fase_seleccionada == "Todas las fases":
                # No filtrar, mantener todas las fases
                df_3 = df_3.copy()
            else:
                df_3 = df_3[df_3['Fase'] == fase_seleccionada].copy()
        else:
            st.warning("La columna 'Fase' no está disponible en el tercer conjunto de datos.")
            return
        
        st.subheader("📊 Análisis de Fortalezas por Encuentro")
        
        # Verificar que las columnas necesarias existen
        required_columns_3 = ['Encuentro', 'pregunta', 'respuesta']
        missing_columns_3 = [col for col in required_columns_3 if col not in df_3.columns]
        
        if missing_columns_3:
            st.error(f"Columnas faltantes en los datos: {missing_columns_3}")
            st.info("Las columnas disponibles son: " + ", ".join(df_3.columns.tolist()))
        else:
            # Limpiar datos: eliminar filas con Encuentro vacío
            df_3_clean = df_3[df_3['Encuentro'].notna() & (df_3['Encuentro'] != '')].copy()
            
            # Filtrar solo las filas donde 'pregunta' contenga 'Fortaleza'
            df_3_clean = df_3_clean[df_3_clean['pregunta'].str.contains('Fortaleza', case=False, na=False)].copy()
            
            if df_3_clean.empty:
                st.warning("No hay datos válidos después de filtrar por 'Fortaleza'.")
                return
            
            # Extraer número del encuentro para ordenar correctamente
            df_3_clean['Encuentro_Num'] = df_3_clean['Encuentro'].str.extract(r'(\d+)').astype(int)
            
            # Crear identificador único considerando Encuentro + Fase para evitar duplicados entre fases
            if 'Fase' in df_3_clean.columns:
                df_3_clean['Encuentro_Fase_Unico'] = df_3_clean['Encuentro'].astype(str) + '_' + df_3_clean['Fase'].astype(str)
                # Contar encuentros únicos por respuesta considerando fase
                conteo_por_pregunta = df_3_clean.groupby('respuesta')['Encuentro_Fase_Unico'].nunique().reset_index()
            else:
                # Fallback si no hay columna Fase
                conteo_por_pregunta = df_3_clean.groupby('respuesta')['Encuentro'].nunique().reset_index()
            
            conteo_por_pregunta.columns = ['Respuesta', 'Numero_de_encuentros']
            # Función para tomar solo las primeras palabras
            def primeras_palabras(texto, num_palabras=3):
                palabras = texto.split()
                if len(palabras) > num_palabras:
                    return " ".join(palabras[:num_palabras]) + "..."
                return texto
            
            # Aplicar función a las respuestas
            conteo_por_pregunta['Respuesta_Corta'] = conteo_por_pregunta['Respuesta'].apply(lambda x: primeras_palabras(x, 3))
            
            # Ordenar por número de encuentros de mayor a menor
            conteo_por_pregunta = conteo_por_pregunta.sort_values('Numero_de_encuentros', ascending=True)
            
            # Crear el gráfico de barras horizontal
            fig_condiciones = px.bar(
                conteo_por_pregunta,
                x='Numero_de_encuentros',
                y='Respuesta_Corta',
                title="Número de Encuentros por Fortaleza",
                labels={
                    'Numero_de_encuentros': 'Número de encuentros',
                    'Respuesta_Corta': 'Fortaleza'
                },
                color='Numero_de_encuentros',
                color_continuous_scale=COLOR_PALETTE['blue_scale'],
                text='Numero_de_encuentros',
                orientation='h',
                hover_data={'Respuesta': True, 'Respuesta_Corta': False}  # Mostrar texto completo en hover
            )
            
            # Personalizar el gráfico
            fig_condiciones.update_traces(
                texttemplate='%{text}',
                textposition='outside'
            )
            
            fig_condiciones.update_layout(
                height=400,  # Aumentar altura del gráfico
                yaxis_title="Fortalezas",
                xaxis_title="Número de encuentros",
                showlegend=False,
                font=dict(size=12),
                xaxis=dict(
                    range=[0, max(conteo_por_pregunta['Numero_de_encuentros']) * 1.1]
                ),
                yaxis=dict(
                    tickfont=dict(size=10),  # Tamaño de fuente legible
                    automargin=True  # Ajuste automático de márgenes
                ),
                margin=dict(l=150, r=50, t=80, b=50)  # Márgenes ajustados para barras horizontales
            )
            
            st.plotly_chart(fig_condiciones, use_container_width=True, config=chart_config)
        
        
        
        st.subheader("📊 Análisis de Condiciones por Encuentro")
        
        # Verificar que las columnas necesarias existen
        required_columns_3 = ['Encuentro', 'pregunta', 'respuesta']
        missing_columns_3 = [col for col in required_columns_3 if col not in df_3.columns]
        
        if missing_columns_3:
            st.error(f"Columnas faltantes en los datos: {missing_columns_3}")
            st.info("Las columnas disponibles son: " + ", ".join(df_3.columns.tolist()))
        else:
            # Limpiar datos: eliminar filas con Encuentro vacío
            df_3_clean = df_3[df_3['Encuentro'].notna() & (df_3['Encuentro'] != '')].copy()
            
            # Filtrar solo las filas donde 'pregunta' contenga 'Condicion '
            df_3_clean = df_3_clean[df_3_clean['pregunta'].str.contains('Condicion', case=False, na=False)].copy()
            
            if df_3_clean.empty:
                st.warning("No hay datos válidos después de filtrar por 'Condicion '.")
                return
            
            # Extraer número del encuentro para ordenar correctamente
            df_3_clean['Encuentro_Num'] = df_3_clean['Encuentro'].str.extract(r'(\d+)').astype(int)
            
            # Crear identificador único considerando Encuentro + Fase para evitar duplicados entre fases
            if 'Fase' in df_3_clean.columns:
                df_3_clean['Encuentro_Fase_Unico'] = df_3_clean['Encuentro'].astype(str) + '_' + df_3_clean['Fase'].astype(str)
                # Contar encuentros únicos por respuesta considerando fase
                conteo_por_pregunta = df_3_clean.groupby('respuesta')['Encuentro_Fase_Unico'].nunique().reset_index()
            else:
                # Fallback si no hay columna Fase
                conteo_por_pregunta = df_3_clean.groupby('respuesta')['Encuentro'].nunique().reset_index()
            
            conteo_por_pregunta.columns = ['Respuesta', 'Numero_de_encuentros']
            
            # Función para tomar solo las primeras palabras
            def primeras_palabras(texto, num_palabras=3):
                palabras = texto.split()
                if len(palabras) > num_palabras:
                    return " ".join(palabras[:num_palabras]) + "..."
                return texto
            
            # Aplicar función a las respuestas
            conteo_por_pregunta['Respuesta_Corta'] = conteo_por_pregunta['Respuesta'].apply(lambda x: primeras_palabras(x, 3))
            
            # Ordenar por número de encuentros de mayor a menor
            conteo_por_pregunta = conteo_por_pregunta.sort_values('Numero_de_encuentros', ascending=True)
            
            # Crear el gráfico de barras horizontal
            fig_condiciones = px.bar(
                conteo_por_pregunta,
                x='Numero_de_encuentros',
                y='Respuesta_Corta',
                title="Número de Encuentros por Condición",
                labels={
                    'Numero_de_encuentros': 'Número de encuentros',
                    'Respuesta_Corta': 'Condición'
                },
                color='Numero_de_encuentros',
                color_continuous_scale=COLOR_PALETTE['blue_scale'],
                text='Numero_de_encuentros',
                orientation='h',
                hover_data={'Respuesta': True, 'Respuesta_Corta': False}  # Mostrar texto completo en hover
            )
            
            # Personalizar el gráfico
            fig_condiciones.update_traces(
                texttemplate='%{text}',
                textposition='outside'
            )
            
            fig_condiciones.update_layout(
                height=400,  # Aumentar altura del gráfico
                yaxis_title="Condiciones",
                xaxis_title="Número de encuentros",
                showlegend=False,
                font=dict(size=12),
                xaxis=dict(
                    range=[0, max(conteo_por_pregunta['Numero_de_encuentros']) * 1.1]
                ),
                yaxis=dict(
                    tickfont=dict(size=10),  # Tamaño de fuente legible
                    automargin=True  # Ajuste automático de márgenes
                ),
                margin=dict(l=150, r=50, t=80, b=50)  # Márgenes ajustados para barras horizontales
            )
            
            st.plotly_chart(fig_condiciones, use_container_width=True, config=chart_config)
        
        st.subheader("📊 Análisis de Debilidades por Encuentro")
        
        # Verificar que las columnas necesarias existen
        required_columns_3 = ['Encuentro', 'pregunta', 'respuesta']
        missing_columns_3 = [col for col in required_columns_3 if col not in df_3.columns]
        
        if missing_columns_3:
            st.error(f"Columnas faltantes en los datos: {missing_columns_3}")
            st.info("Las columnas disponibles son: " + ", ".join(df_3.columns.tolist()))
        else:
            # Limpiar datos: eliminar filas con Encuentro vacío
            df_3_clean = df_3[df_3['Encuentro'].notna() & (df_3['Encuentro'] != '')].copy()
            
            # Filtrar solo las filas donde 'pregunta' contenga 'Debilidad'
            df_3_clean = df_3_clean[df_3_clean['pregunta'].str.contains('Debilidad', case=False, na=False)].copy()
            
            if df_3_clean.empty:
                st.warning("No hay datos válidos después de filtrar por 'Debilidad'.")
                return
            
            # Extraer número del encuentro para ordenar correctamente
            df_3_clean['Encuentro_Num'] = df_3_clean['Encuentro'].str.extract(r'(\d+)').astype(int)
            
            # Crear identificador único considerando Encuentro + Fase para evitar duplicados entre fases
            if 'Fase' in df_3_clean.columns:
                df_3_clean['Encuentro_Fase_Unico'] = df_3_clean['Encuentro'].astype(str) + '_' + df_3_clean['Fase'].astype(str)
                # Contar encuentros únicos por respuesta considerando fase
                conteo_por_pregunta = df_3_clean.groupby('respuesta')['Encuentro_Fase_Unico'].nunique().reset_index()
            else:
                # Fallback si no hay columna Fase
                conteo_por_pregunta = df_3_clean.groupby('respuesta')['Encuentro'].nunique().reset_index()
            
            conteo_por_pregunta.columns = ['Respuesta', 'Numero_de_encuentros']
            
            # Función para tomar solo las primeras palabras
            def primeras_palabras(texto, num_palabras=3):
                palabras = texto.split()
                if len(palabras) > num_palabras:
                    return " ".join(palabras[:num_palabras]) + "..."
                return texto
            
            # Aplicar función a las respuestas
            conteo_por_pregunta['Respuesta_Corta'] = conteo_por_pregunta['Respuesta'].apply(lambda x: primeras_palabras(x, 3))
            
            # Ordenar por número de encuentros de mayor a menor
            conteo_por_pregunta = conteo_por_pregunta.sort_values('Numero_de_encuentros', ascending=True)
            
            # Crear el gráfico de barras horizontal
            fig_condiciones = px.bar(
                conteo_por_pregunta,
                x='Numero_de_encuentros',
                y='Respuesta_Corta',
                title="Número de Encuentros por Debilidad",
                labels={
                    'Numero_de_encuentros': 'Número de encuentros',
                    'Respuesta_Corta': 'Debilidad'
                },
                color='Numero_de_encuentros',
                color_continuous_scale=COLOR_PALETTE['blue_scale'],
                text='Numero_de_encuentros',
                orientation='h',
                hover_data={'Respuesta': True, 'Respuesta_Corta': False}  # Mostrar texto completo en hover
            )
            
            # Personalizar el gráfico
            fig_condiciones.update_traces(
                texttemplate='%{text}',
                textposition='outside'
            )
            
            fig_condiciones.update_layout(
                height=400,  # Aumentar altura del gráfico
                yaxis_title="Debilidades",
                xaxis_title="Número de encuentros",
                showlegend=False,
                font=dict(size=12),
                xaxis=dict(
                    range=[0, max(conteo_por_pregunta['Numero_de_encuentros']) * 1.1]
                ),
                yaxis=dict(
                    tickfont=dict(size=10),  # Tamaño de fuente legible
                    automargin=True  # Ajuste automático de márgenes
                ),
                margin=dict(l=150, r=50, t=80, b=50)  # Márgenes ajustados para barras horizontales
            )
            
            st.plotly_chart(fig_condiciones, use_container_width=True, config=chart_config)
           
    else:
        st.warning("No hay datos válidos en el tercer conjunto de datos.")
    
def instantaneas():
    """Dashboard de métricas instantáneas"""
    st.markdown("---")
    
    # URL del CSV para instantáneas
    url_instantaneas = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR7fcGuqe4teTMNwAZqMsoDLB8ijDTi8i2R-ihu2_ENZ_k4FnkPcqzzaXrZrEXWVil67RFhWQ9jKwjr/pub?output=csv"
    
    # Cargar datos
    df_inst = load_data(url_instantaneas)
    
    if df_inst.empty:
        st.warning("No hay datos disponibles para las métricas instantáneas.")
        return
    # Selector de instantánea al inicio
    st.subheader("🔍 Selección de Instantánea")

    # Obtener instantáneas disponibles
    if 'numInstantanea' in df_inst.columns:
        instantaneas_disponibles = sorted(df_inst['numInstantanea'].dropna().unique())
        # Agregar opción "Todas las instantáneas"
        opciones_instantanea = ["Todas las instantáneas"] + list(instantaneas_disponibles)
        
        instantanea_seleccionada = st.selectbox(
            "Selecciona la instantánea a analizar:",
            options=opciones_instantanea,
            help="Escoge la instantánea específica que deseas analizar en todos los gráficos, o selecciona 'Todas las instantáneas' para incluir todas"
        )
        
        st.markdown("---")
        st.info(f"📋 **Análisis para: {instantanea_seleccionada}**")
    else:
        st.warning("No se encontró la columna 'numInstantanea' en los datos o los datos están vacíos.")
        return

    # Filtrar datos por instantánea seleccionada
    if instantanea_seleccionada == "Todas las instantáneas":
        # No filtrar, mantener todas las instantáneas
        df_inst_filtered = df_inst.copy()
    else:
        # Filtrar por la instantánea específica seleccionada
        df_inst_filtered = df_inst[df_inst['numInstantanea'] == instantanea_seleccionada].copy()

    if df_inst_filtered.empty:
        st.warning("No hay datos válidos para el análisis de instantáneas.")
        return

    # Mapa de calor: accionMomento vs numInstantanea
    st.subheader("📊 Mapa de Calor - Acción Momento vs Instantáneas")
    
    if 'accionMomento' in df_inst_filtered.columns and 'numInstantanea' in df_inst_filtered.columns:
        # Crear tabla de frecuencias para el mapa de calor
        heatmap_data = df_inst_filtered.groupby(['accionMomento', 'numInstantanea']).size().reset_index(name='Frecuencia')
        
        # Crear tabla pivote para el mapa de calor
        pivot_data = heatmap_data.pivot(index='accionMomento', columns='numInstantanea', values='Frecuencia').fillna(0)
        
        if not pivot_data.empty:
            # Generar mapa de calor
            fig_heatmap = px.imshow(
                pivot_data.values,
                x=pivot_data.columns,
                y=pivot_data.index,
                color_continuous_scale=COLOR_PALETTE['blue_scale'],
                title="Frecuencia de Acciones por Instantánea",
                labels=dict(x="Número de Instantánea", y="Acción Momento", color="Frecuencia"),
                aspect="auto"
            )
            
            # Personalizar el diseño
            fig_heatmap.update_layout(
                height=600, 
                yaxis_title="Acción Momento",
                xaxis_title="Número de Instantánea",
                font=dict(size=16),
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(pivot_data.columns),
                    ticktext=[str(int(x)) for x in pivot_data.columns],
                    dtick=1, 
                    tickfont=dict(size=14)
                ),
                yaxis=dict(
                    tickfont=dict(size=14)
                ),
                title=dict(
                    font=dict(size=18)
                )
            )
            
            # Añadir valores en las celdas
            fig_heatmap.update_traces(
                text=pivot_data.values,
                texttemplate="%{text}",
                textfont={"size": 14}
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True, config=chart_config)
        else:
            st.warning("No hay suficientes datos para generar el mapa de calor.")
    
    # Análisis general de instantáneas
    col1, col2 = st.columns(2)
    
    with col1:
        if 'accionMomento' in df_inst_filtered.columns:
            # Gráfico de frecuencia por acción momento
            freq_por_accion = df_inst_filtered.groupby('accionMomento').size().reset_index(name='Frecuencia')
            freq_por_accion = freq_por_accion.sort_values('Frecuencia', ascending=True)
            
            fig_acciones = px.bar(
                freq_por_accion,
                x='Frecuencia',
                y='accionMomento',
                title="Frecuencia por Acción Momento",
                labels={'Frecuencia': 'Frecuencia', 'accionMomento': 'Acción Momento'},
                color='Frecuencia',
                color_continuous_scale=COLOR_PALETTE['blue_scale'],
                text='Frecuencia'
            )
            fig_acciones.update_traces(texttemplate='%{text}', textposition='outside')
            fig_acciones.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_acciones, use_container_width=True, config=chart_config)
    
    with col2:
        if 'numInstantanea' in df_inst_filtered.columns:
            # Gráfico de distribución por instantánea
            freq_por_instantanea = df_inst_filtered.groupby('numInstantanea').size().reset_index(name='Total_Observaciones')
            
            fig_instantaneas = px.bar(
                freq_por_instantanea,
                x='numInstantanea',
                y='Total_Observaciones',
                title="Observaciones por Instantánea",
                labels={'numInstantanea': 'Instantánea', 'Total_Observaciones': 'Total de Observaciones'},
                color='Total_Observaciones',
                color_continuous_scale=COLOR_PALETTE['blue_scale'],
                text='Total_Observaciones'
            )
            fig_instantaneas.update_traces(texttemplate='%{text}', textposition='outside')
            fig_instantaneas.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_instantaneas, use_container_width=True, config=chart_config)

    # Gráfico de barras apiladas: Participación por género en instantáneas
    st.subheader("📊 Distribución en Instantáneas")
    
    if 'participantes' in df_inst_filtered.columns and 'numInstantanea' in df_inst_filtered.columns and 'idEncuentro' in df_inst_filtered.columns:
        # Filtrar datos válidos (sin valores nulos o vacíos)
        df_participacion = df_inst_filtered[
            (df_inst_filtered['participantes'].notna()) & 
            (df_inst_filtered['participantes'] != '') &
            (df_inst_filtered['numInstantanea'].notna()) &
            (df_inst_filtered['idEncuentro'].notna())
        ].copy()
        
        if not df_participacion.empty:
            # Extraer el número del encuentro desde idEncuentro (ej. "E5" de "E5. Chipre - Primaria...")
            df_participacion['NumeroEncuentro'] = df_participacion['idEncuentro'].str.extract(r'(E\d+)')[0]
            
            # Filtrar solo registros que tengan un número de encuentro válido
            df_participacion = df_participacion[df_participacion['NumeroEncuentro'].notna()].copy()
            
            if not df_participacion.empty:
                # Crear conteo agrupado por instantánea y tipo de participantes (sin separar por encuentro)
                participacion_por_instantanea = df_participacion.groupby(['numInstantanea', 'participantes']).size().reset_index(name='Cantidad_Observaciones')
                
                # Crear el gráfico de barras apiladas vertical
                fig_participacion_apilada = px.bar(
                    participacion_por_instantanea,
                    x='numInstantanea',
                    y='Cantidad_Observaciones',
                    color='participantes',
                    title="Distribución de Tipos de Participación por Género en Instantáneas",
                    labels={
                        'numInstantanea': 'Instantáneas',
                        'Cantidad_Observaciones': 'No. de Encuentros',
                        'participantes': 'Tipo de Participación por Género'
                    },
                    color_discrete_sequence=COLOR_PALETTE['categorical'],
                    text='Cantidad_Observaciones'
                )
            
                # Personalizar el gráfico
                fig_participacion_apilada.update_traces(
                    texttemplate='%{text}',
                    textposition='inside',
                    textfont=dict(size=12, color='black')
                )
                
                fig_participacion_apilada.update_layout(
                    height=600,
                    xaxis_title="Instantáneas",
                    yaxis_title="No. de Encuentros",
                    legend=dict(
                        title="",
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5
                    ),
                    font=dict(size=12),
                    xaxis=dict(
                        tickmode='linear',
                        dtick=1
                    ),
                    barmode='stack'  # Apilar las barras
                )
                
                st.plotly_chart(fig_participacion_apilada, use_container_width=True, config=chart_config)
                
                # Generar insights automáticos para participación por género
                st.subheader("🔍  Participación por Género")
                
                # Calcular estadísticas para insights
                total_por_tipo = participacion_por_instantanea.groupby('participantes')['Cantidad_Observaciones'].sum().sort_values(ascending=False)
                
                if len(total_por_tipo) > 0:
                    tipo_mas_participativo = total_por_tipo.index[0]
                    valor_max = total_por_tipo.iloc[0]
                    
                    if len(total_por_tipo) > 1:
                        tipo_menos_participativo = total_por_tipo.index[-1]
                        valor_min = total_por_tipo.iloc[-1]
                    else:
                        tipo_menos_participativo = "otros tipos"
                        valor_min = 0
                    
                    # Verificar equilibrio de género
                    tipos_genero = [tipo for tipo in total_por_tipo.index if any(g in tipo.lower() for g in ['hombre', 'mujer', 'masculin', 'femenin'])]
                    
                    insights_participacion = []
                    
                    if len(tipos_genero) >= 2:
                        # Analizar equilibrio de género
                        valores_genero = [total_por_tipo[tipo] for tipo in tipos_genero[:2]]
                        diferencia_porcentual = abs(valores_genero[0] - valores_genero[1]) / max(valores_genero) * 100
                        
                        if diferencia_porcentual <= 20:  # Consideramos equilibrio si la diferencia es <= 20%
                            insights_participacion.append("🟢 **Equilibrio de género**: En la mayoría de instantáneas se observa participación activa de hombres y mujeres por igual.")
                        else:
                            genero_dominante = tipos_genero[0] if total_por_tipo[tipos_genero[0]] > total_por_tipo[tipos_genero[1]] else tipos_genero[1]
                            insights_participacion.append(f"🟡 **Desequilibrio de género**: Se observa mayor participación de {genero_dominante} en las instantáneas analizadas.")
                    
                    # Insight sobre participación dominante
                    insights_participacion.append(f"📊 **Tipo de participación dominante**: {tipo_mas_participativo} lidera la participación con {valor_max} observaciones, mientras que {tipo_menos_participativo} tiene menor presencia con {valor_min} observaciones.")
                    
                    # Calcular instantáneas con mayor diversidad
                    diversidad_por_instantanea = participacion_por_instantanea.groupby('numInstantanea')['participantes'].nunique().sort_values(ascending=False)
                    if len(diversidad_por_instantanea) > 0:
                        instantanea_mas_diversa = diversidad_por_instantanea.index[0]
                        max_tipos = diversidad_por_instantanea.iloc[0]
                        insights_participacion.append(f"🌟 **Diversidad de participación**: La instantánea {instantanea_mas_diversa} presenta la mayor diversidad con {max_tipos} tipos diferentes de participación.")
                    
                    # Mostrar insights
                    for insight in insights_participacion:
                        st.markdown(insight)
                
            else:
                st.warning("No hay datos válidos después de extraer el número de encuentro.")
        else:
            st.warning("No hay datos válidos de participación por género para mostrar.")
    else:
        st.warning("Las columnas requeridas no están disponibles en los datos.")
        columnas_requeridas = ['participantes', 'numInstantanea', 'idEncuentro']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df_inst_filtered.columns]
        if columnas_faltantes:
            st.info(f"Columnas faltantes: {', '.join(columnas_faltantes)}")
        st.info("Columnas disponibles: " + ", ".join(df_inst_filtered.columns.tolist()))
    
    


    if 'quienDirige' in df_inst_filtered.columns and 'numInstantanea' in df_inst_filtered.columns and 'idEncuentro' in df_inst_filtered.columns:
        # Filtrar datos válidos (sin valores nulos o vacíos)
        df_quien_dirige = df_inst_filtered[
            (df_inst_filtered['quienDirige'].notna()) & 
            (df_inst_filtered['quienDirige'] != '') &
            (df_inst_filtered['numInstantanea'].notna()) &
            (df_inst_filtered['idEncuentro'].notna())
        ].copy()

        if not df_quien_dirige.empty:
                # Crear conteo agrupado por instantánea y tipo de quienDirige (sin separar por encuentro)
                direccion_por_instantanea = df_quien_dirige.groupby(['numInstantanea', 'quienDirige']).size().reset_index(name='Cantidad_Observaciones')

                # Crear el gráfico de barras apiladas vertical
                fig_direccion_apilada = px.bar(
                    direccion_por_instantanea,
                    x='numInstantanea',
                    y='Cantidad_Observaciones',
                    color='quienDirige',
                    title="Distribución de quien Dirige en Instantáneas",
                    labels={
                        'numInstantanea': 'Instantáneas',
                        'Cantidad_Observaciones': 'No. de Encuentros',
                        'quienDirige': 'Qién Dirige la Participación'
                    },
                    color_discrete_sequence=COLOR_PALETTE['categorical'],
                    text='Cantidad_Observaciones'
                )
            
                # Personalizar el gráfico
                fig_direccion_apilada.update_traces(
                    texttemplate='%{text}',
                    textposition='inside',
                    textfont=dict(size=12, color='black')
                )

                fig_direccion_apilada.update_layout(
                    height=600,
                    xaxis_title="Instantáneas",
                    yaxis_title="No. de Encuentros",
                    legend=dict(
                        title="",
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5
                    ),
                    font=dict(size=12),
                    xaxis=dict(
                        tickmode='linear',
                        dtick=1
                    ),
                    barmode='stack'  # Apilar las barras
                )

                st.plotly_chart(fig_direccion_apilada, use_container_width=True, config=chart_config)
                
                # Generar insights automáticos para dirección de encuentros
                st.subheader("🔍  Dirección de Encuentros")
                
                # Calcular estadísticas para insights
                total_por_director = direccion_por_instantanea.groupby('quienDirige')['Cantidad_Observaciones'].sum().sort_values(ascending=False)
                
                if len(total_por_director) > 0:
                    director_principal = total_por_director.index[0]
                    valor_max = total_por_director.iloc[0]
                    
                    if len(total_por_director) > 1:
                        director_secundario = total_por_director.index[-1]
                        valor_min = total_por_director.iloc[-1]
                    else:
                        director_secundario = "otros"
                        valor_min = 0
                    
                    insights_direccion = []
                    
                    # Insight principal sobre dirección
                    porcentaje_principal = (valor_max / total_por_director.sum()) * 100
                    insights_direccion.append(f"🎯 **Dirección principal**: El encuentro estuvo principalmente dirigido por **{director_principal}** ({porcentaje_principal:.1f}% del total), con escasa dirección de **{director_secundario}**.")
                    
                    # Análisis de concentración de dirección
                    if porcentaje_principal > 70:
                        insights_direccion.append(f"⚠️ **Alta concentración**: La dirección está muy concentrada en {director_principal}, lo que podría indicar falta de participación colaborativa en la conducción.")
                    elif porcentaje_principal < 40:
                        insights_direccion.append("🤝 **Dirección equilibrada**: Se observa una distribución más equilibrada en la dirección de los encuentros, indicando mayor colaboración.")
                    else:
                        insights_direccion.append("📊 **Dirección moderada**: Existe un liderazgo claro pero con participación de otros actores en la dirección.")
                    
                    # Análisis por instantáneas
                    instantaneas_con_director = direccion_por_instantanea.groupby('numInstantanea').apply(
                        lambda x: x.loc[x['Cantidad_Observaciones'].idxmax(), 'quienDirige'], include_groups=False
                    )
                    consistencia = (instantaneas_con_director == director_principal).mean() * 100
                    
                    if consistencia > 80:
                        insights_direccion.append(f"🔄 **Consistencia alta**: {director_principal} dirige consistentemente en {consistencia:.0f}% de las instantáneas.")
                    else:
                        insights_direccion.append(f"🔄 **Variabilidad en dirección**: La dirección varía entre instantáneas, con {director_principal} liderando en {consistencia:.0f}% de los casos.")
                    
                    # Mostrar insights
                    for insight in insights_direccion:
                        st.markdown(insight)
                
        else:
            st.warning("No hay datos válidos de 'quienDirige' para mostrar.")
    else:
        st.warning("Las columnas requeridas no están disponibles en los datos.")
        columnas_requeridas = ['quienDirige', 'numInstantanea', 'idEncuentro']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df_inst_filtered.columns]
        if columnas_faltantes:
            st.info(f"Columnas faltantes: {', '.join(columnas_faltantes)}")
        st.info("Columnas disponibles: " + ", ".join(df_inst_filtered.columns.tolist()))


    # Verificar si existen las columnas de participación binaria
    columnas_participacion = ['participaPares', 'participaDocentes', 'participaMentores', 'participaNA']
    
    if all(col in df_inst_filtered.columns for col in columnas_participacion) and 'numInstantanea' in df_inst_filtered.columns:
        # Filtrar datos válidos
        df_participacion_binaria = df_inst_filtered[
            (df_inst_filtered['numInstantanea'].notna())
        ].copy()

        if not df_participacion_binaria.empty:
            # Sumar los valores binarios por instantánea para cada tipo de participación
            participacion_sumada = df_participacion_binaria.groupby('numInstantanea')[columnas_participacion].sum().reset_index()
            
            # Crear el DataFrame en formato largo para Plotly
            participacion_melted = participacion_sumada.melt(
                id_vars=['numInstantanea'],
                value_vars=columnas_participacion,
                var_name='Tipo_Participacion',
                value_name='Cantidad'
            )
            
            # Renombrar los tipos de participación para mejor presentación
            nombres_participacion = {
                'participaPares': 'Pares Expertos',
                'participaDocentes': 'Docentes Acompañados',
                'participaMentores': 'Mentores',
                'participaNA': 'No Aplica'
            }
            participacion_melted['Tipo_Participacion'] = participacion_melted['Tipo_Participacion'].map(nombres_participacion)

            # Crear el gráfico de barras agrupadas
            fig_participacion_agrupada = px.bar(
                participacion_melted,
                x='numInstantanea',
                y='Cantidad',
                color='Tipo_Participacion',
                title="Distribución de Participación por Tipo en Instantáneas",
                labels={
                    'numInstantanea': 'Instantáneas',
                    'Cantidad': 'Cantidad de Observaciones',
                    'Tipo_Participacion': 'Tipo de Participación'
                },
                color_discrete_sequence=COLOR_PALETTE['categorical'],
                text='Cantidad',
                barmode='group'  # Barras agrupadas, no apiladas
            )
            
            # Personalizar el gráfico
            fig_participacion_agrupada.update_traces(
                texttemplate='%{text}',
                textposition='outside',
                textfont=dict(size=10, color='black')
            )

            fig_participacion_agrupada.update_layout(
                height=600,
                xaxis_title="Instantáneas",
                yaxis_title="Cantidad de Observaciones",
                legend=dict(
                    title="Tipo de Participación",
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5
                ),
                font=dict(size=12),
                xaxis=dict(
                    tickmode='linear',
                    dtick=1
                )
            )

            st.plotly_chart(fig_participacion_agrupada, use_container_width=True, config=chart_config)
            
            # Generar insights automáticos para participación por tipo
            st.subheader("🔍  Participación por Tipo")
            
            # Calcular estadísticas para insights
            total_por_tipo_participacion = participacion_melted.groupby('Tipo_Participacion')['Cantidad'].sum().sort_values(ascending=False)
            
            if len(total_por_tipo_participacion) > 0:
                insights_tipos = []
                
                # Identificar tipos más y menos activos
                tipo_mas_activo = total_por_tipo_participacion.index[0]
                valor_mas_activo = total_por_tipo_participacion.iloc[0]
                
                tipo_menos_activo = total_por_tipo_participacion.index[-1]
                valor_menos_activo = total_por_tipo_participacion.iloc[-1]
                
                # Análisis de participación activa
                tipos_muy_activos = total_por_tipo_participacion[total_por_tipo_participacion >= total_por_tipo_participacion.mean()].index.tolist()
                
                if len(tipos_muy_activos) >= 2:
                    tipos_activos_str = " y ".join(tipos_muy_activos[:2]) if len(tipos_muy_activos) == 2 else ", ".join(tipos_muy_activos[:-1]) + " y " + tipos_muy_activos[-1]
                    insights_tipos.append(f"💪 **Participación colaborativa**: En los momentos de conversación o desarrollo de actividades, tanto **{tipos_activos_str}** participaban activamente.")
                else:
                    insights_tipos.append(f"💪 **Participación dominante**: **{tipo_mas_activo}** lidera claramente la participación activa en las instantáneas.")
                
                # Análisis de participación mínima
                if valor_menos_activo < total_por_tipo_participacion.mean() * 0.5:
                    insights_tipos.append(f"⚠️ **Participación limitada**: La participación de **{tipo_menos_activo}** fue mínima, con solo {valor_menos_activo} observaciones en total.")
                
                # Análisis de distribución
                coeficiente_variacion = total_por_tipo_participacion.std() / total_por_tipo_participacion.mean()
                if coeficiente_variacion > 0.5:
                    insights_tipos.append("📊 **Distribución desigual**: Existe una marcada diferencia en los niveles de participación entre los diferentes tipos de participantes.")
                else:
                    insights_tipos.append("📊 **Distribución equilibrada**: Los diferentes tipos de participantes muestran niveles similares de participación.")
                
                # Análisis por instantáneas
                participacion_por_instantanea_pivot = participacion_melted.pivot(index='numInstantanea', columns='Tipo_Participacion', values='Cantidad').fillna(0)
                
                if not participacion_por_instantanea_pivot.empty:
                    # Encontrar instantánea con mayor participación total
                    participacion_total_por_instantanea = participacion_por_instantanea_pivot.sum(axis=1)
                    instantanea_mas_activa = participacion_total_por_instantanea.idxmax()
                    
                    # Encontrar el tipo más consistente (presente en más instantáneas)
                    presencia_por_tipo = (participacion_por_instantanea_pivot > 0).sum()
                    tipo_mas_consistente = presencia_por_tipo.idxmax()
                    instantaneas_presentes = presencia_por_tipo.iloc[presencia_por_tipo.argmax()]
                    total_instantaneas = len(participacion_por_instantanea_pivot)
                    
                    insights_tipos.append(f"🌟 **Instantánea destacada**: La instantánea {instantanea_mas_activa} registra la mayor actividad colaborativa total.")
                    insights_tipos.append(f"🔄 **Consistencia**: **{tipo_mas_consistente}** mantiene presencia en {instantaneas_presentes} de {total_instantaneas} instantáneas analizadas.")
                
                # Mostrar insights
                for insight in insights_tipos:
                    st.markdown(insight)
            
        else:
            st.warning("No hay datos válidos de participación para mostrar.")
    else:
        st.warning("Las columnas requeridas no están disponibles en los datos.")
        columnas_faltantes = [col for col in columnas_participacion if col not in df_inst_filtered.columns]
        if columnas_faltantes:
            st.info(f"Columnas faltantes: {', '.join(columnas_faltantes)}")
        st.info("Columnas disponibles: " + ", ".join(df_inst_filtered.columns.tolist()))


        
# ==========================================
# APLICACIÓN PRINCIPAL
# ==========================================
st.title("🤝 Análisis Colaborativos e Instantáneas")

st.markdown("""
Esta página está dedicada al análisis profundo de los **encuentros colaborativos** entre docentes, 
explorando tanto las actitudes como las prácticas de colaboración en el contexto educativo.
""")

# Crear las pestañas principales
tab1, tab2 = st.tabs(["📊 Momentos", "⚡ Instantáneas"])

with tab1:
    
    # Mostrar dashboards especializados en colaboración
    hallazgos_generales()
    # ==========================================
    # GRAFICADOR PERSONALIZADO EN MOMENTOS
    # ==========================================
    st.markdown("---")

with tab2:
    st.header("⚡ Instantáneas - Métricas Rápidas")
    st.markdown("""
    Vista rápida de métricas clave y visualizaciones instantáneas sobre redes y 
    comunidades colaborativas.
    """)
    instantaneas()
    # Métricas instantáneas adicionales
    st.markdown("---")
  
# ==========================================
# INFORMACIÓN SOBRE COLABORACIÓN
# ==========================================
with st.expander("📚 Información sobre Encuentros Colaborativos"):
    st.markdown("""
    ### ¿Qué son los Encuentros Colaborativos?
    
    Los encuentros colaborativos son espacios de interacción donde los docentes:
    
    - **Comparten experiencias** y conocimientos pedagógicos
    - **Desarrollan proyectos conjuntos** interdisciplinarios
    - **Participan en redes** de aprendizaje profesional
    - **Construyen comunidades** de práctica educativa
    - **Intercambian recursos** y herramientas didácticas
    
    ### Beneficios de la Colaboración Docente:
    
    1. **Mejora de la práctica pedagógica** a través del intercambio de experiencias
    2. **Desarrollo profesional continuo** mediante el aprendizaje entre pares
    3. **Innovación educativa** a través de proyectos colaborativos
    4. **Fortalecimiento de la comunidad educativa** institucional e interinstitucional
    5. **Optimización de recursos** y herramientas educativas
    
    ### Datos Analizados:
    
    - **Actitudes hacia la colaboración** (Q15)
    - **Frecuencia de prácticas colaborativas** (Q18)
    - **Participación en redes y comunidades** 
    - **Correlaciones entre actitudes y prácticas**
    """)

# ==========================================
# FOOTER Y CRÉDITOS
# ==========================================
st.markdown("---")
st.write("© 2025 Colombia Programa - Encuentros Colaborativos - Ministerio de Tecnologías de la Información y las Comunicaciones (MinTIC)")

# Formatear el HTML con las imágenes convertidas a base64
formatted_footer = FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64)

# Mostrar el footer en Streamlit
st.markdown(formatted_footer, unsafe_allow_html=True)