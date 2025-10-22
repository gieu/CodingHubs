import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from actions.chart_actions import graficador
from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import header,  HIDE_STREAMLIT_STYLE, generar_css_personalizado
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

# Ocultar elementos de Streamlit
st.markdown(HIDE_STREAMLIT_STYLE, unsafe_allow_html=True)

# Generar el CSS personalizado con el color deseado
color_fondo_navbar = "#1DB2E8"  # Cambia este valor según lo necesites
custom_css = generar_css_personalizado(color_fondo_navbar)

# Aplicar el CSS en Streamlit
st.markdown(custom_css, unsafe_allow_html=True)

# Crear navbar
header()
# ==========================================
# CARGA DE DATOS
# ==========================================
# URL del CSV
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ5wKRchgokVXA_uIQuSDqQ4MxsPwkTuwrLLOCc7rjIIlVhfgR4MnAKGLY5u_Hucg/pub?output=csv"

@st.cache_data(ttl=600)
def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    return df

df = load_data(CSV_URL)

# ==========================================
# FUNCIONES DE DASHBOARDS
# ==========================================

def dashboard_q19(df):
    """
    Dashboard simplificado con métricas de las preguntas Q19_1 al Q19_7 (excepto Q19_4)
    - Analiza prácticas pedagógicas
    """
    st.markdown("---")
    st.header("📊 Prácticas Pedagógicas")
    
    # Definir las columnas Q19 (excluyendo Q19_4)
    q19_cols = ['Q19_1', 'Q19_2', 'Q19_3', 'Q19_5', 'Q19_6', 'Q19_7']
    q19_labels = {
        'Q19_1': 'Desconectadas',
        'Q19_2': 'Conectadas', 
        'Q19_3': 'Usa-Modifica-Crea',
        'Q19_5': 'ABP',
        'Q19_6': 'Taxonomía Weintrop',
        'Q19_7': 'PRIMM'
    }
    
    # Verificar que las columnas existen
    missing_cols = [col for col in q19_cols if col not in df.columns]
    if missing_cols:
        st.warning(f"Columnas no encontradas: {missing_cols}")
        return
    
    # Procesar datos
    df_q19 = df[q19_cols].copy()
    
    # Convertir "No conozco" a 0 y hacer numérico
    for col in q19_cols:
        df_q19[col] = df_q19[col].replace(['No conozco', 'No sé'], 0)
        df_q19[col] = pd.to_numeric(df_q19[col], errors='coerce')
    
    df_q19 = df_q19.dropna()
    
    if df_q19.empty:
        st.warning("No hay datos válidos para Prácticas Pedagógicas.")
        return
    
    # Calcular métricas
    promedios = df_q19.mean()
    promedio_general = promedios.mean()
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📈 Promedio General", f"{promedio_general:.2f}")
    
    with col2:
        st.metric("📊 Total Respuestas", len(df_q19))
    
    with col3:
        mejor = promedios.idxmax()
        st.metric("🏆 Mejor", q19_labels[mejor], f"{promedios[mejor]:.2f}")
    
    # Gráfico de barras
    st.subheader("📊 Promedios por Práctica")
    
    df_bar = pd.DataFrame({
        'Práctica': [q19_labels[col] for col in promedios.index],
        'Promedio': promedios.values
    })
    
    fig_bar = px.bar(
        df_bar, 
        x='Práctica', 
        y='Promedio',
        title="Prácticas Pedagógicas - Promedios",
        text='Promedio',
        color='Promedio',
        color_continuous_scale=COLOR_PALETTE['blue_scale']
    )
    fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_bar.update_layout(
        xaxis_tickangle=-45,
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig_bar, use_container_width=True, config=chart_config)
    
    # Tabla resumida
    with st.expander("📋 Ver detalles estadísticos"):
        stats_df = pd.DataFrame({
            'Práctica': [q19_labels[col] for col in q19_cols],
            'Promedio': [f"{promedios[col]:.2f}" for col in q19_cols],
            'Desv.Est.': [f"{df_q19[col].std():.2f}" for col in q19_cols]
        })
        st.dataframe(stats_df, use_container_width=True)

