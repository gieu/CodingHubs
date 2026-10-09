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
            config={**chart_config, 'editable': False}
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
    """Resumen ejecutivo conciso de encuentros colaborativos"""
    
    # Cargar datos conductas vertical 
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRxpmEEQR_RrzpGXMe8_XenUwHQPWFtT96SgOoDMAHNzW_eShHBXNHJaSwdOw4xMQ/pub?output=csv"
    df = load_data(url)
    
    if df.empty:
        st.warning("No hay datos disponibles para generar el resumen ejecutivo.")
        return
    
    df, fase_datos = seleccionar_fase_actual(df, 'fase_resumen_2026')
    # Selector de fase
    st.header("📋 Resumen Ejecutivo - Encuentros Colaborativos 2026")
    
    if 'Encuentro' in df.columns:
        fases_disponibles = sorted(df['Encuentro'].dropna().unique())
        opciones_fase = opciones_encuentros(df)
        
        fase_seleccionada = st.selectbox(
            "Selecciona el encuentro:",
            options=opciones_fase,
            help="Escoge el encuentro específico para el análisis ejecutivo"
        )
        
        # Filtrar datos por fase
        if fase_seleccionada == "Todos los encuentros":
            df_filtered = df.copy()
        elif fase_seleccionada == "Match ambos años":
            # Filtrar solo los encuentros que están en la tabla de correspondencia
            # Cada fase tiene su propia lista de encuentros permitidos
            if 'Encuentro' in df.columns and 'Fase' in df.columns:
                # Filtrar Fase 1 con su lista (la columna Fase contiene números: 1 y 2)
                nodos_match = df.groupby('nodo')['Encuentro'].nunique().reset_index()
                nodos_match = nodos_match[nodos_match['Encuentro'] > 3]['nodo'].tolist()
                
                # Combinar ambos DataFrames
                df_filtered = df[df['nodo'].isin(nodos_match)].copy()
                #st.write(df_filtered.groupby(['nodo', 'Encuentro'])['idEncuentro'].nunique())
            else:
                st.error("No se encontraron las columnas 'Encuentro' y 'Fase' necesarias para el filtro Match.")
                return
        else:
            df_filtered = df[df['Encuentro'] == fase_seleccionada].copy()
    else:
        df_filtered = df.copy()
        fase_seleccionada = "Datos disponibles"
    
    if df_filtered.empty:
        st.warning("No hay datos válidos para el resumen ejecutivo.")
        return

    # Filtrar por conductas específicas
    if 'Conducta' in df_filtered.columns:
        df_filtered['Conducta'] = df_filtered['Conducta'].astype(str).str.strip()
        
        # Reemplazar valores NaN, vacíos o 'nan' con "Comunicación en espacios de aprendizaje"
        df_filtered['Conducta'] = df_filtered['Conducta'].replace(['nan', '', 'NaN', 'None'], 'Comunicación en espacios de aprendizaje')
        df_filtered.loc[df_filtered['Conducta'].isna(), 'Conducta'] = 'Comunicación en espacios de aprendizaje'
        
        # Limpiar también la columna 'tipo' si existe
        if 'tipo' in df_filtered.columns:
            df_filtered['tipo'] = df_filtered['tipo'].astype(str).str.strip()
            df_filtered['tipo'] = df_filtered['tipo'].replace(['nan', '', 'NaN', 'None'], 'Comunicación en espacios de aprendizaje')
            df_filtered.loc[df_filtered['tipo'].isna(), 'tipo'] = 'Comunicación en espacios de aprendizaje'
        
        df_filtered = df_filtered[
            (df_filtered['participante'].notna()) & (df_filtered['participante'].astype(str).str.strip() != '')
        ].copy()
        
        df_filtered = expandir_ambos_participantes(df_filtered)
        df_analysis = df_filtered.copy()
        
        if df_analysis.empty:
            st.warning("No hay datos de las conductas analizadas para la fase seleccionada.")
            return
    else:
        st.error("La columna 'Conducta' no existe en los datos.")
        return
    
    # RESUMEN GENERAL
    st.markdown("### **Resumen General:**")

    # Métricas principales - Calcular el total real de encuentros sin filtros de conducta
    total_encuentros_real = int(df_filtered.groupby('Encuentro')['idEncuentro'].nunique().sum()) if 'Encuentro' in df_filtered.columns else 0
    total_participantes = df_analysis['participante'].nunique() if 'participante' in df_analysis.columns else 0
    total_observaciones = len(df_analysis)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**- Total de encuentros:** {total_encuentros_real}")
    with col2:
        st.markdown(f"**- Tipos de participantes:** {total_participantes}")

    
    # Distribución por conducta
    if 'Conducta' in df_analysis.columns:
        conducta_counts = df_analysis['Conducta'].value_counts()
        conducta_percentages = round((conducta_counts / len(df_analysis) * 100), 1)
        
        st.markdown("**Distribución por conducta:**")
        for conducta, porcentaje in conducta_percentages.items():
            st.markdown(f"- {conducta}: {porcentaje}%")
    
    st.markdown("---")
    
    # ANÁLISIS POR PARTICIPANTE
    if 'participante' in df_analysis.columns:
        participantes_unicos = df_analysis['participante'].unique()

        # Definir el orden específico de participantes
        orden_participantes = ['Pares expertos', 'Docentes acompañados', 'Ambos']

        # Filtrar solo los participantes que existen en los datos y mantener el orden
        participantes_ordenados = [p for p in orden_participantes if p in participantes_unicos]

        # Agregar cualquier participante que esté en los datos pero no en la lista (al final)
        participantes_adicionales = [p for p in participantes_unicos if p not in orden_participantes]
        participantes_finales = participantes_ordenados + participantes_adicionales

        def mostrar_participante(participante, col=None):
            df_participante = df_analysis[df_analysis['participante'] == participante].copy()
            df_participante_completo = df_filtered[df_filtered['participante'] == participante].copy()
            # st.write("debug")            
            # st.write(df_participante)

            if not df_participante.empty:
                if col is None:
                    st.markdown(f"### **{participante}:**")
                    encuentros_participante = int(df_participante_completo.groupby('Encuentro')['idEncuentro'].nunique().sum()) if 'idEncuentro' in df_participante_completo.columns and not df_participante_completo.empty else int(df_participante['idEncuentro'].nunique()) if 'idEncuentro' in df_participante.columns else 0
                    observaciones_participante = len(df_participante)
                    if 'Número de momento' in df_participante.columns:
                        momento_mas_activo = df_participante['Número de momento'].value_counts().idxmax()
                        obs_momento_activo = df_participante['Número de momento'].value_counts().max()
                        
                    else:
                        momento_mas_activo = "N/A"
                        obs_momento_activo = 0
                    if 'Conducta' in df_participante.columns:
                        conducta_principal = df_participante['Conducta'].value_counts().index[0]
                        porcentaje_conducta_principal = round((df_participante['Conducta'].value_counts().iloc[0] / len(df_participante) * 100), 1)
                    else:
                        conducta_principal = "N/A"
                        porcentaje_conducta_principal = 0
                    if 'tipo' in df_participante.columns:
                        tipo_principal = df_participante['tipo'].value_counts().index[0]
                        tipos_diversos = df_participante['tipo'].nunique()
                    else:
                        tipo_principal = "N/A"
                        tipos_diversos = 0
                    st.markdown(f"- **Participación en encuentros:** {encuentros_participante} de {total_encuentros_real} ({(encuentros_participante/total_encuentros_real*100):.1f}%)")
                    if 'Encuentro' in df_participante.columns:
                        fase_momento_activo = df_participante[df_participante['Número de momento'] == momento_mas_activo]['Encuentro'].iloc[0]
                        st.markdown(f"- **Momento más activo:** Momento {momento_mas_activo} - Encuentro {fase_momento_activo} ({obs_momento_activo} observaciones)")
                    else:
                        st.markdown(f"- **Momento más activo:** Momento {momento_mas_activo} ({obs_momento_activo} observaciones)")
                    st.markdown(f"- **Conducta principal:** {conducta_principal} ({porcentaje_conducta_principal}%)")
                    st.markdown(f"- **Comportamiento predominante:** {tipo_principal}")
                    st.markdown(f"- **Diversidad de comportamientos:** {tipos_diversos} tipos diferentes")
                    st.markdown("")
                else:
                    with col:
                        st.markdown(f"### **{participante}:**")
                        encuentros_participante = int(df_participante_completo['idEncuentro'].nunique()) if 'idEncuentro' in df_participante_completo.columns and not df_participante_completo.empty else int(df_participante['idEncuentro'].nunique()) if 'idEncuentro' in df_participante.columns else 0
                        observaciones_participante = len(df_participante)
                        if 'Número de momento' in df_participante.columns:
                            momento_mas_activo = df_participante[['Encuentro','Número de momento']].value_counts().idxmax()
                            obs_momento_activo = df_participante[['Encuentro','Número de momento']].value_counts().max()
                            #st.write( df_participante[['Encuentro','Número de momento']].value_counts())
                            #st.write(momento_mas_activo)
                        else:
                            momento_mas_activo = "N/A"
                            obs_momento_activo = 0
                        if 'Conducta' in df_participante.columns:
                            conducta_principal = df_participante['Conducta'].value_counts().index[0]
                            porcentaje_conducta_principal = round((df_participante['Conducta'].value_counts().iloc[0] / len(df_participante) * 100), 1)
                        else:
                            conducta_principal = "N/A"
                            porcentaje_conducta_principal = 0
                        if 'tipo' in df_participante.columns:
                            tipo_principal = df_participante['tipo'].value_counts().index[0]
                            tipos_diversos = df_participante['tipo'].nunique()
                        else:
                            tipo_principal = "N/A"
                            tipos_diversos = 0
                        st.markdown(f"- **Participación en encuentros:** {encuentros_participante} de {total_encuentros_real} ({(encuentros_participante/total_encuentros_real*100):.1f}%)")
                        if 'idEncuentro' in df_participante.columns:
                            #fase_momento_activo = df_participante[df_participante['Número de momento'] == momento_mas_activo]['Encuentro'].iloc[0]
                            st.markdown(f"- **Momento más activo:** Momento {momento_mas_activo[1]} - Encuentro {momento_mas_activo[0]} ({obs_momento_activo} observaciones)")
                        else:
                            st.markdown(f"- **Momento más activo:** Momento {momento_mas_activo[1]} - Encuentro {momento_mas_activo[0]} ({obs_momento_activo} observaciones)")
                        st.markdown(f"- **Conducta principal:** {conducta_principal} ({porcentaje_conducta_principal}%)")
                        st.markdown(f"- **Comportamiento predominante:** {tipo_principal}")
                        st.markdown(f"- **Diversidad de comportamientos:** {tipos_diversos} tipos diferentes")
                        st.markdown("")

        if len(participantes_finales) > 0:
            st.markdown("### **Análisis por Participante:**")
            # Primera fila: Pares expertos y Docentes acompañados
            primera_fila = [p for p in ['Pares expertos', 'Docentes acompañados'] if p in participantes_finales]
            if len(primera_fila) > 0:
                col1, col2 = st.columns(2)
                for i, participante in enumerate(primera_fila):
                    if i == 0:
                        mostrar_participante(participante, col1)
                    elif i == 1:
                        mostrar_participante(participante, col2)
                st.markdown("---")
            # Segunda fila: Ambos (solo)
            if 'Ambos' in participantes_finales:
                mostrar_participante('Ambos')
                st.markdown("---")
            # Participantes adicionales (si los hay)
            participantes_ya_mostrados = ['Pares expertos', 'Docentes acompañados', 'Ambos']
            participantes_restantes = [p for p in participantes_finales if p not in participantes_ya_mostrados]
            if len(participantes_restantes) > 1:
                st.markdown("#### **Otros Participantes:**")
                for participante in participantes_restantes:
                    mostrar_participante(participante)
                    st.markdown("---")
    # ANÁLISIS DE GÉNERO (si disponible) - momentos_sexos_vertical
    url_2 = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT7ngk1_bT8zj18I7yzTKeI74316aXaUvKgyx8ww8OzjL0l1_1ewFwcJqW3hBFyuw/pub?output=csv"
    df_genero = load_data(url_2, mostrar_aviso=False)
    if df_genero.empty:
        df_genero = load_data("https://docs.google.com/spreadsheets/d/e/2PACX-1vSK48GsEKzIzoB0TERqse6L3EeRte_5cgTMn8_nOG8G4M2dry3FxRJks9t3R-fwCQ/pub?output=csv")
        if not df_genero.empty:
            st.info("La fuente de género del resumen no está disponible; se usa la fuente de género actual de Momentos.")
    df_genero = filtrar_fase_actual(df_genero, fase_datos)
    
    if not df_genero.empty and 'sexo' in df_genero.columns:
        # Filtrar por fase
        if 'Encuentro' in df_genero.columns:
            if fase_seleccionada == "Todos los encuentros":
                df_genero = df_genero.copy()
            elif fase_seleccionada == "Match ambos años":
            # Filtrar solo los encuentros que están en la tabla de correspondencia
                if 'Encuentro' in df_genero.columns:
                    # Filtrar Fase 1 con su lista (la columna Fase contiene números: 1 y 2)
                    nodos_match = df_genero.groupby('nodo')['Encuentro'].nunique().reset_index()
                    nodos_match = nodos_match[nodos_match['Encuentro'] > 3]['nodo'].tolist()
                    df_genero = df_genero[df_genero['nodo'].isin(nodos_match)].copy()
                else:
                    st.error("No se encontró la columna 'Encuentro' necesaria para el filtro Match.")
                    return
            else:
                df_genero = df_genero[df_genero['Encuentro'] == fase_seleccionada].copy()
        
        # Filtrar por conductas
        if 'Conducta' in df_genero.columns:
            df_genero['Conducta'] = df_genero['Conducta'].astype(str).str.strip()
            
            # Reemplazar valores NaN, vacíos o 'nan' con "Comunicación en espacios de aprendizaje"
            df_genero['Conducta'] = df_genero['Conducta'].replace(['nan', '', 'NaN', 'None'], 'Comunicación en espacios de aprendizaje')
            df_genero.loc[df_genero['Conducta'].isna(), 'Conducta'] = 'Comunicación en espacios de aprendizaje'
            
            df_genero_filtered = df_genero.copy()
            
            if not df_genero_filtered.empty and 'nombre' in df_genero_filtered.columns:
                st.markdown("### **Distribución por Género:**")
                
                # Limpiar datos de género
                df_genero_filtered['sexo'] = df_genero_filtered['sexo'].astype(str).str.strip().str.title()
                
                # Calcular distribución
                total_participantes_genero = df_genero_filtered['nombre'].nunique()
                distribucion_genero = df_genero_filtered.groupby('sexo')['nombre'].nunique()
                
                for genero, cantidad in distribucion_genero.items():
                    porcentaje = round((cantidad / total_participantes_genero * 100), 1)
                    st.markdown(f"- **{genero}:** {cantidad} participantes ({porcentaje}%)")

