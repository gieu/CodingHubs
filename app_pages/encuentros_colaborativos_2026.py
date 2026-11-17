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
import actions.utils as utils
from actions.graficas_jesus_actions import graficas_jesus
from actions.resumen_actions import resumen_ejecutivo
from actions.momentos_actions import (
    mapa_calor_conductas_que, mapa_calor_conductas_como, lineas_conductas_como, burbujas_acciones_momento,
)
import os
# ==========================================
# CONFIGURACIÓN INICIAL
# ==========================================
chart_config = get_chart_config()

# ==========================================
# PALETA DE COLORES ESTÁNDAR
# ==========================================
# Colores principales del proyecto Colombia Programa
COLOR_PALETTE = {
    # Colores primarios - Paleta oficial para variables
    'primary': '#46BAD2',      # Azul oficial
    'secondary': '#00A651',    # Verde Colombia (mantener)
    'accent': '#ff7f00',       # Naranja oficial
    'dark': '#271D67',         # Morado oficial
    
    # Colores para gráficas
    'bar_single': '#1DB2E8',   # Azul para barras individuales
    'bar_positive': '#00A651', # Verde para valores positivos
    'bar_negative': '#E74C3C', # Rojo para valores negativos
    'pie_colors': ['#1DB2E8', '#00A651', '#FFB400', '#E74C3C', '#9B59B6', '#F39C12'],
    
    # Escalas de colores continuas - Basadas en paleta oficial
    'blue_scale': ['#E8F6FA', '#D1EEEF', '#B9E5F4', '#A2DCF0', '#8BD3EC', '#74CAE8', '#5DC1E4', '#46BAD2', '#3FA8BD', '#3896A8'],
    'green_scale': ['#E8F5E8', '#C8E6C8', '#A5D6A7', '#81C784', '#66BB6A', '#4CAF50', '#43A047', '#388E3C', '#2E7D32', '#1B5E20'],
    'orange_scale': ['#FFF4E6', '#FFE8CC', '#FFDBB3', '#FFCF99', '#FFC280', '#FFB566', '#FFA84D', '#ff7f00', '#E67300', '#CC6600'],
    'purple_scale': ['#EFEEFC', '#DFDDF9', '#CFCCF6', '#BFBBF3', '#AFAAF0', '#9F99ED', '#8F88EA', '#7F77E7', '#6F66E4', '#271D67'],
    # Colores categóricos - Paleta oficial
    'categorical': [
        '#46BAD2',  # Azul oficial
        '#00A651',  # Verde Colombia
        '#ff7f00',  # Naranja oficial
        '#271D67',  # Morado oficial
        '#E74C3C',  # Rojo (complementario)
        '#F39C12',  # Amarillo (complementario)
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

# Escalas de colores para Plotly - Paleta oficial
PLOTLY_COLOR_SCALES = {
    'primary': [[0, '#E8F6FA'], [1, '#46BAD2']],
    'success': [[0, '#E8F5E8'], [1, '#00A651']],
    'accent': [[0, '#FFF4E6'], [1, '#ff7f00']],
    'dark': [[0, '#EFEEFC'], [1, '#271D67']],
    'official_palette': ['#46BAD2', '#00A651', '#ff7f00', '#271D67']
}

# ==========================================
# FUNCIÓN HEADER PERSONALIZADA PARA ESTA PÁGINA
# ==========================================

def header_encuentros_colaborativos(color_fondo_navbar="#ff7f00"):
    """Genera el header personalizado con el logo de Coding Hubs específicamente para encuentros colaborativos."""
    import streamlit as st
    
    # Ruta del logo específico para esta página
    RUTA_LOGO_CODINGHUBS = "./assets/codinghubs.png"
    LOGO_CODINGHUBS_BASE64 = utils.imagen_a_base64(RUTA_LOGO_CODINGHUBS)
    
    # Deploy environment
    deploy_env = os.getenv("DEPLOY_ENV", "local")
    BASE_URL = "/"
    if deploy_env == 'prod':
        BASE_URL = "/codinghubs/"
    else:
        BASE_URL = "/"
    
    # Ocultar elementos de Streamlit
    st.markdown(HIDE_STREAMLIT_STYLE, unsafe_allow_html=True)

    # Generar el CSS personalizado con el color deseado
    custom_css = generar_css_personalizado(color_fondo_navbar)

    # Aplicar el CSS en Streamlit
    st.markdown(custom_css, unsafe_allow_html=True)

    # Navbar personalizado con logo específico de Coding Hubs
    navbar_codinghubs = NAVBAR_TEMPLATE.format(
        LOGO_NAVBAR_BASE64=LOGO_CODINGHUBS_BASE64,
        BASE_URL=BASE_URL
    )
    st.markdown(navbar_codinghubs, unsafe_allow_html=True)

# Definir el color personalizado para esta página
color_fondo_navbar = "#ff7f00"  # Naranja para distinguir esta página

# Crear navbar con el color personalizado y logo específico
header_encuentros_colaborativos(color_fondo_navbar)
# ==========================================
# CARGA DE DATOS
# ==========================================
# URL del CSV

import unicodedata

CONDUCTAS_QUE_GRUPOS = {
    'Anécdotas': 'Transferencia de la experticia',
    'Vocabulario': 'Transferencia de la experticia',
    'Estrategias': 'Transferencia de la experticia',
    'Preguntas estudiantes': 'Instrucción centrada en el estudiante',
    'Características estudiantes': 'Instrucción centrada en el estudiante',
    'Reflexión género': 'Enfoque de género',
    'Diferencias género': 'Enfoque de género',
    'Estrategias género': 'Enfoque de género',
}

CONDUCTAS_QUE = list(CONDUCTAS_QUE_GRUPOS.keys())
GRUPOS_CONDUCTAS_QUE = list(dict.fromkeys(CONDUCTAS_QUE_GRUPOS.values()))

CONDUCTAS_COMO_GRUPOS = {
    'Humor': 'Construcción de ambiente colaborativo',
    'Ánimo': 'Construcción de ambiente colaborativo',
    'Valoración': 'Construcción de ambiente colaborativo',
    'Destacar habilidades': 'Construcción de ambiente colaborativo',
    'Solicitar opinión': 'Habilidades de mentoría y disposición a aprender',
    'Recursos didácticos': 'Habilidades de mentoría y disposición a aprender',
    'Acompañar actividad': 'Habilidades de mentoría y disposición a aprender',
    'Pedir ayuda': 'Habilidades de mentoría y disposición a aprender',
    'Reconocer aprendizaje': 'Habilidades de mentoría y disposición a aprender',
    'Reflexión mejoras': 'Habilidades de mentoría y disposición a aprender',
    'Perspectiva diferente': 'Comunicación en espacios de aprendizaje',
    'Contribución activa': 'Comunicación en espacios de aprendizaje',
    'Rol predominante': 'Comunicación en espacios de aprendizaje',
}

CONDUCTAS_COMO = list(CONDUCTAS_COMO_GRUPOS.keys())
GRUPOS_CONDUCTAS_COMO = list(dict.fromkeys(CONDUCTAS_COMO_GRUPOS.values()))
CONDUCTAS_COMO_EC2_ONLY = ['Destacar habilidades']

ACCIONES_INSTANTANEAS_2026 = [
    'Dialogan activamente entre pares',
    'Realizan una actividad práctica',
    'Un(a) docente hace una participación o intervención',
    'Escuchan una explicación temática de un par experto',
    'Escuchan instrucciones para el desarrollo de una actividad de un par experto',
    'Escuchan una explicación temática de un facilitador del encuentro (ej. mentor)',
    'Escuchan instrucciones para el desarrollo de una actividad de un facilitador del encuentro (ej. mentor)',
    'Observan material audiovisual (ej. video explicativo sobre nodos o pensamiento computacional)',
    'Hacen preguntas o solicitan aclaraciones',
    'Toman notas o registran información',
    'Observan un ejemplo, demostración o modelamiento',
    'Usan materiales o recursos del encuentro, como las guías para la enseñanza del pensamiento computacional.',
    'Exploran o desarrollan actividades con la Micro:bit',
    'Usan dispositivos como celular o computador con fines educativos',
    'Conversan sobre un tema personal o no relacionado con el encuentro',
    'Están distraídos o desconectados de las actividades',
    'Otra',
]

ACCIONES_INSTANTANEAS_ALIASES = {
    'Usan dispositivos electrónicos (micro:bit, computador, celular, etc.)': 'Usan dispositivos como celular o computador con fines educativos',
    'Usan materiales o recursos del encuentro (guías, fichas, etc.)': 'Usan materiales o recursos del encuentro, como las guías para la enseñanza del pensamiento computacional.',
}

ACCIONES_INSTANTANEAS_LABELS = {
    'Dialogan activamente entre pares': 'Dialogan entre pares',
    'Realizan una actividad práctica': 'Realizan actividad práctica',
    'Un(a) docente hace una participación o intervención': 'Docente participa o interviene',
    'Escuchan una explicación temática de un par experto': 'Explicación de par experto',
    'Escuchan instrucciones para el desarrollo de una actividad de un par experto': 'Instrucciones de par experto',
    'Escuchan una explicación temática de un facilitador del encuentro (ej. mentor)': 'Explicación de facilitador',
    'Escuchan instrucciones para el desarrollo de una actividad de un facilitador del encuentro (ej. mentor)': 'Instrucciones de facilitador',
    'Observan material audiovisual (ej. video explicativo sobre nodos o pensamiento computacional)': 'Observan material audiovisual',
    'Hacen preguntas o solicitan aclaraciones': 'Preguntan o piden aclaraciones',
    'Toman notas o registran información': 'Toman notas',
    'Observan un ejemplo, demostración o modelamiento': 'Observan ejemplo o modelamiento',
    'Usan materiales o recursos del encuentro, como las guías para la enseñanza del pensamiento computacional.': 'Usan guías de pensamiento computacional',
    'Exploran o desarrollan actividades con la Micro:bit': 'Actividades con Micro:bit',
    'Usan dispositivos como celular o computador con fines educativos': 'Usan celular o computador',
    'Conversan sobre un tema personal o no relacionado con el encuentro': 'Conversan tema no relacionado',
    'Están distraídos o desconectados de las actividades': 'Distraídos o desconectados',
    'Otra': 'Otra',
}

ACCIONES_INSTANTANEAS_GRUPOS = {
    'Transferencia y Diálogo': [
        'Dialogan activamente entre pares',
        'Un(a) docente hace una participación o intervención',
        'Hacen preguntas o solicitan aclaraciones',
        'Toman notas o registran información',
    ],
    'Actividades y Recursos': [
        'Realizan una actividad práctica',
        'Usan materiales o recursos del encuentro, como las guías para la enseñanza del pensamiento computacional.',
        'Exploran o desarrollan actividades con la Micro:bit',
        'Usan dispositivos como celular o computador con fines educativos',
    ],
    'Escucha': [
        'Escuchan una explicación temática de un par experto',
        'Escuchan instrucciones para el desarrollo de una actividad de un par experto',
        'Escuchan una explicación temática de un facilitador del encuentro (ej. mentor)',
        'Escuchan instrucciones para el desarrollo de una actividad de un facilitador del encuentro (ej. mentor)',
    ],
    'Otras': [
        'Observan un ejemplo, demostración o modelamiento',
        'Observan material audiovisual (ej. video explicativo sobre nodos o pensamiento computacional)',
        'Conversan sobre un tema personal o no relacionado con el encuentro',
        'Están distraídos o desconectados de las actividades',
        'Otra',
    ],
}

ACCIONES_INSTANTANEAS_GRUPO_POR_ACCION = {
    accion: grupo
    for grupo, acciones in ACCIONES_INSTANTANEAS_GRUPOS.items()
    for accion in acciones
}

COLORES_GRUPOS_INSTANTANEAS = {
    'Transferencia y Diálogo': '#00A651',
    'Actividades y Recursos': '#271D67',
    'Escucha': '#46BAD2',
    'Otras': '#ff7f00',
}

MOMENTOS_ENCUENTROS_2026 = {
    'EC1': {
        1: 'Bienvenida y Rompehielos',
        2: '¿Qué es un nodo y qué hacemos?',
        3: 'Lo que sabemos y lo que debemos saber sobre PC',
        4: 'Trayectoria y materiales de PC',
        5: 'Cronograma de mentorías',
        6: 'Cierre y entrega de materiales',
    },
    'EC2': {
        1: 'Retomando cuatro elementos claves',
        2: 'Retos Bebras',
        3: 'Compartiendo experiencias',
        4: 'Programando Micro:bit',
        5: 'Cierre y reflexiones',
    },
}

TIPO_ALIASES = {
    'Anecdotas': 'Anécdotas',
    'Anécdotas': 'Anécdotas',
    'Animo': 'Ánimo',
    'Valoracion': 'Valoración',
    'Solicitar opinion': 'Solicitar opinión',
    'Recursos didacticos': 'Recursos didácticos',
    'Acompanar actividad': 'Acompañar actividad',
    'Pedir ayuda': 'Pedir ayuda',
    'Reconocer aprendizaje': 'Reconocer aprendizaje',
    'Reflexion mejoras': 'Reflexión mejoras',
    'Perspectiva diferente': 'Perspectiva diferente',
    'Contribucion activa': 'Contribución activa',
    'Rol predominante': 'Rol predominante',
}


def normalizar_tipo_conducta(df):
    if 'tipo' not in df.columns:
        return df

    df = df.copy()
    df['tipo'] = df['tipo'].astype(str).str.strip()
    df['tipo'] = df['tipo'].replace(['nan', '', 'NaN', 'None'], 'Comunicación en espacios de aprendizaje')
    df['tipo'] = df['tipo'].replace(TIPO_ALIASES)
    return df


def incluye_ec2_2026(df):
    if 'Encuentro' not in df.columns:
        return False

    encuentros = df['Encuentro'].dropna().astype(str).str.lower()
    return encuentros.str.contains('2026').any() and (
        encuentros.str.contains('ec2|encuentro 2|2026_2|2026-2|_2|-2').any()
    )


def conductas_como_aplicables(df):
    conductas = CONDUCTAS_COMO.copy()
    if not incluye_ec2_2026(df):
        conductas = [c for c in conductas if c not in CONDUCTAS_COMO_EC2_ONLY]
    return conductas


def normalizar_acciones_instantaneas(df):
    if 'accionMomento' not in df.columns:
        return df

    df = df.copy()
    df['accionMomento'] = df['accionMomento'].astype(str).str.strip()
    df['accionMomento'] = df['accionMomento'].replace(['nan', 'NaN', 'None', ''], pd.NA)
    df['accionMomento'] = df['accionMomento'].replace(ACCIONES_INSTANTANEAS_ALIASES)
    return df


def etiqueta_accion_instantanea(accion):
    return ACCIONES_INSTANTANEAS_LABELS.get(accion, envolver_etiqueta(accion, 36))


def grupo_accion_instantanea(accion):
    return ACCIONES_INSTANTANEAS_GRUPO_POR_ACCION.get(accion, 'Otras')


def etiqueta_encuentro_2026(valor):
    texto = str(valor).strip().lower()
    if texto in ['ec1', '2026_1', '2026-1', 'encuentro 1']:
        return 'EC1'
    if texto in ['ec2', '2026_2', '2026-2', 'encuentro 2']:
        return 'EC2'
    if '2026_1' in texto or '2026-1' in texto or texto.endswith('_1') or texto.endswith('-1'):
        return 'EC1'
    if '2026_2' in texto or '2026-2' in texto or texto.endswith('_2') or texto.endswith('-2'):
        return 'EC2'
    return str(valor)


def columna_momento_instantaneas(df):
    candidatos = [
        'NÃºmero de momento',
        'Número de momento',
        'numMomento',
        'numeroMomento',
        'Numero de momento',
        'Momento',
        'momento',
    ]
    for columna in candidatos:
        if columna in df.columns:
            return columna
    return None


def columna_id_instantanea(df):
    candidatos = [
        'idInstantanea',
        'id_instante',
        'ID de instantÃ¡nea',
        'ID de instantánea',
        'idEncuentro',
        'IDEncuentro',
        'ID de respuesta',
        'idRespuesta',
    ]
    disponibles = [col for col in candidatos if col in df.columns]
    if 'numInstantanea' in df.columns:
        disponibles.append('numInstantanea')
    return disponibles


def extraer_numero_momento(serie):
    texto = serie.astype(str).str.extract(r'(\d+)', expand=False)
    return pd.to_numeric(texto, errors='coerce')


def preparar_burbujas_instantaneas_por_momento(df_inst_unicas, df_acciones):
    columna_momento = columna_momento_instantaneas(df_inst_unicas)
    if columna_momento is None or 'Encuentro' not in df_inst_unicas.columns:
        return pd.DataFrame(), columna_momento

    df_base = df_inst_unicas.copy()
    df_acc = df_acciones.copy()
    if columna_momento not in df_acc.columns:
        columnas_merge = [
            col for col in ['idEncuentro', 'numInstantanea', 'Encuentro', 'Fase']
            if col in df_base.columns and col in df_acc.columns
        ]
        if columnas_merge:
            df_acc = df_acc.merge(
                df_base[[*columnas_merge, columna_momento]].drop_duplicates(),
                on=columnas_merge,
                how='left'
            )

    if columna_momento not in df_acc.columns or df_acc.empty:
        return pd.DataFrame(), columna_momento

    df_base['_encuentro_corto'] = df_base['Encuentro'].apply(etiqueta_encuentro_2026)
    df_acc['_encuentro_corto'] = df_acc['Encuentro'].apply(etiqueta_encuentro_2026)
    df_base['_momento_num'] = extraer_numero_momento(df_base[columna_momento])
    df_acc['_momento_num'] = extraer_numero_momento(df_acc[columna_momento])
    df_base = df_base[df_base['_momento_num'].notna()].copy()
    df_acc = df_acc[df_acc['_momento_num'].notna()].copy()

    if df_base.empty or df_acc.empty:
        return pd.DataFrame(), columna_momento

    columnas_id = columna_id_instantanea(df_base)
    dedup_denominador = [
        col for col in ['_encuentro_corto', '_momento_num', *columnas_id]
        if col in df_base.columns
    ]
    denominadores = (
        df_base.drop_duplicates(subset=dedup_denominador)
        .groupby(['_encuentro_corto', '_momento_num'])
        .size()
        .reset_index(name='Total_instantaneas_momento')
    )

    columnas_evento_accion = [
        col for col in ['_encuentro_corto', '_momento_num', 'accionMomento', *columnas_id]
        if col in df_acc.columns
    ]
    numeradores = (
        df_acc.drop_duplicates(subset=columnas_evento_accion)
        .groupby(['_encuentro_corto', '_momento_num', 'accionMomento'])
        .size()
        .reset_index(name='Instantaneas_con_accion')
    )

    burbujas = numeradores.merge(
        denominadores,
        on=['_encuentro_corto', '_momento_num'],
        how='left'
    )
    burbujas = burbujas[burbujas['Total_instantaneas_momento'] > 0].copy()
    burbujas['Porcentaje'] = (
        burbujas['Instantaneas_con_accion']
        / burbujas['Total_instantaneas_momento']
        * 100
    )
    burbujas = burbujas[burbujas['Porcentaje'] > 0].copy()
    burbujas['Porcentaje_redondeado'] = burbujas['Porcentaje'].round(0).astype(int)
    burbujas['Grupo'] = burbujas['accionMomento'].apply(grupo_accion_instantanea)
    burbujas['Accion_etiqueta'] = burbujas['accionMomento'].apply(etiqueta_accion_instantanea)
    burbujas['Momento_etiqueta'] = burbujas.apply(
        lambda fila: etiqueta_momento_burbuja(fila['_encuentro_corto'], fila['_momento_num']),
        axis=1
    )
    return burbujas, columna_momento


def etiqueta_momento_burbuja(encuentro, momento):
    momento_int = int(momento)
    descripcion = MOMENTOS_ENCUENTROS_2026.get(encuentro, {}).get(momento_int)
    if descripcion:
        return f"M{momento_int}<br>{envolver_etiqueta(descripcion, 18)}"
    return f"M{momento_int}"


def graficar_burbujas_instantaneas_por_momento(df_inst_unicas, df_acciones):
    burbujas, columna_momento = preparar_burbujas_instantaneas_por_momento(
        df_inst_unicas,
        df_acciones
    )
    st.subheader("Gráfica de Instantáneas - Mapa de burbujas por momento")
    st.caption(
        "Tamaño = % de instantáneas del momento en que se registró cada acción. "
        "El denominador cambia para cada momento."
    )

    if columna_momento is None:
        st.info("No se encontró una columna de momento para construir el mapa de burbujas.")
        return
    if burbujas.empty:
        st.info("No hay acciones con porcentaje mayor a 0 para el mapa de burbujas por momento.")
        return

    graficas_renderizadas = 0
    for encuentro in sorted(burbujas['_encuentro_corto'].dropna().unique()):
        df_encuentro = burbujas[burbujas['_encuentro_corto'] == encuentro].copy()
        if df_encuentro.empty:
            continue

        acciones_ordenadas = [
            accion for grupo in ACCIONES_INSTANTANEAS_GRUPOS.values()
            for accion in grupo
            if accion in df_encuentro['accionMomento'].unique()
        ]
        acciones_ordenadas += [accion for accion in df_encuentro['accionMomento'].unique()
                              if accion not in acciones_ordenadas]
        acciones_plot = [etiqueta_accion_instantanea(accion) for accion in acciones_ordenadas]
        momentos = sorted(df_encuentro['_momento_num'].dropna().unique())
        ticktext = [etiqueta_momento_burbuja(encuentro, momento) for momento in momentos]

        fig = go.Figure()
        for grupo, color in COLORES_GRUPOS_INSTANTANEAS.items():
            df_grupo = df_encuentro[df_encuentro['Grupo'] == grupo].copy()
            if df_grupo.empty:
                continue
            fig.add_trace(go.Scatter(
                x=df_grupo['_momento_num'],
                y=df_grupo['Accion_etiqueta'],
                mode='markers+text',
                name=grupo,
                marker=dict(
                    color=color,
                    size=df_grupo['Porcentaje'],
                    sizemode='area',
                    sizeref=2.0 * df_encuentro['Porcentaje'].max() / (54 ** 2),
                    sizemin=8,
                    opacity=0.82,
                    line=dict(width=0)
                ),
                text=df_grupo['Porcentaje_redondeado'].astype(str) + '%',
                textposition='middle center',
                textfont=dict(color='white', size=11),
                customdata=df_grupo[[
                    'accionMomento',
                    'Instantaneas_con_accion',
                    'Total_instantaneas_momento',
                    'Porcentaje',
                    'Grupo'
                ]],
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Momento: M%{x}<br>"
                    "Grupo: %{customdata[4]}<br>"
                    "%{customdata[1]} de %{customdata[2]} instantáneas<br>"
                    "%{customdata[3]:.1f}%<extra></extra>"
                )
            ))

        for momento in momentos:
            fig.add_vline(
                x=momento + 0.5,
                line_width=1,
                line_color='rgba(39, 29, 103, 0.08)'
            )

        fig.update_layout(
            title=f"{encuentro}: acciones observadas por momento",
            height=max(620, 36 * len(acciones_plot) + 220),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=13, color='#4A5568'),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.22,
                xanchor='left',
                x=0,
                title=''
            ),
            margin=dict(l=245, r=45, t=95, b=145),
            xaxis=dict(
                title='',
                tickmode='array',
                tickvals=momentos,
                ticktext=ticktext,
                tickangle=0,
                range=[min(momentos) - 0.55, max(momentos) + 0.55],
                showgrid=False,
                zeroline=False,
                side='top',
                tickfont=dict(size=11, color='#5A6473')
            ),
            yaxis=dict(
                title='',
                tickmode='array',
                tickvals=acciones_plot,
                ticktext=acciones_plot,
                categoryorder='array',
                categoryarray=list(reversed(acciones_plot)),
                showgrid=False,
                zeroline=False,
                tickfont=dict(size=11, color='#5A6473'),
                automargin=True
            )
        )
        fig.add_annotation(
            x=0,
            y=-0.31,
            xref='paper',
            yref='paper',
            showarrow=False,
            align='left',
            font=dict(size=11, color='#6B7280'),
            text=(
                "Nota: una misma instantánea puede registrar múltiples acciones simultáneamente; "
                "por eso los porcentajes de las acciones dentro de un mismo momento no suman 100%."
            )
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            config=chart_config
        )
        graficas_renderizadas += 1

    if graficas_renderizadas == 0:
        st.info("El filtro actual no contiene instantáneas de EC1 o EC2 para graficar por separado.")