def dashboard_habilidades_pc(df):
    """
    Dashboard para Percepción de Habilidades PC (Q16)
    - Analiza la percepción de habilidades en Pensamiento Computacional
    """
    st.markdown("---")
    st.header("🎯 Percepción de Habilidades PC")
    
    # Columnas Q16
    q16_cols = ['Q16_1', 'Q16_2', 'Q16_3', 'Q16_4', 'Q16_5', 'Q16_6', 'Q16_7', 'Q16_8', 'Q16_9', 'Q16_10', 'Q16_11', 'Q16_12', 'Q16_13']
    q16_labels = {
        'Q16_1': 'Aplicar en Trabajo',
        'Q16_2': 'Definir PC',
        'Q16_3': 'Describir PC',
        'Q16_4': 'Aplicar Vida Diaria',
        'Q16_5': 'Desarrollar en Estudiantes',
        'Q16_6': 'Enseñar Fácilmente',
        'Q16_7': 'Diseñar Clases',
        'Q16_8': 'Seleccionar Tecnologías',
        'Q16_9': 'Intereses Individuales',
        'Q16_10': 'Evaluar Estrategias',
        'Q16_11': 'Aprender Tecnologías',
        'Q16_12': 'Usar TIC',
        'Q16_13': 'Ajustar Currículo'
    }
    
    missing_cols = [col for col in q16_cols if col not in df.columns]
    if missing_cols:
        st.warning(f"Columnas no encontradas: {missing_cols}")
        return
    
    # Mapeo de respuestas tipo Likert a números
    likert_mapping = {
        'Totalmente en desacuerdo': 1,
        'En desacuerdo': 2,
        'Neutro': 3,
        'De acuerdo': 4,
        'Totalmente de acuerdo': 5
    }
    
    df_q16 = df[q16_cols].copy()
    
    # Convertir respuestas Likert a numérico
    for col in q16_cols:
        df_q16[col] = df_q16[col].map(likert_mapping)
    
    df_q16 = df_q16.dropna()
    
    if df_q16.empty:
        st.warning("No hay datos válidos para Habilidades PC.")
        return
    
    promedios = df_q16.mean()
    promedio_general = promedios.mean()
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📈 Promedio General", f"{promedio_general:.2f}/5")
    
    with col2:
        st.metric("📊 Total Respuestas", len(df_q16))
    
    with col3:
        mejor = promedios.idxmax()
        st.metric("🏆 Mayor Confianza", q16_labels[mejor][:15] + "...", f"{promedios[mejor]:.2f}/5")
    
    # Gráfico de barras horizontal para mejor visualización
    st.subheader("📊 Percepción de Habilidades (1-5)")
    
    df_bar = pd.DataFrame({
        'Habilidad': [q16_labels[col] for col in promedios.index],
        'Promedio': promedios.values
    }).sort_values('Promedio', ascending=True)
    
    fig_bar = px.bar(
        df_bar, 
        x='Promedio', 
        y='Habilidad',
        title="Percepción de Habilidades PC",
        text='Promedio',
        color='Promedio',
        color_continuous_scale=COLOR_PALETTE['blue_scale'],
        orientation='h'
    )
    fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_bar.update_layout(height=600, showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True, config=chart_config)

def dashboard_colaboracion(df):
    """
    Dashboard para Trabajo Colaborativo (Q18)
    - Analiza frecuencia de actividades de colaboración
    """
    st.markdown("---")
    st.header("🤝 Trabajo Colaborativo")
    
    q18_cols = ['Q18_1', 'Q18_2', 'Q18_3', 'Q18_4', 'Q18_5', 'Q18_6', 'Q18_7', 'Q18_8', 'Q18_9', 'Q18_10']
    q18_labels = {
        'Q18_1': 'Comunicación',
        'Q18_2': 'Interinstitucional',
        'Q18_3': 'Redes Aprendizaje',
        'Q18_4': 'Comunidades Práctica',
        'Q18_5': 'Intercambio Recursos',
        'Q18_6': 'Equipos Colaborativos',
        'Q18_7': 'Proyectos Interdisciplinarios',
        'Q18_8': 'Mentoría',
        'Q18_9': 'Diálogo y Retroalimentación',
        'Q18_10': 'Adaptación Curricular'
    }
    
    missing_cols = [col for col in q18_cols if col not in df.columns]
    if missing_cols:
        st.warning(f"Columnas no encontradas: {missing_cols}")
        return
    
    # Mapeo de frecuencias
    freq_mapping = {
        'Nunca': 1,
        'Rara vez': 2,
        'Ocasionalmente': 3,
        'Frecuentemente': 4,
        'Muy frecuentemente': 5
    }
    
    df_q18 = df[q18_cols].copy()
    
    for col in q18_cols:
        df_q18[col] = df_q18[col].map(freq_mapping)
    
    df_q18 = df_q18.dropna()
    
    if df_q18.empty:
        st.warning("No hay datos válidos para Colaboración.")
        return
    
    promedios = df_q18.mean()
    promedio_general = promedios.mean()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📈 Promedio General", f"{promedio_general:.2f}/5")
    
    with col2:
        st.metric("📊 Total Respuestas", len(df_q18))
    
    with col3:
        mejor = promedios.idxmax()
        st.metric("🏆 Más Frecuente", q18_labels[mejor], f"{promedios[mejor]:.2f}/5")
    
    # Gráfico radar para colaboración
    st.subheader("🕸️ Perfil de Colaboración")
    
    categories = [q18_labels[col] for col in q18_cols]
    values = [promedios[col] for col in q18_cols]
    
    fig_radar = go.Figure()
    
    fig_radar.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Colaboración',
        line=dict(color=COLOR_PALETTE['primary'], width=2),
        fillcolor=f"rgba({int(COLOR_PALETTE['primary'][1:3], 16)}, {int(COLOR_PALETTE['primary'][3:5], 16)}, {int(COLOR_PALETTE['primary'][5:7], 16)}, 0.3)"
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )),
        showlegend=False,
        title="Perfil de Trabajo Colaborativo",
        height=500
    )
    
    st.plotly_chart(fig_radar, use_container_width=True, config=chart_config)

