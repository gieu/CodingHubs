import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from actions.chart_actions import graficador
from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import LOGO_NAVBAR_BASE64, HIDE_STREAMLIT_STYLE, NAVBAR_TEMPLATE, generar_css_personalizado
from utils.chart_config import get_chart_config

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
        'Masculino': '#1DB2E8',
        'Femenino': '#E91E63',
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

# Configuración de la página
st.set_page_config(layout="wide")

# Ocultar elementos de Streamlit
st.markdown(HIDE_STREAMLIT_STYLE, unsafe_allow_html=True)

# Generar el CSS personalizado con el color deseado
color_fondo_navbar = "#00A651"  # Verde para distinguir esta página
custom_css = generar_css_personalizado(color_fondo_navbar)

# Aplicar el CSS en Streamlit
st.markdown(custom_css, unsafe_allow_html=True)

# Crear navbar
navbar = NAVBAR_TEMPLATE.format(LOGO_NAVBAR_BASE64=LOGO_NAVBAR_BASE64)
st.markdown(navbar, unsafe_allow_html=True)

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
    
    url="https://docs.google.com/spreadsheets/d/e/2PACX-1vTpLweVduepr4MGi-VmtH35p9QPKz42V3MwiyRr7e3WILR2wFiI8KruhkytY96M4w/pub?output=csv"
    df = load_data(url)
    
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
    
    # Filtrar EXCLUYENDO los datos donde participante = 'DA' o 'M-Junior'
    # Y INCLUYENDO solo las Conductas específicas
    Conductas_permitidas = ['Transferencia de la experticia', 'Instrucción centrada en el estudiante', 'Enfoque de género']
    df_filtered = df[
        (~df['participante'].isin(['DA'])) & 
        (df['Conducta'].isin(Conductas_permitidas))
    ].copy()
    
    if df_filtered.empty:
        st.warning("No hay datos válidos después de aplicar los filtros.")
        st.info(f"Valores únicos en 'participante': {df['participante'].unique().tolist()}")
        st.info(f"Valores únicos en 'Conducta' (limpiados): {df['Conducta'].unique().tolist()}")
        st.info(f"Conductas buscadas: {Conductas_permitidas}")
        
        # Mostrar datos de depuración
        participantes_validos = df[~df['participante'].isin(['DA', 'M-Junior'])]
        st.info(f"Registros después de filtrar participantes: {len(participantes_validos)}")
        if len(participantes_validos) > 0:
            st.info(f"Conductas disponibles en participantes válidos: {participantes_validos['Conducta'].unique().tolist()}")
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
        font=dict(size=12),
        xaxis=dict(
            tickmode='array',
            tickvals=list(pivot_data.columns),
            ticktext=[str(int(x)) for x in pivot_data.columns],
            dtick=1  # Mostrar solo números enteros
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
        
        fig_bar_momentos = px.bar(
            freq_por_momento,
            x='Número de momento',
            y='Total_Observaciones',
            title="Total de conductas observadas por momento",
            labels={'Número de momento': 'Número de Momento', 'Total_Observaciones': 'Cantidad de Observaciones'},
            color='Total_Observaciones',
            color_continuous_scale=COLOR_PALETTE['green_scale'],
            text='Total_Observaciones'
        )
        fig_bar_momentos.update_traces(texttemplate='%{text}', textposition='outside')
        fig_bar_momentos.update_layout(
            showlegend=False, 
            height=400,
            xaxis=dict(
                tickmode='linear',
                dtick=1  # Mostrar solo números enteros
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
    st.subheader("� Análisis de Líneas: Transferencia de la Experticia por Participante y Momento")
    
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
                        porcentaje = (encuentros_en_momento / max_encuentros) * 100
                        total_obs = len(df_subset[df_subset['Número de momento'] == momento])
                    else:
                        # No hay datos para este momento, usar 0
                        encuentros_en_momento = 0
                        porcentaje = 0
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
                height=600,
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
                tabla_tipo = df_tipo.pivot(index='Momento', columns='Participante', values='Porcentaje_Encuentros').fillna(0)
                st.dataframe(tabla_tipo, use_container_width=True)
            elif num_tipos == 2:
                # Dos columnas
                col1, col2 = st.columns(2)
                for i, tipo in enumerate(tipos_unicos):
                    with (col1 if i == 0 else col2):
                        st.write(f"**{tipo}:**")
                        df_tipo = df_lineas[df_lineas['Tipo'] == tipo]
                        tabla_tipo = df_tipo.pivot(index='Momento', columns='Participante', values='Porcentaje_Encuentros').fillna(0)
                        st.dataframe(tabla_tipo, use_container_width=True)
            elif num_tipos == 3:
                # Tres columnas
                col1, col2, col3 = st.columns(3)
                columnas = [col1, col2, col3]
                for i, tipo in enumerate(tipos_unicos):
                    with columnas[i]:
                        st.write(f"**{tipo}:**")
                        df_tipo = df_lineas[df_lineas['Tipo'] == tipo]
                        tabla_tipo = df_tipo.pivot(index='Momento', columns='Participante', values='Porcentaje_Encuentros').fillna(0)
                        st.dataframe(tabla_tipo, use_container_width=True)
            else:
                # Más de 3 tipos: usar 2 columnas y distribuir
                col1, col2 = st.columns(2)
                for i, tipo in enumerate(tipos_unicos):
                    with (col1 if i % 2 == 0 else col2):
                        st.write(f"**{tipo}:**")
                        df_tipo = df_lineas[df_lineas['Tipo'] == tipo]
                        tabla_tipo = df_tipo.pivot(index='Momento', columns='Participante', values='Porcentaje_Encuentros').fillna(0)
                        st.dataframe(tabla_tipo, use_container_width=True)
                        if i % 2 == 1 or i == len(tipos_unicos) - 1:  # Añadir espacio después de cada fila
                            st.write("")
        else:
            st.warning("No se pudieron calcular los porcentajes por participante y momento.")
    else:
        st.warning("No hay datos disponibles para 'Transferencia de la experticia' o faltan las columnas necesarias ('Encuentro', 'participante' o 'tipo').")
   
   
    url_2="https://docs.google.com/spreadsheets/d/e/2PACX-1vTzFwQJLWwU2jMg49j0HDgXEdXLER-EuP2qLGlPI7OuGA0TLQ8sMgc9rnb4lG5GZA/pub?output=csv"
    df_2 = load_data(url_2)

    if df_2.empty:
        st.warning("No hay datos válidos para docentes por sexo.")
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
    
    st.subheader("📊 Participación por Tipo y Género")
    
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
            title="Porcentaje de Participación por Tipo de Conducta, Género y Participante",
            labels={
                'Porcentaje_Participacion': 'Porcentaje de Participación (%)',
                'Tipo': 'Tipo de Conducta',
                'Género': 'Género'
            },
            facet_col='Participante',
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
        
        # Mostrar tabla de datos detallados
        st.subheader("📋 Datos Detallados de Participación")
        
        # Mostrar tabla completa con todas las dimensiones
        st.dataframe(participacion_con_total, use_container_width=True)
        
        # Crear tabla pivote por participante para mejor visualización
        st.subheader("📊 Resumen por Participante")
        
        # Tabla resumen por participante
        resumen_participante = participacion_con_total.groupby('Participante').agg({
            'Participantes_Únicos': 'sum',
            'Total_Participantes': 'first',
            'Porcentaje_Participacion': 'mean'
        }).round(2)
        
        st.dataframe(resumen_participante, use_container_width=True)
        
        # Métricas adicionales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_participantes = df_filtered_genero['nombre'].nunique()
            st.metric("Total Participantes Únicos", total_participantes)
        
        with col2:
            generos_unicos = df_filtered_genero['sexo'].nunique()
            st.metric("Géneros Identificados", generos_unicos)
        
        with col3:
            tipos_unicos = df_filtered_genero['tipo'].nunique()
            st.metric("Tipos de Conducta", tipos_unicos)
        
        with col4:
            participantes_unicos = df_filtered_genero['participante'].nunique()
            st.metric("Tipos de Participante", participantes_unicos)
        
        # Análisis adicional por género
        st.subheader("🔍 Análisis por Género")
        
        # Distribución general por género
        distribucion_genero = df_filtered_genero.groupby('sexo')['nombre'].nunique().reset_index()
        distribucion_genero.columns = ['Género', 'Participantes']
        distribucion_genero['Porcentaje'] = (distribucion_genero['Participantes'] / 
                                           distribucion_genero['Participantes'].sum() * 100)
        
        fig_pie_genero = px.pie(
            distribucion_genero,
            values='Porcentaje',
            names='Género',
            title="Distribución General por Género",
            color_discrete_map=COLOR_PALETTE['gender_colors']
        )
        fig_pie_genero.update_traces(textinfo='percent+label')
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_pie_genero, use_container_width=True, config=chart_config)
        
        with col2:
            st.dataframe(distribucion_genero, use_container_width=True)
    
    else:
        st.warning("No hay datos válidos para crear la gráfica de participación por género.")

    

def dashboard_actitudes_colaboracion_ampliado(df):
    """
    Dashboard ampliado para Actitudes hacia la Colaboración (Q15)
    """
    st.markdown("---")
    st.header("💭 Actitudes hacia los Encuentros Colaborativos")
    
    q15_cols = ['Q15_1', 'Q15_2', 'Q15_3', 'Q15_4', 'Q15_5', 'Q15_6', 'Q15_7', 'Q15_8', 'Q15_9', 'Q15_10', 'Q15_11']
    q15_labels = {
        'Q15_1': 'Compartir Ideas Abiertamente',
        'Q15_2': 'Escuchar Opiniones Diversas',
        'Q15_3': 'Valorar Retroalimentación',
        'Q15_4': 'Compartir Conocimiento',
        'Q15_5': 'Organizar Agenda Colaborativa',
        'Q15_6': 'Buscar Retroalimentación Activa',
        'Q15_7': 'Encontrar Tiempo para Colaborar',
        'Q15_8': 'Importancia de la Colaboración',
        'Q15_9': 'Resistencia a la Colaboración',
        'Q15_10': 'Necesidad de Colaboración',
        'Q15_11': 'Desgaste por Colaboración'
    }
    
    missing_cols = [col for col in q15_cols if col not in df.columns]
    if missing_cols:
        st.error(f"Columnas faltantes en los datos: {missing_cols}")
        return
    
    likert_mapping = {
        'Totalmente en desacuerdo': 1,
        'En desacuerdo': 2,
        'Neutro': 3,
        'De acuerdo': 4,
        'Totalmente de acuerdo': 5
    }
    
    df_q15 = df[q15_cols].copy()
    
    for col in q15_cols:
        df_q15[col] = df_q15[col].map(likert_mapping)
    
    # Invertir preguntas negativas (Q15_9 y Q15_11)
    if 'Q15_9' in df_q15.columns:
        df_q15['Q15_9'] = 6 - df_q15['Q15_9']
    if 'Q15_11' in df_q15.columns:
        df_q15['Q15_11'] = 6 - df_q15['Q15_11']
    
    df_q15 = df_q15.dropna()
    
    if df_q15.empty:
        st.warning("No hay datos válidos para mostrar.")
        return
    
    promedios = df_q15.mean()
    promedio_general = promedios.mean()
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Actitud General", f"{promedio_general:.2f}/5")
    
    with col2:
        actitudes_positivas = len(promedios[promedios >= 4])
        st.metric("Actitudes Positivas", f"{actitudes_positivas}/{len(promedios)}")
    
    with col3:
        st.metric("Actitud Más Positiva", f"{q15_labels[promedios.idxmax()][:20]}...")
    
    with col4:
        participantes_positivos = len(df_q15[df_q15.mean(axis=1) >= 4])
        st.metric("Docentes muy Positivos", f"{participantes_positivos}")
    
    # Gráfico de barras mejorado
    st.subheader("📊 Perfil de Actitudes Colaborativas")
    
    # Categorizar actitudes
    df_bar = pd.DataFrame({
        'Actitud': [q15_labels[col] for col in promedios.index],
        'Promedio': promedios.values,
        'Categoria': ['Positiva' if x >= 4 else 'Neutral' if x >= 3 else 'Negativa' for x in promedios.values]
    }).sort_values('Promedio', ascending=True)
    
    color_map = {'Positiva': COLOR_PALETTE['secondary'], 'Neutral': COLOR_PALETTE['accent'], 'Negativa': COLOR_PALETTE['danger']}
    
    fig_bar = px.bar(
        df_bar, 
        x='Promedio', 
        y='Actitud',
        title="Actitudes hacia los Encuentros Colaborativos",
        text='Promedio',
        color='Categoria',
        color_discrete_map=color_map,
        orientation='h'
    )
    fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_bar.update_layout(height=700, legend_title_text="Nivel de Actitud")
    st.plotly_chart(fig_bar, use_container_width=True, config=chart_config)
    
    # Análisis de correlaciones
    st.subheader("🔗 Análisis de Correlaciones entre Actitudes")
    
    # Matriz de correlación
    corr_matrix = df_q15.corr()
    
    fig_heatmap = px.imshow(
        corr_matrix,
        title="Matriz de Correlación - Actitudes Colaborativas",
        color_continuous_scale='RdBu',
        aspect="auto"
    )
    fig_heatmap.update_layout(height=600)
    st.plotly_chart(fig_heatmap, use_container_width=True, config=chart_config)

def dashboard_comparativo_colaboracion(df):
    """
    Dashboard comparativo entre diferentes aspectos de colaboración
    """
    st.markdown("---")
    st.header("⚖️ Análisis Comparativo de Colaboración")
    
    # Comparar Q15 (Actitudes) vs Q18 (Prácticas)
    q15_cols = ['Q15_1', 'Q15_2', 'Q15_3', 'Q15_4', 'Q15_5', 'Q15_6', 'Q15_7', 'Q15_8', 'Q15_9', 'Q15_10', 'Q15_11']
    q18_cols = ['Q18_1', 'Q18_2', 'Q18_3', 'Q18_4', 'Q18_5', 'Q18_6', 'Q18_7', 'Q18_8', 'Q18_9', 'Q18_10']
    
    # Verificar disponibilidad de datos
    missing_q15 = [col for col in q15_cols if col not in df.columns]
    missing_q18 = [col for col in q18_cols if col not in df.columns]
    
    if missing_q15 or missing_q18:
        st.error(f"Datos faltantes. Q15: {missing_q15}, Q18: {missing_q18}")
        return
    
    # Procesar datos Q15 (Actitudes)
    likert_mapping = {
        'Totalmente en desacuerdo': 1, 'En desacuerdo': 2, 'Neutro': 3, 'De acuerdo': 4, 'Totalmente de acuerdo': 5
    }
    
    df_q15 = df[q15_cols].copy()
    for col in q15_cols:
        df_q15[col] = df_q15[col].map(likert_mapping)
    
    # Invertir preguntas negativas
    if 'Q15_9' in df_q15.columns:
        df_q15['Q15_9'] = 6 - df_q15['Q15_9']
    if 'Q15_11' in df_q15.columns:
        df_q15['Q15_11'] = 6 - df_q15['Q15_11']
    
    # Procesar datos Q18 (Prácticas)
    freq_mapping = {
        'Nunca': 1, 'Rara vez': 2, 'Ocasionalmente': 3, 'Frecuentemente': 4, 'Muy frecuentemente': 5
    }
    
    df_q18 = df[q18_cols].copy()
    for col in q18_cols:
        df_q18[col] = df_q18[col].map(freq_mapping)
    
    # Calcular promedios
    promedio_actitudes = df_q15.mean(axis=1)
    promedio_practicas = df_q18.mean(axis=1)
    
    # Crear DataFrame combinado
    df_comparativo = pd.DataFrame({
        'Actitudes': promedio_actitudes,
        'Prácticas': promedio_practicas
    }).dropna()
    
    if df_comparativo.empty:
        st.warning("No hay datos válidos para la comparación.")
        return
    
    # Métricas comparativas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Promedio Actitudes", f"{df_comparativo['Actitudes'].mean():.2f}/5")
    
    with col2:
        st.metric("Promedio Prácticas", f"{df_comparativo['Prácticas'].mean():.2f}/5")
    
    with col3:
        correlacion = df_comparativo['Actitudes'].corr(df_comparativo['Prácticas'])
        st.metric("Correlación", f"{correlacion:.3f}")
    
    with col4:
        coherentes = len(df_comparativo[abs(df_comparativo['Actitudes'] - df_comparativo['Prácticas']) <= 0.5])
        st.metric("Docentes Coherentes", f"{coherentes}/{len(df_comparativo)}")
    
    # Gráfico de dispersión
    st.subheader("📈 Relación Actitudes vs Prácticas Colaborativas")
    
    fig_scatter = px.scatter(
        df_comparativo,
        x='Actitudes',
        y='Prácticas',
        title="Actitudes vs Prácticas en Colaboración",
        labels={'Actitudes': 'Actitudes hacia la Colaboración (1-5)', 
                'Prácticas': 'Frecuencia de Prácticas Colaborativas (1-5)'},
        color_discrete_sequence=[COLOR_PALETTE['secondary']]
    )
    
    # Añadir línea de tendencia
    fig_scatter.add_trace(
        px.scatter(df_comparativo, x='Actitudes', y='Prácticas', trendline="ols").data[1]
    )
    
    fig_scatter.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig_scatter, use_container_width=True, config=chart_config)
    
    # Análisis de segmentos
    st.subheader("🎯 Segmentación de Docentes")
    
    # Crear segmentos basados en niveles de actitudes y prácticas
    df_comparativo['Segmento'] = 'Intermedio'
    df_comparativo.loc[(df_comparativo['Actitudes'] >= 4) & (df_comparativo['Prácticas'] >= 4), 'Segmento'] = 'Colaboradores Activos'
    df_comparativo.loc[(df_comparativo['Actitudes'] >= 4) & (df_comparativo['Prácticas'] < 3), 'Segmento'] = 'Potencial sin Acción'
    df_comparativo.loc[(df_comparativo['Actitudes'] < 3) & (df_comparativo['Prácticas'] >= 4), 'Segmento'] = 'Activos sin Convicción'
    df_comparativo.loc[(df_comparativo['Actitudes'] < 3) & (df_comparativo['Prácticas'] < 3), 'Segmento'] = 'Poco Colaborativos'
    
    segmentos = df_comparativo['Segmento'].value_counts()
    
    fig_pie = px.pie(
        values=segmentos.values,
        names=segmentos.index,
        title="Segmentación de Docentes según Colaboración",
        color_discrete_sequence=COLOR_PALETTE['categorical']
    )
    fig_pie.update_layout(height=500)
    st.plotly_chart(fig_pie, use_container_width=True, config=chart_config)

def dashboard_redes_colaboracion(df):
    """
    Dashboard sobre redes y comunidades de colaboración
    """
    st.markdown("---")
    st.header("🌐 Redes y Comunidades Colaborativas")
    
    # Enfocarse en preguntas específicas sobre redes
    red_cols = ['Q18_2', 'Q18_3', 'Q18_4']  # Interinstitucional, Redes, Comunidades
    red_labels = {
        'Q18_2': 'Colaboración Interinstitucional',
        'Q18_3': 'Redes de Aprendizaje',
        'Q18_4': 'Comunidades de Práctica'
    }
    
    missing_cols = [col for col in red_cols if col not in df.columns]
    if missing_cols:
        st.error(f"Columnas faltantes: {missing_cols}")
        return
    
    freq_mapping = {
        'Nunca': 1, 'Rara vez': 2, 'Ocasionalmente': 3, 'Frecuentemente': 4, 'Muy frecuentemente': 5
    }
    
    df_red = df[red_cols].copy()
    for col in red_cols:
        df_red[col] = df_red[col].map(freq_mapping)
    
    df_red = df_red.dropna()
    
    if df_red.empty:
        st.warning("No hay datos válidos para redes.")
        return
    
    # Métricas de redes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        interinstitucional_activos = len(df_red[df_red['Q18_2'] >= 4])
        st.metric("Colaboración Interinstitucional Activa", f"{interinstitucional_activos}")
    
    with col2:
        redes_activos = len(df_red[df_red['Q18_3'] >= 4])
        st.metric("Participantes en Redes", f"{redes_activos}")
    
    with col3:
        comunidades_activos = len(df_red[df_red['Q18_4'] >= 4])
        st.metric("Miembros de Comunidades", f"{comunidades_activos}")
    
    # Gráfico de redes
    st.subheader("🕸️ Participación en Diferentes Tipos de Redes")
    
    promedios_red = df_red.mean()
    
    fig_red = px.bar(
        x=[red_labels[col] for col in red_cols],
        y=[promedios_red[col] for col in red_cols],
        title="Nivel de Participación en Redes Colaborativas",
        labels={'x': 'Tipo de Red', 'y': 'Promedio de Participación (1-5)'},
        color=[promedios_red[col] for col in red_cols],
        color_continuous_scale=[COLOR_PALETTE['accent'], COLOR_PALETTE['secondary']]
    )
    fig_red.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_red, use_container_width=True, config=chart_config)

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
        
    # Métricas instantáneas adicionales
    st.markdown("---")
    st.subheader("🚀 Métricas Instantáneas")
  
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