def normalizar_texto_busqueda(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower().strip()


def contiene_patrones(texto, patrones):
    texto_normalizado = normalizar_texto_busqueda(texto)
    return all(patron in texto_normalizado for patron in patrones)


def normalizar_respuesta_clave(texto):
    return normalizar_texto_busqueda(texto).rstrip('.')


def envolver_etiqueta(texto, ancho=38):
    palabras = str(texto).split()
    lineas = []
    linea_actual = []

    for palabra in palabras:
        candidato = " ".join([*linea_actual, palabra])
        if linea_actual and len(candidato) > ancho:
            lineas.append(" ".join(linea_actual))
            linea_actual = [palabra]
        else:
            linea_actual.append(palabra)

    if linea_actual:
        lineas.append(" ".join(linea_actual))

    return "<br>".join(lineas)


def respuestas_desde_pregunta(df, patrones, orden_respuestas):
    columnas_id_respuesta = [
        'ID de respuesta',
        'idRespuesta',
        'IDEncuentro',
        'idEncuentro',
        'Número de momento',
        'Evento',
        'Encuentro',
        'nodo',
    ]

    if {'pregunta', 'respuesta'}.issubset(df.columns):
        pregunta_mask = df['pregunta'].apply(lambda valor: contiene_patrones(valor, patrones))
        df_respuestas = df[pregunta_mask].copy()
        if not df_respuestas.empty:
            columnas_unicas = [
                col for col in [*columnas_id_respuesta, 'pregunta', 'respuesta']
                if col in df_respuestas.columns
            ]
            df_respuestas = df_respuestas[columnas_unicas].drop_duplicates()
            return df_respuestas, 'respuesta'

    for columna in df.columns:
        if contiene_patrones(columna, patrones):
            columnas_unicas = [
                col for col in [*columnas_id_respuesta, columna]
                if col in df.columns
            ]
            df_respuestas = df[columnas_unicas].copy()
            df_respuestas = df_respuestas.rename(columns={columna: 'respuesta'})
            df_respuestas = df_respuestas[
                df_respuestas['respuesta'].notna()
                & (df_respuestas['respuesta'].astype(str).str.strip() != '')
            ]
            return df_respuestas, 'respuesta'

    return pd.DataFrame(columns=['respuesta']), 'respuesta'


def preparar_resumen_respuestas(df_base, patrones, orden_respuestas):
    df_respuestas, respuesta_col = respuestas_desde_pregunta(df_base, patrones, orden_respuestas)

    if df_respuestas.empty:
        return pd.DataFrame()

    df_respuestas[respuesta_col] = df_respuestas[respuesta_col].astype(str).str.strip()
    respuestas_canonicas = {
        normalizar_respuesta_clave(respuesta): respuesta for respuesta in orden_respuestas
    }
    df_respuestas[respuesta_col] = (
        df_respuestas[respuesta_col]
        .apply(lambda respuesta: respuestas_canonicas.get(normalizar_respuesta_clave(respuesta), respuesta))
    )
    resumen = (
        df_respuestas.groupby(respuesta_col)
        .size()
        .reset_index(name='Total')
        .rename(columns={respuesta_col: 'Respuesta'})
    )
    resumen['Respuesta'] = pd.Categorical(
        resumen['Respuesta'],
        categories=orden_respuestas,
        ordered=True
    )
    resumen = resumen.dropna(subset=['Respuesta']).sort_values('Respuesta')
    total = resumen['Total'].sum()

    if total == 0:
        return pd.DataFrame()

    resumen['Porcentaje'] = (resumen['Total'] / total * 100).round(1)
    return resumen


def graficar_distribucion_respuestas(df_base, patrones, orden_respuestas, titulo, envolver_respuestas=False):
    resumen = preparar_resumen_respuestas(df_base, patrones, orden_respuestas)

    if resumen.empty:
        return False

    resumen['Etiqueta'] = (
        resumen['Respuesta'].astype(str).apply(envolver_etiqueta)
        if envolver_respuestas
        else resumen['Respuesta'].astype(str)
    )

    fig = px.bar(
        resumen,
        x='Porcentaje',
        y='Etiqueta',
        orientation='h',
        title=titulo,
        labels={'Porcentaje': 'Porcentaje de respuestas (%)', 'Etiqueta': ''},
        text='Porcentaje',
        color='Porcentaje',
        color_continuous_scale=COLOR_PALETTE['blue_scale'],
        category_orders={
            'Etiqueta': [envolver_etiqueta(respuesta) for respuesta in orden_respuestas]
            if envolver_respuestas else orden_respuestas
        },
        hover_data={'Total': True, 'Porcentaje': ':.1f'}
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(
        height=360,
        showlegend=False,
        coloraxis_showscale=False,
        xaxis=dict(range=[0, max(resumen['Porcentaje'].max() * 1.2, 10)]),
        yaxis=dict(autorange='reversed'),
        margin=dict(l=20, r=40, t=70, b=40)
    )
    st.plotly_chart(fig, use_container_width=True, config=chart_config)
    return True


def graficar_indicadores_pregunta(df_base, indicadores, titulo):
    if not {'pregunta', 'respuesta'}.issubset(df_base.columns):
        st.info(f"No se encontró información para: {titulo}")
        return

    df_indicadores = df_base[df_base['pregunta'].isin(indicadores.keys())].copy()
    if df_indicadores.empty:
        st.info(f"No se encontró información para: {titulo}")
        return

    df_indicadores['Indicador'] = df_indicadores['pregunta'].map(indicadores)
    resumen = (
        df_indicadores.groupby('Indicador')
        .size()
        .reset_index(name='Total')
    )
    resumen['Indicador'] = pd.Categorical(
        resumen['Indicador'],
        categories=list(indicadores.values()),
        ordered=True
    )
    resumen = resumen.sort_values('Indicador')

    fig = px.bar(
        resumen,
        x='Total',
        y='Indicador',
        orientation='h',
        title=titulo,
        labels={'Total': 'Menciones', 'Indicador': ''},
        text='Total',
        color='Indicador',
        color_discrete_sequence=['#46BAD2', '#271D67']
    )
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(
        height=320,
        showlegend=False,
        xaxis=dict(range=[0, max(resumen['Total'].max() * 1.2, 1)]),
        yaxis=dict(autorange='reversed'),
        margin=dict(l=20, r=40, t=70, b=40)
    )
    st.plotly_chart(fig, use_container_width=True, config=chart_config)


def filtrar_por_encuentro_seleccionado(df, fase_seleccionada):
    if 'Encuentro' not in df.columns and 'Evento' in df.columns:
        if fase_seleccionada in ["Todos los encuentros", "Match ambos años", "Match solo 2026"]:
            return df.copy()
        evento_map = {
            '2026_1': 'EC1',
            '2026_2': 'EC2',
            'EC1': 'EC1',
            'EC2': 'EC2',
        }
        evento = evento_map.get(str(fase_seleccionada))
        if evento is None:
            return df.copy()
        return df[df['Evento'].astype(str) == evento].copy()

    if 'Encuentro' not in df.columns:
        return df

    if fase_seleccionada == "Todos los encuentros":
        return df.copy()

    if fase_seleccionada == "Match ambos años":
        if 'nodo' not in df.columns:
            return df.iloc[0:0].copy()
        nodos_match = df.groupby('nodo')['Encuentro'].nunique().reset_index()
        nodos_match = nodos_match[nodos_match['Encuentro'] > 3]['nodo'].tolist()
        return df[df['nodo'].isin(nodos_match)].copy()

    if fase_seleccionada == "Match solo 2026":
        if 'nodo' not in df.columns:
            return df.iloc[0:0].copy()
        encuentros = df['Encuentro'].fillna('').astype(str)
        nodos_match_2026 = (
            df[encuentros.str.contains('2026_')]
            .groupby('nodo')['Encuentro']
            .nunique()
            .reset_index()
        )
        nodos_match_2026 = nodos_match_2026[nodos_match_2026['Encuentro'] > 1]['nodo'].tolist()
        df_filtrado = df[df['nodo'].isin(nodos_match_2026)].copy()
        return df_filtrado[df_filtrado['Encuentro'].fillna('').astype(str).str.contains('2026_')].copy()

    return df[df['Encuentro'] == fase_seleccionada].copy()

# Tabla de correspondencia Match entre fases
# MATCH_ENCUENTROS = {
#     'Fase 1': ['EC24', 'EC12', 'EC37', 'EC1', 'EC15', 'EC22', 'EC39', 'EC35', 'EC41', 'EC40', 'EC34', 'EC10', 'EC16', 'EC36'],
#     'Fase 2': ['EC1', 'EC10', 'EC11', 'EC12', 'EC13', 'EC14', 'EC15', 'EC3', 'EC4', 'EC5', 'EC6', 'EC7', 'EC8', 'EC9']
# }

# MATCH_ENCUENTROS_INSTANTANEAS = {
#     'Fase 1': ['EC24', 'EC12', 'EC37', 'EC1', 'EC15', 'EC22',  'EC35', 'EC41', 'EC40', 'EC34', 'EC10', 'EC16', 'EC36'],
#     'Fase 2': ['EC1', 'EC10', 'EC11', 'EC12', 'EC13', 'EC14',  'EC3', 'EC4', 'EC5', 'EC6', 'EC7', 'EC8', 'EC9']
# }

# URL del CSV
import os
from io import BytesIO
DEPLOY_ENV = os.getenv("DEPLOY_ENV")

# --- Cargar Datos con Cache ---
@st.cache_data(ttl=600)
def load_data(file, mostrar_aviso=True):
    try:
        df = pd.read_csv(file, encoding='utf-8')
    except Exception:
        if mostrar_aviso:
            st.warning("No se pudo cargar una de las fuentes actuales. Los demás análisis siguen disponibles.")
        return pd.DataFrame()
    df.columns = df.columns.str.strip()
    # Older sheets identify an encounter by its phase and code.
    if not {'idEncuentro', 'IDEncuentro'}.intersection(df.columns) and {'Fase', 'Encuentro'}.issubset(df.columns):
        df['idEncuentro'] = df['Fase'].astype(str) + ':' + df['Encuentro'].astype(str)
    return df


def opciones_encuentros(df):
    opciones = ['Todos los encuentros']
    if 'nodo' in df.columns:
        opciones.append('Match ambos años')
        if df['Encuentro'].astype(str).str.contains('2026').any():
            opciones.append('Match solo 2026')
    return opciones + sorted(df['Encuentro'].dropna().unique().tolist())


def seleccionar_fase_actual(df, key):
    if 'Fase' not in df.columns:
        return df, None
    fases = sorted(df['Fase'].dropna().unique().tolist())
    fase = st.selectbox('Selecciona la fase de los datos:', ['Todas las fases'] + fases, key=key)
    return (df, None) if fase == 'Todas las fases' else (df[df['Fase'] == fase].copy(), fase)


def filtrar_fase_actual(df, fase):
    return df[df['Fase'] == fase].copy() if fase is not None and 'Fase' in df.columns else df


def filtrar_conductas_actuales(df, tipo_filtro):
    grupos = GRUPOS_CONDUCTAS_QUE if tipo_filtro == 'Conductas asociadas al que' else GRUPOS_CONDUCTAS_COMO
    # Keep historical subtypes inside their observed group, including ones absent from the 2026 catalog.
    return df[df['Conducta'].isin(grupos) & df['participante'].notna()].copy()

def expandir_ambos_participantes(df):
    """
    Expande las filas con participante='Ambos' en dos filas:
    una para 'Pares expertos' y otra para 'Docentes acompañados'
    """
    # Separar las filas con "Ambos" de las demás
    df_ambos = df[df['participante'] == 'Ambos'].copy()
    df_otros = df[df['participante'] != 'Ambos'].copy()
    
    if not df_ambos.empty:
        # Crear dos copias: una para Pares expertos y otra para Docentes acompañados
        df_pares = df_ambos.copy()
        df_pares['participante'] = 'Pares expertos'
        
        df_docentes = df_ambos.copy()
        df_docentes['participante'] = 'Docentes acompañados'
        
        # Combinar todos los DataFrames
        df_resultado = pd.concat([df_otros, df_pares, df_docentes], ignore_index=True)
        
        return df_resultado
    else:
        # Si no hay filas con "Ambos", devolver el DataFrame original
        return df

def resumen_ejecutivo_momentos():
    """Resumen ejecutivo de 2026: conductas por tipo de participante y distribución por género."""
    resumen_ejecutivo(load_data(URL_MOMENTOS_EC), load_data(URL_DOCENTES_UNICOS, mostrar_aviso=False))


URL_DOCENTES_UNICOS = "https://docs.google.com/spreadsheets/d/1nCnSS2qt45U8Bh8n6YobT8Tyw_LLPSN86Vgzs3oq-wg/export?format=csv&gid=2015426318"
URL_MOMENTOS_EC = "https://docs.google.com/spreadsheets/d/1pfcVzbsb2N9hbRR3wEsuEfuaU76EwBuac8moRMXNd78/export?format=csv&gid=1073044251"
URL_AFIRMACIONES_EC = "https://docs.google.com/spreadsheets/d/1dbQaOF24h5FzGXbw3X2Gx4cU9Vjgdh-22kNKo2jXPDE/export?format=csv&gid=1583679053"


def momentos():
    """Pestaña Momentos: conductas asociadas al qué y al cómo, por momento (sin filtros)."""
    df_afirmaciones = load_data(URL_AFIRMACIONES_EC)
    st.subheader("📊 Conductas asociadas al qué")
    mapa_calor_conductas_que(df_afirmaciones)
    st.subheader("📊 Conductas asociadas al cómo")
    mapa_calor_conductas_como(df_afirmaciones)

    st.subheader("📈 Conductas del cómo por tipo de participante")
    lineas_conductas_como(load_data(URL_MOMENTOS_EC))

    st.subheader("🫧 Acciones por momento")
    burbujas_acciones_momento(load_data(URL_INSTANTANEAS_ACCIONES))


URL_INSTANTANEAS_ACCIONES = "https://docs.google.com/spreadsheets/d/1dU6-Hb5MW252A_PF3iaOqhX95W1tXF1J5BWrCIhD_u8/export?format=csv&gid=134781920"


def instantaneas():
    """Pestaña Instantáneas: gráficas sobre la hoja de instantáneas (sin filtros)."""
    df_inst = load_data(URL_INSTANTANEAS_ACCIONES)
    graficas_jesus(df_inst)


# ==========================================
# APLICACIÓN PRINCIPAL
# ==========================================
st.title("🤝  Análisis Encuentros Colaborativos 2026 e Instantáneas")

st.markdown("""
Esta página está dedicada al análisis profundo de los **encuentros colaborativos** entre docentes, 
explorando tanto las actitudes como las prácticas de colaboración en el contexto educativo.
""")

# Crear las pestañas principales
tab1, tab2, tab3 = st.tabs([" Resumen Ejecutivo", "📊 Momentos", "⚡ Instantáneas"])

with tab1:
    # Mostrar resumen ejecutivo
    resumen_ejecutivo_momentos()

with tab2:
    
    momentos()

with tab3:
    st.header("⚡ Instantáneas - Métricas Rápidas")
    st.markdown("""
    Vista rápida de métricas clave y visualizaciones instantáneas sobre redes y 
    comunidades colaborativas.
    """)
    instantaneas()


# Pie de página
st.markdown("---")
st.write("© 2026 Colombia Programa - Encuentros Colaborativos 2026 - Ministerio de Tecnologías de la Información y las Comunicaciones (MinTIC)")

# Formatear el HTML con las imágenes convertidas a base64
formatted_footer = FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64)

# Mostrar el footer en Streamlit
st.markdown(formatted_footer, unsafe_allow_html=True)