def dashboard_actitudes_colaboracion(df):
    """
    Dashboard para Actitudes hacia la Colaboración (Q15)
    - Analiza actitudes y disposición hacia el trabajo colaborativo
    """
    st.markdown("---")
    st.header("💭 Actitudes hacia la Colaboración")
    
    q15_cols = ['Q15_1', 'Q15_2', 'Q15_3', 'Q15_4', 'Q15_5', 'Q15_6', 'Q15_7', 'Q15_8', 'Q15_9', 'Q15_10', 'Q15_11']
    q15_labels = {
        'Q15_1': 'Compartir Ideas',
        'Q15_2': 'Escuchar Opiniones',
        'Q15_3': 'Valorar Retroalimentación',
        'Q15_4': 'Compartir Conocimiento',
        'Q15_5': 'Organizar Agenda',
        'Q15_6': 'Buscar Retroalimentación',
        'Q15_7': 'Encontrar Tiempo',
        'Q15_8': 'Importancia Colaboración',
        'Q15_9': 'Actitud Negativa', # Reverso
        'Q15_10': 'Colaboración Necesaria',
        'Q15_11': 'Desgaste Colaboración' # Reverso
    }
    
    missing_cols = [col for col in q15_cols if col not in df.columns]
    if missing_cols:
        st.warning(f"Columnas no encontradas: {missing_cols}")
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
        st.warning("No hay datos válidos para Actitudes.")
        return
    
    promedios = df_q15.mean()
    promedio_general = promedios.mean()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📈 Actitud General", f"{promedio_general:.2f}/5")
    
    with col2:
        st.metric("📊 Total Respuestas", len(df_q15))
    
    with col3:
        mejor = promedios.idxmax()
        st.metric("🏆 Mejor Actitud", q15_labels[mejor][:12] + "...", f"{promedios[mejor]:.2f}/5")
    
    # Gráfico de barras
    st.subheader("📊 Actitudes hacia la Colaboración")
    
    df_bar = pd.DataFrame({
        'Actitud': [q15_labels[col] for col in promedios.index],
        'Promedio': promedios.values
    }).sort_values('Promedio', ascending=False)
    
    fig_bar = px.bar(
        df_bar, 
        x='Actitud', 
        y='Promedio',
        title="Actitudes hacia la Colaboración (1-5)",
        text='Promedio',
        color='Promedio',
        color_continuous_scale=COLOR_PALETTE['blue_scale']
    )
    fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_bar.update_layout(
        xaxis_tickangle=-45,
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig_bar, use_container_width=True, config=chart_config)

def dashboard_estrategias_programacion(df):
    """
    Dashboard para Estrategias de Programación (Q20)
    - Analiza estrategias de enseñanza específicas para programación
    """
    st.markdown("---")
    st.header("💻 Estrategias de Programación")
    
    q20_cols = ['Q20_1', 'Q20_2', 'Q20_3', 'Q20_4', 'Q20_5', 'Q20_6', 'Q20_7']
    q20_labels = {
        'Q20_1': 'Explicar Respuesta',
        'Q20_2': 'Paso a Paso',
        'Q20_3': 'Revisar Notas',
        'Q20_4': 'Memorias Colectivas',
        'Q20_5': 'Releer Problema',
        'Q20_6': 'Probar Valores',
        'Q20_7': 'Explicar Problema'
    }
    
    missing_cols = [col for col in q20_cols if col not in df.columns]
    if missing_cols:
        st.warning(f"Columnas no encontradas: {missing_cols}")
        return
    
    df_q20 = df[q20_cols].copy()
    
    # Convertir "No sé" a 0 y hacer numérico
    for col in q20_cols:
        df_q20[col] = df_q20[col].replace(['No sé', 'No conozco'], 0)
        df_q20[col] = pd.to_numeric(df_q20[col], errors='coerce')
    
    df_q20 = df_q20.dropna()
    
    if df_q20.empty:
        st.warning("No hay datos válidos para Estrategias de Programación.")
        return
    
    promedios = df_q20.mean()
    promedio_general = promedios.mean()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📈 Promedio General", f"{promedio_general:.2f}/10")
    
    with col2:
        st.metric("📊 Total Respuestas", len(df_q20))
    
    with col3:
        mejor = promedios.idxmax()
        st.metric("🏆 Estrategia Preferida", q20_labels[mejor], f"{promedios[mejor]:.2f}/10")
    
    # Gráfico de barras
    st.subheader("📊 Frecuencia de Uso de Estrategias (1-10)")
    
    df_bar = pd.DataFrame({
        'Estrategia': [q20_labels[col] for col in promedios.index],
        'Promedio': promedios.values
    }).sort_values('Promedio', ascending=False)
    
    fig_bar = px.bar(
        df_bar, 
        x='Estrategia', 
        y='Promedio',
        title="Estrategias de Enseñanza - Programación",
        text='Promedio',
        color='Promedio',
        color_continuous_scale=COLOR_PALETTE['blue_scale']
    )
    fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_bar.update_layout(
        xaxis_tickangle=-45,
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig_bar, use_container_width=True, config=chart_config)