def momentos():
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
        """)
    

    with st.expander("📚 Información sobre la Estructura de los Encuentros"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🎯 **Primer Encuentro Colaborativo**
            
            **Momento 1: Bienvenida y Rompehielos**
            
            Los docentes intercambiaron aspectos significativos de su vida como nombre de familiares, lugares especiales, entre otros.
            
            **Momento 2: ¿Qué es un nodo y qué hacemos?**
            
            Se explicó a los participantes en qué consiste Colombia Programa y el componente de Nodos de Pensamiento Computacional, como también aspectos claves de la experticia colaborativa.
            
            **Momento 3: Lo que sabemos y lo que debemos saber sobre el pensamiento computacional (citas rápidas)**
            
            Intercambio de experiencias pedagógicas con la dinámica de speed dating, a partir de preguntas relacionadas con actividades de clase que implican resolver problemas, seguimiento de pasos, reconocimiento de patrones, uso de modelos, entre otros.
            
            **Momento 4: Lo que sabemos y lo que debemos saber sobre el pensamiento computacional (construcción y socialización de definición de PC)**
            
            De forma creativa, los docentes acompañados construyeron una definición de pensamiento computacional basada en las experiencias compartidas en las citas rápidas. Posteriormente, se presentó la definición de PC.
            
            **Momento 5: Programando la tarjeta Micro:bit (momento de instrucción)**
            
            Se presentaron aspectos técnicos generales de la Micro:bit (qué es, sus partes, el entorno de programación de Makecode) y se invitó a los docentes acompañados a explorar la tarjeta.
            
            **Momento 6: Programando la tarjeta Micro:bit (sesión de retos)**
            
            Los docentes acompañados, con apoyo de los pares expertos, resolvieron dos retos haciendo uso de la Micro:bit con la programación en bloques desde Makecode.
            
            **Momento 7: Socialización PlayGround**
            
            Los pares expertos socializaron el reto PlayGround. Además, se compartió con los docentes acompañados la experiencia de implementación en uno de los retos.
            
            **Momento 8: Elaboración cronograma**
            
            Los pares expertos y los docentes acompañados crearon un cronograma de acompañamiento, designando fechas y espacios para tratar temas relacionados a la enseñanza del PC y del reto PlayGround.
            """)
        
        with col2:
            st.markdown("""
            ### 🎯 **Segundo Encuentro Colaborativo**
            
            **Momento 1: Retomando tres elementos claves**
            
            A través de una actividad de memoria y reflexión, los docentes revisaron conceptos esenciales sobre pensamiento computacional.
            
            **Momento 2: Poniendo a prueba nuestro pensamiento computacional con retos Bebras**
            
            Los docentes resolvieron retos tipo Bebras que promueven el uso de las subhabilidades del pensamiento computacional. Posteriormente, contrastaron estrategias y discutieron su aplicabilidad en el aula.
            
            **Momento 3: Compartiendo experiencias de enseñanza de pensamiento computacional**
            
            Mediante el protocolo de diálogo profesional 3x3x3+5, los docentes compartieron experiencias de aula y reflexionaron colectivamente sobre prácticas exitosas y desafíos comunes en la enseñanza del pensamiento computacional.
            
            **Momento 4: ¿Qué sigue ahora? Trayectoria y materiales para la enseñanza del pensamiento computacional desde transición hasta 11°**
            
            Los participantes exploraron las guías nacionales de pensamiento computacional, y a través de una carrera de observación, identificaron recursos y actividades aplicables a diferentes niveles educativos.
            
            **Momento 5: Fortaleciendo nuestros conocimientos sobre Micro:bit**
            
            Los docentes, guiados por los pares expertos, realizaron ejercicios prácticos de programación en MakeCode utilizando bloques condicionales y de comparación, aplicando conceptos de lógica y resolución de problemas.
            
            **Momento 6: Reflexiones de cierre y conclusiones de la sesión**
            
            Se realizó una reflexión individual y colectiva sobre los aprendizajes alcanzados, los logros del trabajo conjunto entre nodo y sede acompañada, y los compromisos para continuar fortaleciendo la colaboración docente.
            """)
        
        st.info("💡 **Nota**: Cada momento tiene objetivos específicos que contribuyen al desarrollo de competencias colaborativas y pedagógicas en el contexto del programa Coding Hubs.")

    with st.expander("📚 Estructura EC 1 y EC 2 de 2026"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            ### 🎯 **EC 1 de 2026**
            
            **Momento 1: Bienvenida y Rompehielos**
            
            Para conocerse, los docentes intercambiaron aspectos significativos de su vida como nombre de familiares, lugares especiales, entre otros.
            
            **Momento 2: ¿Qué es un nodo y qué hacemos?**
            
            Se explicó a los participantes en qué consiste Colombia Programa y el componente de Nodos de Pensamiento Computacional, como también aspectos claves de la experticia colaborativa.
            
            **Momento 3: Lo que sabemos y lo que debemos saber sobre el pensamiento computacional**
            
            Intercambio de experiencias pedagógicas con la dinámica de speed dating (citas rápidas), a partir de preguntas relacionadas con actividades de clase que implican resolver problemas, seguimiento de pasos, reconocimiento de patrones, uso de modelos, entre otros.
            
            **Momento 4: Trayectoria y materiales para la enseñanza del pensamiento computacional desde transición hasta 11°**
            
            Presentación de guías sobre pensamiento computacional, basado en aprendizaje por proyectos y actividades desconectadas.
            
            **Momento 5: Cronograma de mentorías expansión de la experticia**
            
            Los pares expertos y los docentes acompañados crearon un cronograma de acompañamiento, designando fechas y espacios para tratar temas relacionados a la enseñanza del PC.
            
            **Momento 6: Actividades de cierre y entrega de materiales**
            
            Se realizó la autoevaluación a partir de los objetivos del encuentro, se aplicó una encuesta de satisfacción y se hizo entrega de guías sobre pensamiento computacional a la sede de transferencia.
            """)

        with col2:
            st.markdown("""
            ### 🎯 **EC 2 de 2026**
            
            **Momento 1: Retomando cuatro elementos claves**
            
            A través de una actividad de memoria y reflexión, los docentes revisaron conceptos esenciales sobre pensamiento computacional abordados en el primer encuentro, identificando cómo ha evolucionado su comprensión del tema y cómo lo relacionan con su práctica pedagógica.
            
            **Momento 2: Poniendo a prueba nuestro pensamiento computacional con retos Bebras**
            
            Los docentes resolvieron retos tipo Bebras que promueven el uso de las subhabilidades del pensamiento computacional. Posteriormente, contrastaron estrategias y discutieron su aplicabilidad en el aula.
            
            **Momento 3: Compartiendo experiencias de enseñanza de pensamiento computacional**
            
            Mediante el protocolo de diálogo profesional 3x3x3+5, los docentes compartieron experiencias de aula y reflexionan colectivamente sobre prácticas exitosas y desafíos comunes en la enseñanza del pensamiento computacional.
            
            **Momento 4: Programando la micro:bit para fortalecer el pensamiento computacional**
            
            Los docentes, guiados por los pares expertos, realizaron ejercicios prácticos de programación en MakeCode utilizando bloques condicionales y de comparación, aplicando conceptos de lógica y resolución de problemas.
            
            **Momento 5: Reflexiones de cierre y conclusiones de la sesión**
            
            El encuentro concluyó con una reflexión individual y colectiva sobre los aprendizajes alcanzados, los logros del trabajo conjunto entre nodo y sede acompañada, y los compromisos para continuar fortaleciendo la colaboración docente.
            """)
    
    st.markdown("---")
    url="https://docs.google.com/spreadsheets/d/e/2PACX-1vRxpmEEQR_RrzpGXMe8_XenUwHQPWFtT96SgOoDMAHNzW_eShHBXNHJaSwdOw4xMQ/pub?output=csv"
    df_temp = load_data(url)
    df_temp, fase_datos = seleccionar_fase_actual(df_temp, 'fase_momentos_2026')
    df = df_temp.copy()

    # Selector de fase al inicio
    st.header("🔍 Selección de Encuentro a Analizar")
    if not df_temp.empty and 'Encuentro' in df_temp.columns:
        fases_disponibles = sorted(df_temp['Encuentro'].dropna().unique())
        # Agregar opciones "Todas las fases" y "Match"
        opciones_fase = opciones_encuentros(df_temp)
        
        fase_seleccionada = st.selectbox(
            "Selecciona la fase a analizar:",
            options=opciones_fase,
            help="Escoge el/los encuentros que deseas analizar en todos los gráficos, selecciona 'Todos los encuentros' para incluir todos los datos, o 'Match' para analizar solo los encuentros emparejados entre encuentros"
        )
        
        st.info(f"📋 **Análisis para: {fase_seleccionada}**")
    else:
        st.warning("No se encontró la columna 'Encuentro' en los datos o los datos están vacíos.")
        return
    
    st.markdown("---")
    st.subheader("📊 Mapa de Calor - Conductas-Momentos")


    # Cargar y filtrar datos por fase seleccionada
    if not df.empty and 'Encuentro' in df.columns:
        if fase_seleccionada == "Todos los encuentros":
            # No filtrar, mantener todos los encuentros
            df = df.copy()
        elif fase_seleccionada == "Match ambos años":
            if 'Encuentro' in df.columns:
                ## filtrar nodos que tengan más de 3 encuentros únicos para asegurar que sean nodos con datos en ambos años
                nodos_match = df.groupby('nodo')['Encuentro'].nunique().reset_index()
                nodos_match = nodos_match[nodos_match['Encuentro'] > 3]['nodo'].tolist()
                df = df[df['nodo'].isin(nodos_match)].copy()
                totales_df = df.groupby('Encuentro')['idEncuentro'].nunique()
                text_totales = "\n".join([f"- {encuentro}: {total} observaciones" for encuentro, total in totales_df.items()])
                st.info(f"🔗 **Analizando {len(df['idEncuentro'].unique())} encuentros emparejados: {text_totales}**")
            else:
                st.error("No se encontró la columna 'Encuentro' necesaria para el filtro Match.")
                return
        elif fase_seleccionada == "Match solo 2026":
            if 'Encuentro' in df.columns:
                ## filtrar nodos que tengan más de 1 encuentro en 2026 para asegurar que sean nodos con datos en el año 2026
                nodos_match_2026 = df[df['Encuentro'].str.contains('2026_')].groupby('nodo')['Encuentro'].nunique().reset_index()
                nodos_match_2026 = nodos_match_2026[nodos_match_2026['Encuentro'] > 1]['nodo'].tolist()
                df = df[df['nodo'].isin(nodos_match_2026)].copy()
                df = df[df['Encuentro'].str.contains('2026_')].copy()
                st.info(f"🔗 **Analizando {len(df['idEncuentro'].unique())} encuentros de 2026**")
        else:
            # Filtrar por la fase específica seleccionada
            df = df[df['Encuentro'] == fase_seleccionada].copy()
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
    
    # Limpiar espacios en blanco en la columna Conducta y reemplazar NaN o vacíos
    df['Conducta'] = df['Conducta'].astype(str).str.strip()
    
    # Reemplazar valores NaN, vacíos o 'nan' con "Comunicación en espacios de aprendizaje"
    df['Conducta'] = df['Conducta'].replace(['nan', '', 'NaN', 'None'], 'Comunicación en espacios de aprendizaje')
    df.loc[df['Conducta'].isna(), 'Conducta'] = 'Comunicación en espacios de aprendizaje'
    df = normalizar_tipo_conducta(df)
    
    # Selector para tipo de filtro de conductas
    st.subheader("🎯 Filtro de Conductas")
    
    # Definir los grupos de conductas asociadas al qué para EC 2026.
    Conductas_permitidas = GRUPOS_CONDUCTAS_QUE
    conductas_como_permitidas = conductas_como_aplicables(df)
    
    # Crear selector para tipo de filtro
    tipo_filtro = st.selectbox(
        "Selecciona el tipo de conductas a analizar:",
        options=[
            "Conductas asociadas al que",
            "Conductas asociadas al como"
        ],
        help="Escoge si quieres analizar solo las conductas específicas o todas las demás"
    )
    
    df_filtered = expandir_ambos_participantes(filtrar_conductas_actuales(df, tipo_filtro))
    st.info('Tipos observados incluidos: ' + ', '.join(sorted(df_filtered['tipo'].dropna().unique())))

    # Filtrar para que solo aparezca un Encuentro único por cada tipo y número de momento
    df_map = df_filtered.drop_duplicates(subset=['idEncuentro', 'tipo', 'Número de momento','Encuentro'])
    
    if df_map.empty:
        st.warning("No hay datos válidos después de aplicar los filtros.")
        st.info(f"Valores únicos en 'Conducta' (limpiados): {df['Conducta'].unique().tolist()}")
        st.info(f"Conductas buscadas: {Conductas_permitidas}")
        return

    # Usar directamente la columna "Número de momento"
    # Crear una tabla de frecuencias para el mapa de calor
    heatmap_data = df_map.groupby(['Número de momento', 'tipo']).size().reset_index(name='Frecuencia')
    
    # Crear tabla pivote para el mapa de calor
    pivot_data = heatmap_data.pivot(index='tipo', columns='Número de momento', values='Frecuencia').fillna(0)
    
    # Definir el orden específico deseado según las conductas
    orden_especifico = [
        *CONDUCTAS_QUE,
        *CONDUCTAS_COMO
    ]

    # Crear un DataFrame con todas las conductas esperadas y todos los momentos
    momentos_unicos = sorted(df_map['Número de momento'].unique())
    
    # Filtrar el orden específico según el tipo de filtro seleccionado
    if tipo_filtro == "Conductas asociadas al que":
        conductas_esperadas = CONDUCTAS_QUE
    else:  # "Conductas asociadas al como"
        conductas_esperadas = conductas_como_permitidas

    conductas_esperadas = list(conductas_esperadas) + [
        tipo for tipo in sorted(df_map['tipo'].dropna().unique())
        if tipo not in conductas_esperadas
    ]
    
    # Crear un DataFrame completo con todas las combinaciones esperadas
    combinaciones_completas = pd.MultiIndex.from_product(
        [conductas_esperadas, momentos_unicos],
        names=['tipo', 'Número de momento']
    )
    df_completo = pd.DataFrame(index=combinaciones_completas).reset_index()
    
    # Merge con pivot_data original para mantener los valores existentes
    pivot_data_reset = pivot_data.stack().reset_index()
    pivot_data_reset.columns = ['tipo', 'Número de momento', 'Frecuencia']
    
    # Combinar con el DataFrame completo
    df_merged = df_completo.merge(pivot_data_reset, on=['tipo', 'Número de momento'], how='left')
    df_merged['Frecuencia'] = df_merged['Frecuencia'].fillna(0)
    
    # Pivotar nuevamente para obtener la estructura deseada
    pivot_data = df_merged.pivot(index='tipo', columns='Número de momento', values='Frecuencia').fillna(0)
    
    # Asegurar que el orden de las filas sea el especificado en conductas_esperadas
    pivot_data = pivot_data.reindex(conductas_esperadas, fill_value=0)

    # Filtrar solo los tipos que existen en los datos y mantener el orden especificado
    orden_relevante = [t for t in orden_especifico if t in pivot_data.index]

    # Agregar cualquier tipo que esté en los datos pero no en la lista especificada (al final)
    tipos_adicionales = [t for t in pivot_data.index if t not in orden_especifico]
    orden_final = orden_relevante + tipos_adicionales

    # Reindexar los datos con el orden final
    if orden_final:
        pivot_data = pivot_data.reindex(orden_final)

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
        # Obtener valores únicos de momentos para asegurar solo enteros
        momentos_unicos = sorted(freq_por_momento['Número de momento'].unique())
        fig_bar_momentos.update_layout(
            showlegend=False, 
            height=400,
            xaxis=dict(
                tickmode='array',
                tickvals=momentos_unicos,
                ticktext=[str(int(x)) for x in momentos_unicos],
                title="Número de Momento"
            ),
            yaxis=dict(
                title="Porcentaje (%)",
                range=[0, 100]
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
            labels={'Total_Observaciones': 'Cantidad de Conductas', 'tipo': 'Conducta'},
            color='Total_Observaciones',
            color_continuous_scale=COLOR_PALETTE['green_scale'],
            orientation='h',
            text='Total_Observaciones'
        )
        fig_bar_tipos.update_traces(texttemplate='%{text}', textposition='outside')
        fig_bar_tipos.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_bar_tipos, use_container_width=True, config=chart_config)
    
    st.subheader("Participación por rol en los comportamientos observados")

    roles_objetivo = sorted(df_filtered['participante'].dropna().unique().tolist())
    df_roles = df_filtered[
        df_filtered['participante'].isin(roles_objetivo)
    ].drop_duplicates(
        subset=['idEncuentro', 'tipo', 'Número de momento', 'Encuentro', 'participante']
    ).copy()

    if df_roles.empty:
        st.warning("No hay datos suficientes para comparar la participación por rol.")
    else:
        etiquetas_rol = {
            'Pares expertos': 'Par experto',
            'Docentes acompañados': 'Docente acompañado'
        }
        participacion_rol = (
            df_roles.groupby(['participante', 'tipo'])
            .size()
            .reset_index(name='Conductas_observadas')
        )
        totales_conducta = (
            participacion_rol.groupby('tipo')['Conductas_observadas']
            .sum()
            .reset_index(name='Total_conducta')
        )
        combinaciones_rol = pd.MultiIndex.from_product(
            [roles_objetivo, conductas_esperadas],
            names=['participante', 'tipo']
        ).to_frame(index=False)
        participacion_rol = combinaciones_rol.merge(
            participacion_rol,
            on=['participante', 'tipo'],
            how='left'
        )
        participacion_rol['Conductas_observadas'] = participacion_rol['Conductas_observadas'].fillna(0)
        participacion_rol = participacion_rol.merge(
            totales_conducta,
            on=['tipo'],
            how='left'
        )
        participacion_rol['Total_conducta'] = participacion_rol['Total_conducta'].fillna(0)
        participacion_rol['Porcentaje_conducta'] = (
            participacion_rol['Conductas_observadas']
            .div(participacion_rol['Total_conducta'])
            .fillna(0) * 100
        ).round(0).astype(int)
        participacion_rol['Etiqueta_porcentaje'] = participacion_rol['Porcentaje_conducta'].apply(
            lambda valor: f"{valor}%" if valor > 0 else ""
        )
        participacion_rol['Rol'] = participacion_rol['participante'].map(etiquetas_rol).fillna(participacion_rol['participante'])
        participacion_rol['Conducta'] = participacion_rol['tipo'].apply(lambda valor: envolver_etiqueta(valor, 16))
        periodo_titulo_roles = 'Per?odo seleccionado'
        if fase_datos is not None:
            periodo_titulo_roles += f' ? Fase {fase_datos}'
        if fase_seleccionada != 'Todos los encuentros':
            periodo_titulo_roles += f' ? {fase_seleccionada}'
        titulo_roles = (
            f"Participación por rol - Conductas del cómo ({periodo_titulo_roles})"
            if tipo_filtro == "Conductas asociadas al como"
            else f"Participación por rol - Conductas del qué ({periodo_titulo_roles})"
        )

        fig_roles = px.bar(
            participacion_rol,
            x='Conducta',
            y='Porcentaje_conducta',
            color='Rol',
            barmode='group',
            title=titulo_roles,
            labels={
                'Conducta': '',
                'Porcentaje_conducta': '% dentro de cada conducta',
                'Rol': ''
            },
            category_orders={
                'Conducta': [envolver_etiqueta(conducta, 16) for conducta in conductas_esperadas],
                'Rol': [etiquetas_rol.get(rol, rol) for rol in roles_objetivo]
            },
            color_discrete_map={
                **{etiquetas_rol.get(rol, rol): COLOR_PALETTE['categorical'][i % len(COLOR_PALETTE['categorical'])]
                   for i, rol in enumerate(roles_objetivo)},
                'Par experto': '#46BAD2',
                'Docente acompañado': '#271D67'
            },
            text='Etiqueta_porcentaje',
            hover_data={
                'Conducta': False,
                'Rol': True,
                'Porcentaje_conducta': ':.0f',
                'Conductas_observadas': True,
                'Total_conducta': True,
                'Etiqueta_porcentaje': False
            }
        )
        fig_roles.update_traces(
            texttemplate='%{text}',
            textposition='outside',
            cliponaxis=False,
            marker_line_width=0
        )
        fig_roles.update_layout(
            height=520,
            yaxis_title="% dentro de cada conducta",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='closest',
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=40, r=30, t=100, b=110),
            bargap=0.22,
            bargroupgap=0.08
        )
        fig_roles.update_xaxes(tickangle=0, showgrid=False, title=None)
        fig_roles.update_yaxes(range=[0, 105], ticksuffix="%", showgrid=True, gridcolor="#EEF2F6", zeroline=False)
        fig_roles.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        st.plotly_chart(fig_roles, use_container_width=True, config=chart_config)
        st.caption("Nota: para cada conducta, los porcentajes por rol se calculan sobre el total de veces que se observó esa conducta durante todo el per?odo seleccionado; el conteo queda disponible al pasar el cursor.")

  
    df_line = df_filtered.drop_duplicates(subset=['idEncuentro', 'tipo', 'Número de momento','Encuentro', 'participante'])

    # Obtener conductas disponibles de los datos filtrados
    conductas_disponibles = sorted(df_line['Conducta'].unique())
    
    # Establecer el índice por defecto para "Transferencia de la experticia"
    indice_por_defecto = 0
    if 'Transferencia de la experticia' in conductas_disponibles:
        indice_por_defecto = conductas_disponibles.index('Transferencia de la experticia')
    
    conducta_seleccionada = st.selectbox(
        "Selecciona la conducta a analizar en detalle:",
        options=conductas_disponibles,
        index=indice_por_defecto,
        help="Escoge la conducta específica que deseas analizar por participante y momento"
    )
    
    df_puntos = df_line[ 
        (df_line['Conducta'].isin([conducta_seleccionada]))
    ].copy()
    
    # Gráfica de líneas: Momento vs Porcentaje de Encuentros 
    st.subheader(f"📈 Análisis de Líneas: {conducta_seleccionada} por Encuentros y Momento")
    
    if not df_puntos.empty and 'idEncuentro' in df_puntos.columns and 'participante' in df_puntos.columns and 'tipo' in df_puntos.columns:
        # Calcular dinámicamente el número máximo de encuentros y momentos basándose en los datos
        max_encuentros = df_puntos['idEncuentro'].nunique()
        momento_min = int(df_puntos['Número de momento'].min())
        momento_max = int(df_puntos['Número de momento'].max())
        momentos_completos = range(momento_min, momento_max + 1)
        
        porcentaje_por_participante = []
        
        # Obtener todos los participantes únicos
        participantes_unicos = df_puntos['participante'].unique()
        tipos_unicos = df_puntos['tipo'].unique()  
        
        for tipo in tipos_unicos:
            for participante in participantes_unicos:
                df_subset = df_puntos[(df_puntos['participante'] == participante) & (df_puntos['tipo'] == tipo)]
                
                # Procesar TODOS los momentos, incluso si no hay datos
                for momento in momentos_completos: 
                    if not df_subset.empty and momento in df_subset['Número de momento'].values:
                        # Hay datos para este momento
                        encuentros_en_momento = df_subset[df_subset['Número de momento'] == momento]['idEncuentro'].nunique()
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
        
        # 🔹 Filtrar participantes sin datos reales
        df_lineas = df_lineas.groupby(['Participante', 'Tipo']).filter(
            lambda g: g['Porcentaje_Encuentros'].sum() > 0
        )

        if not df_lineas.empty:
            # Determinar el número de tipos únicos para configurar las facetas
            tipos_unicos = df_lineas['Tipo'].unique()
            num_tipos = len(tipos_unicos)
            
            # Configurar facet_col_wrap para máximo 3 columnas por fila
            facet_col_wrap = min(3, num_tipos)
            
            # Crear gráfico de líneas con facet_col y facet_col_wrap
            fig_lineas = px.line(
                df_lineas,
                x='Momento',
                y='Porcentaje_Encuentros',
                color='Participante',
                facet_col='Tipo',
                facet_col_wrap=facet_col_wrap,
                title=f"Evolución del Porcentaje de Encuentros con {conducta_seleccionada} por Participante y Tipo",
                labels={
                    'Momento': 'Momento',
                    'Porcentaje_Encuentros': 'Porcentaje de Encuentros (%)',
                    'Participante': 'Tipo de Participante',
                    'Tipo': 'Tipo de Comportamiento'
                },
                color_discrete_sequence=['#46BAD2', '#271D67', '#00A651', '#ff7f00', '#46BAD2', '#00A651'],
                markers=True,
                hover_data=['Encuentros_Activos', 'Total_Observaciones'],
                facet_row_spacing=0.25  # Agregar separación vertical entre filas
            )
            
            # Personalizar el gráfico
            fig_lineas.update_traces(
                line=dict(width=3),
                marker=dict(size=8, line=dict(width=2, color='white'))
            )
            # Obtener valores únicos de momentos para asegurar solo enteros
            momentos_unicos = sorted(df_lineas['Momento'].unique())
            
            # Calcular altura dinámica basada en el número de filas
            num_filas = (num_tipos + 2) // 3  # Redondear hacia arriba
            if num_filas == 1:
                altura_total = 400
            elif num_filas == 2:
                altura_total = 800  # Altura más compacta con facet_row_spacing
            else:
                altura_total = 1200  # Altura más compacta para 3+ filas
            
            fig_lineas.update_layout(
                height=altura_total,
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
                    x=1
                ),
                hovermode='x unified'
            )
            
            # Aplicar configuración de eje X a todos los subplots (facetas)
            fig_lineas.update_xaxes(
                tickmode='array',
                tickvals=momentos_unicos,
                ticktext=[str(int(x)) for x in momentos_unicos],
                title="Momento"
            )
            fig_lineas.for_each_xaxis(lambda axis: axis.update(showticklabels=True))
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
                    
        else:
            st.warning("No se pudieron calcular los porcentajes por participante y momento.")
    else:
        st.warning(f"No hay datos disponibles para '{conducta_seleccionada}' o faltan las columnas necesarias ('Encuentro', 'participante' o 'tipo').")
   
    url_2="https://docs.google.com/spreadsheets/d/e/2PACX-1vSK48GsEKzIzoB0TERqse6L3EeRte_5cgTMn8_nOG8G4M2dry3FxRJks9t3R-fwCQ/pub?output=csv"
    df_2 = load_data(url_2)
    df_2 = filtrar_fase_actual(df_2, fase_datos)

    if df_2.empty:
        st.warning("No hay datos válidos para docentes por sexo.")
        return
    
    # Filtrar por fase seleccionada
    if 'Encuentro' in df_2.columns:
        if fase_seleccionada == "Todos los encuentros":
            # No filtrar, mantener todas las fases
            df_2 = df_2.copy()
        elif fase_seleccionada == "Match ambos años":
            # Filtrar solo los encuentros que están en la tabla de correspondencia
            if 'nodo' in df_2.columns:
                # Filtrar Fase 1 con su lista (la columna Fase contiene números: 1 y 2)
                nodos_match = df_2.groupby('nodo')['Encuentro'].nunique().reset_index()
                nodos_match = nodos_match[nodos_match['Encuentro'] > 3]['nodo'].tolist()
                df_2 = df_2[df_2['nodo'].isin(nodos_match)].copy()
                
            else:
                st.error("No se encontró la columna 'nodo' necesaria para el filtro Match.")
                return
        elif fase_seleccionada == "Match solo 2026":
            # Filtrar solo los encuentros que están en la tabla de correspondencia para 2026
            if 'nodo' in df_2.columns:
                nodos_match_2026 = df_2[df_2['Encuentro'].str.contains('2026_')].groupby('nodo')['Encuentro'].nunique().reset_index()
                nodos_match_2026 = nodos_match_2026[nodos_match_2026['Encuentro'] > 1]['nodo'].tolist()
                df_2 = df_2[df_2['nodo'].isin(nodos_match_2026)].copy()
                df_2 = df_2[df_2['Encuentro'].str.contains('2026_')].copy()
            else:
                st.error("No se encontró la columna 'nodo' necesaria para el filtro Match.")
                return
        else:
            df_2 = df_2[df_2['Encuentro'] == fase_seleccionada].copy()
    else:
        st.warning("La columna 'Encuentro' no está disponible en el segundo conjunto de datos.")
        return
    # Verificar que las columnas necesarias existen
    required_columns = ['Número de momento', 'tipo', 'participante', 'Conducta']
    missing_columns = [col for col in required_columns if col not in df_2.columns]
    
    if missing_columns:
        st.error(f"Columnas faltantes en los datos: {missing_columns}")
        st.info("Las columnas disponibles son: " + ", ".join(df_2.columns.tolist()))
        return
    
    # Limpiar espacios en blanco en la columna Conducta y reemplazar NaN o vacíos
    df_2['Conducta'] = df_2['Conducta'].astype(str).str.strip()
    
    # Reemplazar valores NaN, vacíos o 'nan' con "Comunicación en espacios de aprendizaje"
    df_2['Conducta'] = df_2['Conducta'].replace(['nan', '', 'NaN', 'None'], 'Comunicación en espacios de aprendizaje')
    df_2.loc[df_2['Conducta'].isna(), 'Conducta'] = 'Comunicación en espacios de aprendizaje'
    df_2 = normalizar_tipo_conducta(df_2)
    
     # Aplicar el mismo filtro de conductas que se seleccionó anteriormente
    Conductas_permitidas = GRUPOS_CONDUCTAS_QUE
    conductas_como_permitidas_genero = conductas_como_aplicables(df_2)
    
    df_filtered_genero = filtrar_conductas_actuales(df_2, tipo_filtro)
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
            ).round(1)
            
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
            ).round(1)
            
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

    # Reuse available answers; adding a separate source requires a later data update.
    df_base_interaccion = df_2

    orden_escucha_interaccion = ['Nunca', 'Pocas veces', 'Algunas veces', 'Frecuentemente', 'Siempre']
    orden_turnos_interaccion = [
        'Fluido y equilibrado entre varios participantes.',
        'Mayormente fluido, con participación desigual.',
        'Poco fluido, predominaron algunos participantes.',
        'Interrumpido o desordenado.',
        'No se observó intercambio de turnos y/o conversación en este momento.'
    ]
    graficas_interaccion = [
        {
            'patrones': ['escucha activa'],
            'orden': orden_escucha_interaccion,
            'titulo': 'Escucha activa y atención entre pares',
            'envolver': False,
        },
        {
            'patrones': ['intercambio', 'turnos'],
            'orden': orden_turnos_interaccion,
            'titulo': 'Intercambio de turnos y conversación',
            'envolver': True,
        },
    ]
    graficas_interaccion = [
        grafica for grafica in graficas_interaccion
        if not preparar_resumen_respuestas(
            df_base_interaccion,
            grafica['patrones'],
            grafica['orden']
        ).empty
    ]

    if graficas_interaccion:
        st.subheader("Caracterización de la interacción durante los momentos")
        contenedores = st.columns(2) if len(graficas_interaccion) > 1 else [st.container()]
        for contenedor, grafica in zip(contenedores, graficas_interaccion):
            with contenedor:
                graficar_distribucion_respuestas(
                    df_base_interaccion,
                    patrones=grafica['patrones'],
                    orden_respuestas=grafica['orden'],
                    titulo=grafica['titulo'],
                    envolver_respuestas=grafica['envolver']
                )
    else:
        st.info("La fuente actual no contiene respuestas de escucha activa ni intercambio de turnos.")

    url_3="https://docs.google.com/spreadsheets/d/e/2PACX-1vRMhpi8RzNOKQYiW6vetPerkCkRZkmtsUwLB8ZEe0DRpdUusPcr3VNLMohF4r7m2Q/pub?output=csv"
    df_3 = load_data(url_3)
    df_3 = filtrar_fase_actual(df_3, fase_datos)
    
    if not df_3.empty:
        # Filtrar por fase seleccionada
        if 'Encuentro' in df_3.columns:
            if fase_seleccionada == "Todos los encuentros":
                # No filtrar, mantener todas las fases
                df_3 = df_3.copy()
            elif fase_seleccionada == "Match ambos años":
                # Filtrar solo los encuentros que están en la tabla de correspondencia
                if 'nodo' in df_3.columns:
                    # Filtrar Fase 1 con su lista (la columna Fase contiene números: 1 y 2)
                    nodos_match = df_3.groupby('nodo')['Encuentro'].nunique().reset_index()
                    nodos_match = nodos_match[nodos_match['Encuentro'] > 3]['nodo'].tolist()
                    df_3 = df_3[df_3['nodo'].isin(nodos_match)].copy()
                else:
                    st.error("No se encontró la columna 'Encuentro' necesaria para el filtro Match.")
                    return
            elif fase_seleccionada == "Match solo 2026":
                # Filtrar solo los encuentros que están en la tabla de correspondencia para 2026
                if 'nodo' in df_3.columns:
                    nodos_match_2026 = df_3[df_3['Encuentro'].str.contains('2026_')].groupby('nodo')['Encuentro'].nunique().reset_index()
                    nodos_match_2026 = nodos_match_2026[nodos_match_2026['Encuentro'] > 1]['nodo'].tolist()
                    df_3 = df_3[df_3['nodo'].isin(nodos_match_2026)].copy()
                    df_3 = df_3[df_3['Encuentro'].str.contains('2026_')].copy()
                else:
                    st.error("No se encontró la columna 'nodo' necesaria para el filtro Match.")
                    return
            else:
                df_3 = df_3[df_3['Encuentro'] == fase_seleccionada].copy()
        else:
            st.warning("La columna 'Encuentro' no está disponible en el tercer conjunto de datos.")
            return
        
        st.subheader("📊 Análisis de Fortalezas por Encuentro")
        
        # Verificar que las columnas necesarias existen
        required_columns_3 = ['idEncuentro', 'pregunta', 'respuesta']
        missing_columns_3 = [col for col in required_columns_3 if col not in df_3.columns]
        
        if missing_columns_3:
            st.error(f"Columnas faltantes en los datos: {missing_columns_3}")
            st.info("Las columnas disponibles son: " + ", ".join(df_3.columns.tolist()))
        else:
            # Limpiar datos: eliminar filas con Encuentro vacío
            df_3_clean = df_3[df_3['idEncuentro'].notna() & (df_3['idEncuentro'] != '')].copy()
            
            # Filtrar solo las filas donde 'pregunta' contenga 'Fortaleza'
            df_3_clean = df_3_clean[df_3_clean['pregunta'].str.contains('Fortaleza', case=False, na=False)].copy()
            
            if df_3_clean.empty:
                st.warning("No hay datos válidos después de filtrar por 'Fortaleza'.")
                return
            
            # Extraer número del encuentro para ordenar correctamente
            df_3_clean['Encuentro_Num'] = df_3_clean['idEncuentro'].str.extract(r'(\d+)').astype(int)
            
            # Crear identificador único considerando Encuentro + Fase para evitar duplicados entre fases
            if 'Encuentro' in df_3_clean.columns:
                df_3_clean['Encuentro_Fase_Unico'] = df_3_clean['idEncuentro'].astype(str) + '_' + df_3_clean['Encuentro'].astype(str)
                # Contar encuentros únicos por respuesta considerando fase
                conteo_por_pregunta = df_3_clean.groupby('respuesta')['Encuentro_Fase_Unico'].nunique().reset_index()
            else:
                # Fallback si no hay columna Fase
                conteo_por_pregunta = df_3_clean.groupby('respuesta')['idEncuentro'].nunique().reset_index()
            
            conteo_por_pregunta.columns = ['Respuesta', 'Numero_de_encuentros']
            # Función para tomar solo las primeras palabras
            def primeras_palabras(texto, num_palabras=3):
                palabras = texto.split()
                if len(palabras) > num_palabras:
                    return " ".join(palabras[:num_palabras]) + "..."
                return texto
            
            # Aplicar función a las respuestas
            conteo_por_pregunta['Respuesta_Corta'] = conteo_por_pregunta['Respuesta'].apply(lambda x: primeras_palabras(x, 15))
            
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
        required_columns_3 = ['idEncuentro', 'pregunta', 'respuesta']
        missing_columns_3 = [col for col in required_columns_3 if col not in df_3.columns]
        
        if missing_columns_3:
            st.error(f"Columnas faltantes en los datos: {missing_columns_3}")
            st.info("Las columnas disponibles son: " + ", ".join(df_3.columns.tolist()))
        else:
            # Limpiar datos: eliminar filas con Encuentro vacío
            df_3_clean = df_3[df_3['idEncuentro'].notna() & (df_3['idEncuentro'] != '')].copy()
            
            # Filtrar solo las filas donde 'pregunta' contenga 'Condicion '
            df_3_clean = df_3_clean[df_3_clean['pregunta'].str.contains('Condicion', case=False, na=False)].copy()
            
            if df_3_clean.empty:
                st.warning("No hay datos válidos después de filtrar por 'Condicion '.")
                return
            
            # Extraer número del encuentro para ordenar correctamente
            df_3_clean['Encuentro_Num'] = df_3_clean['idEncuentro'].str.extract(r'(\d+)').astype(int)
            
            # Crear identificador único considerando Encuentro + Fase para evitar duplicados entre fases
            if 'Encuentro' in df_3_clean.columns:
                df_3_clean['Encuentro_Fase_Unico'] = df_3_clean['idEncuentro'].astype(str) + '_' + df_3_clean['Encuentro'].astype(str)
                # Contar encuentros únicos por respuesta considerando fase
                conteo_por_pregunta = df_3_clean.groupby('respuesta')['Encuentro_Fase_Unico'].nunique().reset_index()
            else:
                # Fallback si no hay columna Fase
                conteo_por_pregunta = df_3_clean.groupby('respuesta')['idEncuentro'].nunique().reset_index()
            
            conteo_por_pregunta.columns = ['Respuesta', 'Numero_de_encuentros']
            
            # Función para tomar solo las primeras palabras
            def primeras_palabras(texto, num_palabras=3):
                palabras = texto.split()
                if len(palabras) > num_palabras:
                    return " ".join(palabras[:num_palabras]) + "..."
                return texto
            
            # Aplicar función a las respuestas
            conteo_por_pregunta['Respuesta_Corta'] = conteo_por_pregunta['Respuesta'].apply(lambda x: primeras_palabras(x, 15))
            
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
        required_columns_3 = ['idEncuentro', 'pregunta', 'respuesta']
        missing_columns_3 = [col for col in required_columns_3 if col not in df_3.columns]
        
        if missing_columns_3:
            st.error(f"Columnas faltantes en los datos: {missing_columns_3}")
            st.info("Las columnas disponibles son: " + ", ".join(df_3.columns.tolist()))
        else:
            # Limpiar datos: eliminar filas con Encuentro vacío
            df_3_clean = df_3[df_3['idEncuentro'].notna() & (df_3['idEncuentro'] != '')].copy()
            
            # Filtrar solo las filas donde 'pregunta' contenga 'Debilidad'
            df_3_clean = df_3_clean[df_3_clean['pregunta'].str.contains('Debilidad', case=False, na=False)].copy()
            
            if df_3_clean.empty:
                st.warning("No hay datos válidos después de filtrar por 'debilidad'.")
                return
            
            # Extraer número del encuentro para ordenar correctamente
            df_3_clean['Encuentro_Num'] = df_3_clean['idEncuentro'].str.extract(r'(\d+)').astype(int)
            
            # Crear identificador único considerando Encuentro + Fase para evitar duplicados entre fases
            if 'Fase' in df_3_clean.columns:
                df_3_clean['Encuentro_Fase_Unico'] = df_3_clean['idEncuentro'].astype(str) + '_' + df_3_clean['Encuentro'].astype(str)
                # Contar encuentros únicos por respuesta considerando fase
                conteo_por_pregunta = df_3_clean.groupby('respuesta')['Encuentro_Fase_Unico'].nunique().reset_index()
            else:
                # Fallback si no hay columna Fase
                conteo_por_pregunta = df_3_clean.groupby('respuesta')['idEncuentro'].nunique().reset_index()
            
            conteo_por_pregunta.columns = ['Respuesta', 'Numero_de_encuentros']
            
            # Función para tomar solo las primeras palabras
            def primeras_palabras(texto, num_palabras=3):
                palabras = texto.split()
                if len(palabras) > num_palabras:
                    return " ".join(palabras[:num_palabras]) + "..."
                return texto
            
            # Aplicar función a las respuestas
            conteo_por_pregunta['Respuesta_Corta'] = conteo_por_pregunta['Respuesta'].apply(lambda x: primeras_palabras(x, 15))
            
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
                yaxis_title="Debilidad",
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
    url_instantaneas = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQVjpXfTYh6SWRLYmbo1oD9cmEKCMR9uL0jAoNd2x4zt7s45UUDEMQeL5I3OnBpuYOwWBs7ooMf9tHL/pub?output=csv"
    
    # Cargar datos
    df_inst = load_data(url_instantaneas)
    df_inst, _ = seleccionar_fase_actual(df_inst, 'fase_instantaneas_2026')
    # Renombrar columnas según el diccionario proporcionado
    rename_dict = {
        'Fecha de inicio': 'fechaInicio',
        'Fecha de finalización': 'fechaFin',
        'Tipo de respuesta': 'tipoRespuesta',
        'Dirección IP': 'ip',
        'Progreso': 'progreso',
        'Finalizado': 'finalizado',
        'Fecha registrada': 'fechaRegistro',
        'Encuentro': 'Encuentro',
        'ID de respuesta': 'idRespuesta',
        'Antes de finalizar el registro de instantáneas, por favor confirma algunos datos: - Nombre del/la observador(a)': 'nombreObservador',
        'Antes de finalizar el registro de instantáneas, por favor confirma algunos datos: - Correo electrónico': 'correoObservador',
        'IDEncuentro': 'idEncuentro',
        'accion momento': 'accionMomento',
        'accion momento - otra': 'accionMomentoOtra',
        '¿Quiénes participan activamente en la conversación o actividad en este momento? Puede seleccionar más de un actor. Si no está ocurriendo una conversación o actividad en este momento, selecciona No aplica - Pares expertos': 'participaPares',
        '¿Quiénes participan activamente en la conversación o actividad en este momento? Puede seleccionar más de un actor. Si no está ocurriendo una conversación o actividad en este momento, selecciona No aplica - Docentes acompañados': 'participaDocentes',
        '¿Quiénes participan activamente en la conversación o actividad en este momento? Puede seleccionar más de un actor. Si no está ocurriendo una conversación o actividad en este momento, selecciona No aplica - Mentores': 'participaMentores',
        '¿Quiénes participan activamente en la conversación o actividad en este momento? Puede seleccionar más de un actor. Si no está ocurriendo una conversación o actividad en este momento, selecciona No aplica - No aplica': 'participaNA',
        '¿Quiénes participan activamente en la conversación o actividad en este momento? Si no está ocurriendo una conversación o actividad en este momento, selecciona "No aplica" - antiguo': 'participantesAntiguo',
        '¿Quiénes participan activamente en la conversación o actividad en este momento? Si no está ocurriendo una conversación o actividad en este momento, selecciona "No aplica" -': 'participantes',
        'Quien dirige': 'quienDirige',
        'Registre cualquier comentario para comprender lo sucedido en esta instantánea': 'comentario',
        'Número de instantánea': 'numInstantanea'
    }
    
    # Aplicar el renombramiento solo a las columnas que existen
    df_inst = df_inst.rename(columns={k: v for k, v in rename_dict.items() if k in df_inst.columns})
    
    # Crear columna 'participantes' fusionando las dos columnas posibles
    if 'participantes' not in df_inst.columns and 'participantesAntiguo' in df_inst.columns:
        df_inst['participantes'] = df_inst['participantesAntiguo']
    elif 'participantes' in df_inst.columns and 'participantesAntiguo' in df_inst.columns:
        # Si ambas existen, usar la que tenga datos, priorizando la nueva
        df_inst['participantes'] = df_inst['participantes'].fillna(df_inst['participantesAntiguo'])
    
    if df_inst.empty:
        st.warning("No hay datos disponibles para las métricas instantáneas.")
        return
    # Selector de instantánea al inicio
    st.subheader("🔍 Selección de Fase")

    # Obtener fases disponibles
    if 'Encuentro' in df_inst.columns:
        fases_disponibles = sorted(df_inst['Encuentro'].dropna().unique())
        # Agregar opción "Todas las fases"
        opciones_fase = opciones_encuentros(df_inst)
        
        fase_seleccionada = st.selectbox(
            "Selecciona el encuentro a analizar:",
            options=opciones_fase,
            help="Escoge el encuentro específico que deseas analizar en todos los gráficos, o selecciona 'Todos los encuentros' para incluir todos"
        )
        
        st.markdown("---")
        st.info(f"📋 **Análisis para: {fase_seleccionada}**")
    else:
        st.warning("No se encontró la columna 'Fase' en los datos o los datos están vacíos.")
        return
    # Filtrar filas donde 'Nombre del/la observador(a)' no esté vacío
    if 'Nombre del/la observador(a)' in df_inst.columns:
        df_inst = df_inst[
            (df_inst['Nombre del/la observador(a)'].notna()) & 
            (df_inst['Nombre del/la observador(a)'].astype(str).str.strip() != '')
        ].copy()

    df_inst = normalizar_acciones_instantaneas(df_inst)
    df_inst_acciones = df_inst[
        df_inst['accionMomento'].notna()
    ].copy() if 'accionMomento' in df_inst.columns else pd.DataFrame()

    columnas_dedup_inst = [
        col for col in ['idEncuentro', 'numInstantanea', 'Encuentro', 'Fase']
        if col in df_inst.columns
    ]
    if columnas_dedup_inst:
        df_inst = df_inst.drop_duplicates(subset=columnas_dedup_inst)

    # Filtrar datos por fase seleccionada
    if fase_seleccionada == "Todos los encuentros":
        # No filtrar, mantener todas las fases
        df_inst_filtered = df_inst.copy()
    elif fase_seleccionada == "Match ambos años":
        if 'nodo' in df_inst.columns:
            nodos_match = df_inst.groupby('nodo')['Encuentro'].nunique().reset_index()
            nodos_match = nodos_match[nodos_match['Encuentro'] > 3]['nodo'].tolist()
            df_inst_filtered = df_inst[df_inst['nodo'].isin(nodos_match)].copy()
            
            st.info(f"🔗 **Analizando {len(df_inst_filtered['idEncuentro'].unique())} encuentros emparejados**")
        else:
            st.error("No se encontró la columna 'Encuentro' necesaria para el filtro Match.")
            return
    elif fase_seleccionada in ["Match solo 2026", "Match 2026"]:
        if 'nodo' in df_inst.columns:
            nodos_match_2026 = df_inst[df_inst['Encuentro'].str.contains('2026_')].groupby('nodo')['Encuentro'].nunique().reset_index()
            nodos_match_2026 = nodos_match_2026[nodos_match_2026['Encuentro'] > 1]['nodo'].tolist()
            df_inst_filtered = df_inst[df_inst['nodo'].isin(nodos_match_2026)].copy()
            df_inst_filtered = df_inst_filtered[df_inst_filtered['Encuentro'].str.contains('2026_')].copy()
            
            st.info(f"🔗 **Analizando {len(df_inst_filtered['idEncuentro'].unique())} encuentros emparejados para 2026**")
        else:
            st.error("No se encontró la columna 'Encuentro' necesaria para el filtro Match.")
            return
    else:
        # Filtrar por la fase específica seleccionada
        df_inst_filtered = df_inst[df_inst['Encuentro'] == fase_seleccionada].copy()

    if df_inst_filtered.empty:
        st.warning("No hay datos válidos para el análisis de instantáneas.")
        return

    if not df_inst_acciones.empty and columnas_dedup_inst:
        llaves_seleccionadas = df_inst_filtered[columnas_dedup_inst].drop_duplicates()
        df_inst_acciones_filtered = df_inst_acciones.merge(
            llaves_seleccionadas,
            on=columnas_dedup_inst,
            how='inner'
        )
    else:
        df_inst_acciones_filtered = pd.DataFrame()

    with st.expander("Ver equivalencia de nombres completos y nombres cortos"):
        st.dataframe(
            pd.DataFrame({
                'Nombre completo en la base': ACCIONES_INSTANTANEAS_2026,
                'Nombre corto en las gráficas': [
                    etiqueta_accion_instantanea(accion) for accion in ACCIONES_INSTANTANEAS_2026
                ],
            }),
            use_container_width=True,
            hide_index=True
        )

    # Mapa de calor: accionMomento vs numInstantanea
    st.subheader("📊 Mapa de Calor - Acción Momento vs Instantáneas")
    
    if 'accionMomento' in df_inst_acciones_filtered.columns and 'numInstantanea' in df_inst_acciones_filtered.columns:
        df_inst_heatmap = df_inst_acciones_filtered.copy()

        # Crear tabla de frecuencias para el mapa de calor
        heatmap_data = df_inst_heatmap.groupby(['accionMomento', 'numInstantanea']).size().reset_index(name='Frecuencia')
        
        # Crear tabla pivote para el mapa de calor
        pivot_data = heatmap_data.pivot(index='accionMomento', columns='numInstantanea', values='Frecuencia').fillna(0)
        orden_acciones = [accion for accion in ACCIONES_INSTANTANEAS_2026 if accion in pivot_data.index]
        orden_acciones += [accion for accion in pivot_data.index if accion not in orden_acciones]
        pivot_data = pivot_data.reindex(orden_acciones)
        
        if not pivot_data.empty:
            # Generar mapa de calor
            fig_heatmap = px.imshow(
                pivot_data.values,
                x=pivot_data.columns,
                y=[etiqueta_accion_instantanea(accion) for accion in pivot_data.index],
                color_continuous_scale=COLOR_PALETTE['blue_scale'],
                title="Frecuencia de Acciones por Instantánea",
                labels=dict(x="Número de Instantánea", y="Acción Momento", color="Frecuencia"),
                aspect="auto"
            )
            
            # Personalizar el diseño
            fig_heatmap.update_layout(
                height=max(560, 34 * len(pivot_data.index) + 180),
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
                    tickfont=dict(size=12),
                    automargin=True
                ),
                margin=dict(l=230, r=40, t=80, b=55),
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
    else:
        st.warning("No hay acciones válidas del catálogo actualizado para generar el mapa de calor.")
    
    # Análisis general de instantáneas
    col1, col2 = st.columns(2)
    
    with col1:
        if 'accionMomento' in df_inst_acciones_filtered.columns:
            # Gráfico de frecuencia por acción momento
            freq_por_accion = df_inst_acciones_filtered.groupby('accionMomento').size().reset_index(name='Frecuencia')
            freq_por_accion = freq_por_accion.sort_values('Frecuencia', ascending=True)
            freq_por_accion['accionMomento_plot'] = freq_por_accion['accionMomento'].apply(etiqueta_accion_instantanea)
            
            fig_acciones = px.bar(
                freq_por_accion,
                x='Frecuencia',
                y='accionMomento_plot',
                title="Frecuencia por Acción Momento",
                labels={'Frecuencia': 'Frecuencia', 'accionMomento_plot': 'Acción Momento'},
                color='Frecuencia',
                color_continuous_scale=COLOR_PALETTE['blue_scale'],
                text='Frecuencia',
                hover_data={'accionMomento': True, 'accionMomento_plot': False}
            )
            fig_acciones.update_traces(texttemplate='%{text}', textposition='outside')
            fig_acciones.update_layout(
                showlegend=False,
                height=max(440, 28 * len(freq_por_accion) + 160),
                yaxis=dict(tickfont=dict(size=12), automargin=True),
                margin=dict(l=230, r=60, t=80, b=50)
            )
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
            fig_instantaneas.update_layout(
                showlegend=False, 
                height=400,
                yaxis=dict(
                    range=[0, 130]
                )
            )
            st.plotly_chart(fig_instantaneas, use_container_width=True, config=chart_config)

    # Mapa de burbujas por momento oculto temporalmente.

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
            # Filtrar solo registros que tengan un número de encuentro válido
            df_participacion = df_participacion[df_participacion['idEncuentro'].notna()].copy()
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
                        'Cantidad_Observaciones': 'Observaciones de instantáneas',
                        'participantes': 'Tipo de Participación por Género'
                    },
                    color_discrete_sequence=['#46BAD2', '#271D67', '#00A651', '#ff7f00', '#8E44AD'],
                    text='Cantidad_Observaciones'
                )
            
                # Personalizar el gráfico
                fig_participacion_apilada.update_traces(
                    texttemplate='%{text}',
                    textposition='inside',
                    textfont=dict(size=12, color='#111111'),
                    insidetextfont=dict(color='#111111')
                )
                for traza in fig_participacion_apilada.data:
                    color_texto = 'white' if traza.marker.color in ['#271D67', '#8E44AD'] else '#111111'
                    traza.update(textfont=dict(color=color_texto), insidetextfont=dict(color=color_texto))

                
                # Obtener valores únicos de instantáneas para asegurar solo enteros
                instantaneas_unicas = sorted(participacion_por_instantanea['numInstantanea'].unique())
                
                fig_participacion_apilada.update_layout(
                    height=650,
                    xaxis_title="Instantáneas",
                    yaxis_title="Observaciones de instantáneas",
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
                        tickmode='array',
                        tickvals=instantaneas_unicas,
                        ticktext=[str(int(x)) for x in instantaneas_unicas]
                    ),
                    yaxis=dict(rangemode='tozero', dtick=1),
                    barmode='stack'  # Apilar las barras
                )
                
                for traza in fig_participacion_apilada.data:
                    valores_x = [float(valor) for valor in traza.x]
                    valores_y = [int(valor) for valor in traza.y]
                    traza.x = None
                    traza.y = None
                    traza.x = valores_x
                    traza.y = valores_y
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
                    
                    total_observaciones = int(total_por_tipo.sum())
                    insights_participacion = [
                        f"**Observaciones registradas:** {total_observaciones}. "
                        "Las respuestas describen la participación observada; no son conteos de personas."
                    ]
                    for categoria, cantidad in total_por_tipo.items():
                        porcentaje = cantidad / total_observaciones * 100
                        insights_participacion.append(
                            f"- **{categoria}:** {int(cantidad)} observaciones ({porcentaje:.1f}%)."
                        )

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
                etiquetas_direccion = {
                    'Sí, un(a) par experto(a)': 'Coding Hubs Masters',
                    'Sí, un(a) docente acompañado(a)': 'Docentes Acompañados',
                    'Sí, un mentor(a)': 'Mentores',
                    'No, la interacción se da entre varios/as docentes de manera balanceada': 'Dirección compartida entre docentes',
                    'No ocurre interacción': 'No Aplica',
                }
                df_quien_dirige['quienDirige'] = df_quien_dirige['quienDirige'].astype(str).str.strip()
                df_quien_dirige = df_quien_dirige[df_quien_dirige['quienDirige'] != ''].copy()
                df_quien_dirige['quienDirige'] = df_quien_dirige['quienDirige'].replace(etiquetas_direccion)
                # Crear conteo agrupado por instantánea y tipo de quienDirige (sin separar por encuentro)
                direccion_por_instantanea = df_quien_dirige.groupby(['numInstantanea', 'quienDirige']).size().reset_index(name='Cantidad_Observaciones')

                # Crear el gráfico de barras apiladas vertical
                fig_direccion_apilada = px.bar(
                    direccion_por_instantanea,
                    x='numInstantanea',
                    y='Cantidad_Observaciones',
                    color='quienDirige',
                    title="Dirección de Encuentros por Instantánea",
                    labels={
                        'numInstantanea': 'Instantáneas',
                        'Cantidad_Observaciones': 'Observaciones de instantáneas',
                        'quienDirige': 'Quién dirige la participación'
                    },
                    color_discrete_map={
                        'Coding Hubs Masters': '#46BAD2',
                        'Docentes Acompañados': '#00A651',
                        'Mentores': '#ff7f00',
                        'Dirección compartida entre docentes': '#8E44AD',
                        'No Aplica': '#271D67',
                    },
                    category_orders={'quienDirige': list(etiquetas_direccion.values())},
                    text='Cantidad_Observaciones'
                )
            
                # Personalizar el gráfico
                fig_direccion_apilada.update_traces(
                    texttemplate='%{text}',
                    textposition='inside',
                    textfont=dict(size=12, color='#111111'),
                    insidetextfont=dict(color='#111111')
                )
                for traza in fig_direccion_apilada.data:
                    color_texto = 'white' if traza.marker.color in ['#271D67', '#8E44AD'] else '#111111'
                    traza.update(textfont=dict(color=color_texto), insidetextfont=dict(color=color_texto))


                # Obtener valores únicos de instantáneas para asegurar solo enteros
                instantaneas_unicas = sorted(direccion_por_instantanea['numInstantanea'].unique())

                fig_direccion_apilada.update_layout(
                    height=650,
                    xaxis_title="Instantáneas",
                    yaxis_title="Observaciones de instantáneas",
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
                        tickmode='array',
                        tickvals=instantaneas_unicas,
                        ticktext=[str(int(x)) for x in instantaneas_unicas]
                    ),
                    yaxis=dict(rangemode='tozero', dtick=1),
                    barmode='stack'  # Apilar las barras
                )

                for traza in fig_direccion_apilada.data:
                    valores_x = [float(valor) for valor in traza.x]
                    valores_y = [int(valor) for valor in traza.y]
                    traza.x = None
                    traza.y = None
                    traza.x = valores_x
                    traza.y = valores_y
                st.plotly_chart(fig_direccion_apilada, use_container_width=True, config=chart_config)
                
                # Generar insights automáticos para dirección de encuentros
                st.subheader("🔍  Dirección de Encuentros")
                
                # Calcular estadísticas para insights
                total_por_director = direccion_por_instantanea.groupby('quienDirige')['Cantidad_Observaciones'].sum().sort_values(ascending=False)
                
                if len(total_por_director) > 0:
                    total_observaciones = int(total_por_director.sum())
                    insights_direccion = [
                        f"**Observaciones registradas:** {total_observaciones}. "
                        "Los porcentajes corresponden a las instantáneas con respuesta de dirección, "
                        "incluidas aquellas sin interacción."
                    ]
                    for categoria, cantidad in total_por_director.items():
                        porcentaje = cantidad / total_observaciones * 100
                        insights_direccion.append(
                            f"- **{categoria}:** {int(cantidad)} observaciones ({porcentaje:.1f}%)."
                        )

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
            # Contar cuántos datos hay por cada tipo de participación en cada instantánea
            # Las columnas son binarias: 1 indica presencia y 0 indica ausencia.
            participacion_contada = df_participacion_binaria[columnas_participacion + ['numInstantanea']].copy()
            for col in columnas_participacion:
                participacion_contada[col] = pd.to_numeric(participacion_contada[col], errors='coerce').eq(1).astype(int)
            # Agrupar por instantánea y sumar los 1s para cada tipo
            participacion_agrupada = participacion_contada.groupby('numInstantanea')[columnas_participacion].sum().reset_index()

            # Crear el DataFrame en formato largo para Plotly
            participacion_melted = participacion_agrupada.melt(
                id_vars=['numInstantanea'],
                value_vars=columnas_participacion,
                var_name='Tipo_Participacion',
                value_name='Cantidad'
            )
            # Renombrar los tipos de participación para mejor presentación
            nombres_participacion = {
                'participaPares': 'Coding Hubs Masters',
                'participaDocentes': 'Docentes Acompañados',
                'participaMentores': 'Mentores',
                'participaNA': 'No Aplica'
            }
            participacion_melted['Tipo_Participacion'] = participacion_melted['Tipo_Participacion'].map(nombres_participacion)

            # Crear el gráfico de líneas
            fig_participacion_lineas = px.line(
                participacion_melted,
                x='numInstantanea',
                y='Cantidad',
                color='Tipo_Participacion',
                title="Evolución de Participación por Instantáneas",
                labels={
                    'numInstantanea': 'Instantáneas',
                    'Cantidad': 'Cantidad de Observaciones',
                    'Tipo_Participacion': 'Tipo de Participación'
                },
                color_discrete_map={
                    'Coding Hubs Masters': '#46BAD2',
                    'Docentes Acompañados': '#00A651',
                    'Mentores': '#ff7f00',
                    'No Aplica': '#271D67',
                },
                markers=True
            )
            
            # Personalizar el gráfico
            fig_participacion_lineas.update_traces(
                line=dict(width=3),
                marker=dict(size=8, line=dict(width=2, color='white'))
            )

            fig_participacion_lineas.update_layout(
                height=600,
                xaxis_title="Instantáneas",
                yaxis_title="Cantidad de Observaciones",
                legend=dict(
                    title="Tipo de Participante",
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5
                ),
                font=dict(size=12),
                xaxis=dict(
                    tickmode='array',
                    tickvals=sorted(participacion_melted['numInstantanea'].unique()),
                    ticktext=[str(int(x)) for x in sorted(participacion_melted['numInstantanea'].unique())]
                ),
                hovermode='x unified'
            )

            for traza in fig_participacion_lineas.data:
                valores_x = [float(valor) for valor in traza.x]
                valores_y = [int(valor) for valor in traza.y]
                traza.x = None
                traza.y = None
                traza.x = valores_x
                traza.y = valores_y
            st.plotly_chart(fig_participacion_lineas, use_container_width=True, config=chart_config)
            # Generar insights automáticos para participación por participantes
            st.subheader("🔍  Participación por Participantes")
            
            # Calcular estadísticas para insights
            total_por_participante = participacion_melted.groupby('Tipo_Participacion')['Cantidad'].sum().sort_values(ascending=False)

            if len(total_por_participante) > 0:
                insights_participantes = []

                # Identificar participantes más y menos activos
                participante_mas_activo = total_por_participante.index[0]
                valor_mas_activo = total_por_participante.iloc[0]

                participante_menos_activo = total_por_participante.index[-1]
                valor_menos_activo = total_por_participante.iloc[-1]

                # Análisis de participación activa
                tipos_muy_activos = total_por_participante[total_por_participante >= total_por_participante.mean()].index.tolist()

                if len(tipos_muy_activos) >= 2:
                    tipos_activos_str = " y ".join(tipos_muy_activos[:2]) if len(tipos_muy_activos) == 2 else ", ".join(tipos_muy_activos[:-1]) + " y " + tipos_muy_activos[-1]
                    insights_participantes.append(f"💪 **Participación colaborativa**: En los momentos de conversación o desarrollo de actividades, tanto **{tipos_activos_str}** participaban activamente.")
                else:
                    insights_participantes.append(f"💪 **Participación dominante**: **{participante_mas_activo}** lidera claramente la participación activa en las instantáneas.")

                # Análisis de participación mínima
                if valor_menos_activo < total_por_participante.mean() * 0.5:
                    insights_participantes.append(f"⚠️ **Participación limitada**: La participación de **{participante_menos_activo}** fue mínima, con solo {valor_menos_activo} observaciones en total.")

                # Análisis de distribución
                coeficiente_variacion = total_por_participante.std() / total_por_participante.mean()
                if coeficiente_variacion > 0.5:
                    insights_participantes.append("📊 **Distribución desigual**: Existe una marcada diferencia en los niveles de participación entre los diferentes tipos de participantes.")
                else:
                    insights_participantes.append("📊 **Distribución equilibrada**: Los diferentes tipos de participantes muestran niveles similares de participación.")

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

                    insights_participantes.append(f"🌟 **Instantánea destacada**: La instantánea {instantanea_mas_activa} registra la mayor actividad colaborativa total.")
                    insights_participantes.append(f"🔄 **Consistencia**: **{tipo_mas_consistente}** mantiene presencia en {instantaneas_presentes} de {total_instantaneas} instantáneas analizadas.")

                # Mostrar insights
                for insight in insights_participantes:
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
    
    # Mostrar dashboards especializados en colaboración
    momentos()
    # ==========================================
    # GRAFICADOR PERSONALIZADO EN MOMENTOS
    # ==========================================
    st.markdown("---")

with tab3:
    st.header("⚡ Instantáneas - Métricas Rápidas")
    st.markdown("""
    Vista rápida de métricas clave y visualizaciones instantáneas sobre redes y 
    comunidades colaborativas.
    """)
    instantaneas()
    # Métricas instantáneas adicionales
    st.markdown("---")


# Pie de página
st.markdown("---")
st.write("© 2026 Colombia Programa - Encuentros Colaborativos 2026 - Ministerio de Tecnologías de la Información y las Comunicaciones (MinTIC)")

# Formatear el HTML con las imágenes convertidas a base64
formatted_footer = FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64)

# Mostrar el footer en Streamlit
st.markdown(formatted_footer, unsafe_allow_html=True)