def dashboard_estrategias_pc(df):
    """
    Dashboard para Estrategias de Pensamiento Computacional (Q43)
    - Analiza estrategias específicas para enseñanza de PC
    """
    st.markdown("---")
    st.header("🧠 Estrategias PC")
    
    q43_cols = ['Q43_1', 'Q43_2', 'Q43_3', 'Q43_4', 'Q43_5', 'Q43_6', 'Q43_7']
    q43_labels = {
        'Q43_1': 'Explicar Respuesta',
        'Q43_2': 'Paso a Paso',
        'Q43_3': 'Revisar Notas',
        'Q43_4': 'Memorias Colectivas',
        'Q43_5': 'Releer Problema',
        'Q43_6': 'Probar Valores',
        'Q43_7': 'Explicar Problema'
    }
    
    missing_cols = [col for col in q43_cols if col not in df.columns]
    if missing_cols:
        st.warning(f"Columnas no encontradas: {missing_cols}")
        return
    
    df_q43 = df[q43_cols].copy()
    
    for col in q43_cols:
        df_q43[col] = df_q43[col].replace(['No sé', 'No conozco'], 0)
        df_q43[col] = pd.to_numeric(df_q43[col], errors='coerce')
    
    df_q43 = df_q43.dropna()
    
    if df_q43.empty:
        st.warning("No hay datos válidos para Estrategias PC.")
        return
    
    promedios = df_q43.mean()
    promedio_general = promedios.mean()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📈 Promedio General", f"{promedio_general:.2f}/10")
    
    with col2:
        st.metric("📊 Total Respuestas", len(df_q43))
    
    with col3:
        mejor = promedios.idxmax()
        st.metric("🏆 Estrategia Preferida", q43_labels[mejor], f"{promedios[mejor]:.2f}/10")
    
    # Comparación entre Programación (Q20) y PC (Q43)
    st.subheader("📊 Comparación: Programación vs PC")
    
    # Intentar obtener datos de Q20 para comparación
    q20_cols = ['Q20_1', 'Q20_2', 'Q20_3', 'Q20_4', 'Q20_5', 'Q20_6', 'Q20_7']
    q20_available = all(col in df.columns for col in q20_cols)
    
    if q20_available:
        df_q20 = df[q20_cols].copy()
        for col in q20_cols:
            df_q20[col] = df_q20[col].replace(['No sé', 'No conozco'], 0)
            df_q20[col] = pd.to_numeric(df_q20[col], errors='coerce')
        df_q20 = df_q20.dropna()
        
        if not df_q20.empty:
            promedios_q20 = df_q20.mean()
            
            # Crear DataFrame para comparación
            comparison_data = []
            for i, (q20_col, q43_col) in enumerate(zip(q20_cols, q43_cols)):
                comparison_data.append({
                    'Estrategia': q43_labels[q43_col],
                    'Programación': promedios_q20[q20_col],
                    'Pensamiento Computacional': promedios[q43_col],
                    'Diferencia': promedios[q43_col] - promedios_q20[q20_col]
                })
            
            df_comparison = pd.DataFrame(comparison_data)
            
            fig_comparison = go.Figure()
            
            fig_comparison.add_trace(go.Bar(
                name='Programación',
                x=df_comparison['Estrategia'],
                y=df_comparison['Programación'],
                marker_color=COLOR_PALETTE['primary']
            ))
            
            fig_comparison.add_trace(go.Bar(
                name='Pensamiento Computacional',
                x=df_comparison['Estrategia'],
                y=df_comparison['Pensamiento Computacional'],
                marker_color=COLOR_PALETTE['secondary']
            ))
            
            fig_comparison.update_layout(
                title='Comparación de Estrategias: Programación vs PC',
                xaxis_title='Estrategias',
                yaxis_title='Promedio (1-10)',
                barmode='group',
                height=400,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig_comparison, use_container_width=True, config=chart_config)
        else:
            # Solo mostrar PC si no hay datos de Q20
            df_bar = pd.DataFrame({
                'Estrategia': [q43_labels[col] for col in promedios.index],
                'Promedio': promedios.values
            })
            
            fig_bar = px.bar(
                df_bar, 
                x='Estrategia', 
                y='Promedio',
                title="Estrategias de Enseñanza - Pensamiento Computacional",
                text='Promedio',
                color='Promedio',
                color_continuous_scale=COLOR_PALETTE['blue_scale']
            )
            fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig_bar.update_layout(
                xaxis_tickangle=-45,
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True, config=chart_config)

def dashboard_conocimientos_pc(df):
    """
    Dashboard para Autorreporte de Conocimientos PC (Q22)
    - Analiza el conocimiento sobre conceptos de Pensamiento Computacional
    """
    st.markdown("---")
    st.header("🎓 Conocimientos PC")
    
    q22_cols = ['Q22_1', 'Q22_2', 'Q22_3', 'Q22_4', 'Q22_5', 'Q22_6']
    q22_labels = {
        'Q22_1': 'Medios Digitales',
        'Q22_2': 'Modelos y Simulaciones',
        'Q22_3': 'Procesador de Texto',
        'Q22_4': 'Automatizar Tareas',
        'Q22_5': 'Análisis de Datos',
        'Q22_6': 'Herramientas Computacionales'
    }
    
    # Respuestas correctas según PC (las que SÍ corresponden a PC)
    respuestas_correctas = {
        'Q22_1': 'No',   # Medios digitales - NO es PC
        'Q22_2': 'Sí',   # Modelos y simulaciones - SÍ es PC
        'Q22_3': 'No',   # Word - NO es PC
        'Q22_4': 'Sí',   # Automatizar tareas - SÍ es PC
        'Q22_5': 'Sí',   # Análisis de datos - SÍ es PC
        'Q22_6': 'Sí'    # Herramientas computacionales - SÍ es PC
    }
    
    missing_cols = [col for col in q22_cols if col not in df.columns]
    if missing_cols:
        st.warning(f"Columnas no encontradas: {missing_cols}")
        return
    
    df_q22 = df[q22_cols].copy()
    df_q22 = df_q22.dropna()
    
    if df_q22.empty:
        st.warning("No hay datos válidos para Conocimientos PC.")
        return
    
    # Calcular porcentajes de respuestas correctas
    porcentajes_correctos = {}
    for col in q22_cols:
        respuesta_correcta = respuestas_correctas[col]
        total_respuestas = len(df_q22[col])
        respuestas_correctas_count = (df_q22[col] == respuesta_correcta).sum()
        porcentajes_correctos[col] = (respuestas_correctas_count / total_respuestas) * 100
    
    promedio_conocimiento = sum(porcentajes_correctos.values()) / len(porcentajes_correctos)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📈 Conocimiento Promedio", f"{promedio_conocimiento:.1f}%")
    
    with col2:
        st.metric("📊 Total Respuestas", len(df_q22))
    
    with col3:
        mejor_concepto = max(porcentajes_correctos, key=porcentajes_correctos.get)
        st.metric("🏆 Mejor Comprendido", q22_labels[mejor_concepto][:10] + "...", 
                 f"{porcentajes_correctos[mejor_concepto]:.1f}%")
    
    # Gráfico de conocimientos
    st.subheader("📊 Nivel de Conocimiento por Concepto")
    
    df_bar = pd.DataFrame({
        'Concepto': [q22_labels[col] for col in q22_cols],
        'Porcentaje Correcto': [porcentajes_correctos[col] for col in q22_cols],
        'Es PC': [respuestas_correctas[col] for col in q22_cols]
    })
    
    # Color según si es PC o no
    colors = ['green' if x == 'Sí' else 'red' for x in df_bar['Es PC']]
    
    fig_bar = px.bar(
        df_bar, 
        x='Concepto', 
        y='Porcentaje Correcto',
        title="Conocimiento de Conceptos PC (% Respuestas Correctas)",
        text='Porcentaje Correcto',
        color='Es PC',
        color_discrete_map=COLOR_PALETTE['yes_no_colors']
    )
    fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_bar.update_layout(
        xaxis_tickangle=-45,
        height=400,
        yaxis_range=[0, 100]
    )
    st.plotly_chart(fig_bar, use_container_width=True, config=chart_config)
    
    # Tabla detallada
    with st.expander("📋 Ver detalles por concepto"):
        detailed_stats = []
        for col in q22_cols:
            si_count = (df_q22[col] == 'Sí').sum()
            no_count = (df_q22[col] == 'No').sum()
            total = len(df_q22[col])
            
            detailed_stats.append({
                'Concepto': q22_labels[col],
                'Respuesta Correcta': respuestas_correctas[col],
                'Respuestas "Sí"': f"{si_count} ({si_count/total*100:.1f}%)",
                'Respuestas "No"': f"{no_count} ({no_count/total*100:.1f}%)",
                '% Correcto': f"{porcentajes_correctos[col]:.1f}%"
            })
        
        st.dataframe(pd.DataFrame(detailed_stats), use_container_width=True)

def dashboard_demografia(df):
    """
    Dashboard demográfico y de formación completo
    - Analiza características demográficas de los participantes
    """
    st.markdown("---")
    st.header("👥 Demográfico")
    
    # Métricas generales
    total_participantes = len(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Participantes", total_participantes)
    
    with col2:
        if 'Q11' in df.columns:  # Sexo
            sexo_dist = df['Q11'].value_counts()
            sexo_mayoritario = sexo_dist.index[0] if len(sexo_dist) > 0 else "N/A"
            porcentaje = (sexo_dist.iloc[0] / total_participantes * 100) if len(sexo_dist) > 0 else 0
            st.metric("⚖️ Género Predominante", sexo_mayoritario, f"{porcentaje:.1f}%")
    
    with col3:
        if 'Q27' in df.columns:  # Formación TI
            formacion_ti = df['Q27'].value_counts()
            con_formacion = formacion_ti.get('Sí', 0)
            porcentaje_ti = (con_formacion / total_participantes * 100) if total_participantes > 0 else 0
            st.metric("💻 Con Formación TI", f"{porcentaje_ti:.1f}%", f"{con_formacion} docentes")
    
    with col4:
        if 'Q26' in df.columns:  # Nivel educativo
            nivel_counts = df['Q26'].value_counts()
            nivel_principal = nivel_counts.index[0] if len(nivel_counts) > 0 else "N/A"
            st.metric("🎓 Nivel Principal", nivel_principal[:12] + "...", f"{nivel_counts.iloc[0] if len(nivel_counts) > 0 else 0}")
    
    # Primera fila de gráficos
    col_left, col_right = st.columns(2)
    
    with col_left:
        if 'Q11' in df.columns:
            st.subheader("👫 Distribución por Género")
            sexo_counts = df['Q11'].value_counts()
            if not sexo_counts.empty:
                # Gráfico de barras horizontal para género
                fig_sexo = px.bar(
                    x=sexo_counts.values,
                    y=sexo_counts.index,
                    title="Participación por Género",
                    labels={'x': 'Cantidad de Participantes', 'y': 'Género'},
                    color=sexo_counts.index,
                    color_discrete_map=COLOR_PALETTE['gender_colors'],
                    orientation='h'
                )
                fig_sexo.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig_sexo, use_container_width=True, config=chart_config)
                
                # Mostrar porcentajes
                for genero, cantidad in sexo_counts.items():
                    porcentaje = (cantidad / total_participantes * 100)
                    st.write(f"**{genero}**: {cantidad} personas ({porcentaje:.1f}%)")
    
    with col_right:
        if 'Q27' in df.columns:  # Formación en TI
            st.subheader("💻 Formación en TI")
            formacion_ti = df['Q27'].value_counts()
            if not formacion_ti.empty:
                # Gráfico de barras para formación TI
                colors = ['lightgreen' if x == 'Sí' else 'lightcoral' for x in formacion_ti.index]
                fig_ti = px.bar(
                    x=formacion_ti.index,
                    y=formacion_ti.values,
                    title="¿Tiene formación en TI?",
                    labels={'x': 'Formación TI', 'y': 'Cantidad de Docentes'},
                    color=formacion_ti.index,
                    color_discrete_map=COLOR_PALETTE['yes_no_colors']
                )
                fig_ti.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig_ti, use_container_width=True, config=chart_config)
                
                # Mostrar porcentajes
                for respuesta, cantidad in formacion_ti.items():
                    porcentaje = (cantidad / total_participantes * 100)
                    st.write(f"**{respuesta}**: {cantidad} docentes ({porcentaje:.1f}%)")
    
    # Segunda fila - Nivel educativo
    if 'Q26' in df.columns:
        st.subheader("🎓 Niveles Educativos donde Enseñan")
        nivel_counts = df['Q26'].value_counts()
        if not nivel_counts.empty:
            # Gráfico de barras para nivel educativo
            fig_nivel = px.bar(
                x=nivel_counts.index,
                y=nivel_counts.values,
                title="Distribución por Nivel Educativo",
                labels={'x': 'Nivel Educativo', 'y': 'Cantidad de Docentes'},
                color=nivel_counts.values,
                color_continuous_scale=COLOR_PALETTE['blue_scale']
            )
            fig_nivel.update_layout(
                xaxis_tickangle=-45,
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig_nivel, use_container_width=True, config=chart_config)
            
            # Mostrar estadísticas adicionales
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Total niveles**: {len(nivel_counts)}")
            with col2:
                st.write(f"**Nivel más común**: {nivel_counts.index[0]}")
            with col3:
                st.write(f"**Docentes en ese nivel**: {nivel_counts.iloc[0]}")
    
    # Tercera fila - Análisis adicional si hay más columnas demográficas
    col_left, col_right = st.columns(2)
    
    with col_left:
        # Análisis de experiencia si existe alguna columna relacionada
        if 'Q25' in df.columns:  # Años de experiencia (si existe)
            st.subheader("📅 Experiencia Docente")
            experiencia_counts = df['Q25'].value_counts().head(10)  # Top 10
            if not experiencia_counts.empty:
                fig_exp = px.bar(
                    x=experiencia_counts.index,
                    y=experiencia_counts.values,
                    title="Distribución de Años de Experiencia",
                    labels={'x': 'Años de Experiencia', 'y': 'Cantidad de Docentes'},
                    color=experiencia_counts.values,
                    color_continuous_scale=COLOR_PALETTE['blue_scale']
                )
                fig_exp.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig_exp, use_container_width=True, config=chart_config)
        else:
            st.info("💡 Información adicional de experiencia no disponible")
    
    with col_right:
        # Resumen demográfico
        st.subheader("📊 Resumen Demográfico")
        
        resumen_data = []
        
        if 'Q11' in df.columns:
            sexo_counts = df['Q11'].value_counts()
            for genero, cantidad in sexo_counts.items():
                resumen_data.append({
                    'Categoría': 'Género',
                    'Valor': genero,
                    'Cantidad': cantidad,
                    'Porcentaje': f"{(cantidad/total_participantes*100):.1f}%"
                })
        
        if 'Q27' in df.columns:
            ti_counts = df['Q27'].value_counts()
            for respuesta, cantidad in ti_counts.items():
                resumen_data.append({
                    'Categoría': 'Formación TI',
                    'Valor': respuesta,
                    'Cantidad': cantidad,
                    'Porcentaje': f"{(cantidad/total_participantes*100):.1f}%"
                })
        
        if resumen_data:
            df_resumen = pd.DataFrame(resumen_data)
            st.dataframe(df_resumen, use_container_width=True, hide_index=True)
        else:
            st.info("💡 Datos demográficos en proceso de carga")

def dashboard_transferencia(df):
    """
    Dashboard para Transferencia de Conocimientos
    - Analiza la transferencia de conocimientos a estudiantes
    """
    st.markdown("---")
    st.header("🎯 Transferencia de Conocimientos")
    
    if 'Q36' not in df.columns:
        st.warning("No hay datos de transferencia disponibles.")
        return
    
    # Análisis de transferencia
    transferencia_counts = df['Q36'].value_counts()
    total_respuestas = len(df['Q36'].dropna())
    
    if total_respuestas == 0:
        st.warning("No hay datos válidos de transferencia.")
        return
    
    porcentaje_si = (transferencia_counts.get('Sí', 0) / total_respuestas) * 100
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("✅ Realizó Transferencia", f"{porcentaje_si:.1f}%", f"{transferencia_counts.get('Sí', 0)} docentes")
    
    with col2:
        st.metric("📊 Total Respuestas", total_respuestas)
    
    with col3:
        # Estudiantes totales si hay datos
        if 'Q38' in df.columns and 'Q39' in df.columns:
            hombres = pd.to_numeric(df['Q38'], errors='coerce').sum()
            mujeres = pd.to_numeric(df['Q39'], errors='coerce').sum()
            total_estudiantes = hombres + mujeres
            st.metric("👨‍🎓 Total Estudiantes", f"{int(total_estudiantes)}", f"H: {int(hombres)} | M: {int(mujeres)}")
    
    # Gráfico de transferencia
    col_left, col_right = st.columns(2)
    
    with col_left:
        # Sección de transferencia eliminada - gráfica de pie removida
        pass
    
    with col_right:
        # Distribución por grados si hay datos
        grado_cols = [f'Q37_{i}' for i in range(1, 12)]
        available_grados = [col for col in grado_cols if col in df.columns]
        
        if available_grados:
            st.subheader("📚 Grados con Transferencia")
            grados_labels = {
                'Q37_1': '1°', 'Q37_2': '2°', 'Q37_3': '3°', 'Q37_4': '4°',
                'Q37_5': '5°', 'Q37_6': '6°', 'Q37_7': '7°', 'Q37_8': '8°',
                'Q37_9': '9°', 'Q37_10': '10°', 'Q37_11': '11°'
            }
            
            grados_data = []
            for col in available_grados:
                if col in grados_labels:
                    count = (df[col] == 'Sí').sum() if col in df.columns else 0
                    grados_data.append({'Grado': grados_labels[col], 'Cantidad': count})
            
            if grados_data:
                df_grados = pd.DataFrame(grados_data)
                df_grados = df_grados[df_grados['Cantidad'] > 0]  # Solo mostrar grados con transferencia
                
                if not df_grados.empty:
                    fig_grados = px.bar(
                        df_grados,
                        x='Grado',
                        y='Cantidad',
                        title="Transferencia por Grado",
                        color='Cantidad',
                        color_continuous_scale=COLOR_PALETTE['blue_scale']
                    )
                    fig_grados.update_layout(height=300, showlegend=False)
                    st.plotly_chart(fig_grados, use_container_width=True, config=chart_config)

def mostrar_paleta_colores():
    """
    Función para mostrar la paleta de colores estándar del dashboard
    """
    st.markdown("---")
    st.header("🎨 Paleta de Colores Estándar")
    st.write("Esta sección muestra los colores utilizados consistentemente en todo el dashboard.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Colores Principales")
        st.markdown(f"""
        - **Primario**: <span style="color:{COLOR_PALETTE['primary']}">●</span> {COLOR_PALETTE['primary']} (Azul Colombia Programa)
        - **Secundario**: <span style="color:{COLOR_PALETTE['secondary']}">●</span> {COLOR_PALETTE['secondary']} (Verde Colombia)
        - **Acento**: <span style="color:{COLOR_PALETTE['accent']}">●</span> {COLOR_PALETTE['accent']} (Amarillo Colombia)
        - **Oscuro**: <span style="color:{COLOR_PALETTE['dark']}">●</span> {COLOR_PALETTE['dark']} (Azul Oscuro)
        """, unsafe_allow_html=True)
        
        st.subheader("✅ Colores Sí/No")
        st.markdown(f"""
        - **Sí/Positivo**: <span style="color:{COLOR_PALETTE['yes_no_colors']['Sí']}">●</span> {COLOR_PALETTE['yes_no_colors']['Sí']}
        - **No/Negativo**: <span style="color:{COLOR_PALETTE['yes_no_colors']['No']}">●</span> {COLOR_PALETTE['yes_no_colors']['No']}
        """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("👫 Colores de Género")
        for genero, color in COLOR_PALETTE['gender_colors'].items():
            st.markdown(f"- **{genero}**: <span style='color:{color}'>●</span> {color}", unsafe_allow_html=True)
        
        st.subheader("📊 Estados")
        st.markdown(f"""
        - **Éxito**: <span style="color:{COLOR_PALETTE['success']}">●</span> {COLOR_PALETTE['success']}
        - **Advertencia**: <span style="color:{COLOR_PALETTE['warning']}">●</span> {COLOR_PALETTE['warning']}
        - **Peligro**: <span style="color:{COLOR_PALETTE['danger']}">●</span> {COLOR_PALETTE['danger']}
        - **Información**: <span style="color:{COLOR_PALETTE['info']}">●</span> {COLOR_PALETTE['info']}
        """, unsafe_allow_html=True)

# ==========================================
# APLICACIÓN PRINCIPAL
# ==========================================
st.title("📚 Dashboard Integral - Codinghub Masters")

# Mostrar todos los dashboards en la misma página
dashboard_q19(df)
dashboard_habilidades_pc(df)
dashboard_colaboracion(df)
dashboard_estrategias_programacion(df)
dashboard_estrategias_pc(df)
dashboard_conocimientos_pc(df)
dashboard_demografia(df)
dashboard_transferencia(df)

# ==========================================
# GRAFICADOR PERSONALIZADO
# ==========================================
# Separador para el graficador
st.markdown("---")
st.header("🎨 Graficador Personalizado")
st.write("Utiliza esta herramienta para crear gráficos personalizados con cualquier combinación de variables.")
graficador(df, key_suffix="pares_expertos")

# ==========================================
# INFORMACIÓN TÉCNICA
# ==========================================
with st.expander("🎨 Ver Paleta de Colores Estándar"):
    mostrar_paleta_colores()

# ==========================================
# FOOTER Y CRÉDITOS
# ==========================================
st.markdown("---")
st.write("© 2025 Colombia Programa - Ministerio de Tecnologías de la Información y las Comunicaciones (MinTIC)")

# Formatear el HTML con las imágenes convertidas a base64
formatted_footer = FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64)

# Mostrar el footer en Streamlit
st.markdown(formatted_footer, unsafe_allow_html=True)