import streamlit as st
import pandas as pd
import plotly.graph_objects as go # type: ignore
from constants.marco_constants import CSV_URL, MAPPING, COLORS
def centrar_texto(texto, tipo="h1"):
    """Centrar headers, subheaders y textos en Streamlit."""
    st.markdown(f"<{tipo} style='text-align: center;'>{texto}</{tipo}>", unsafe_allow_html=True)


def cargar_datos():
    """
    Carga los datos desde el archivo CSV publicado en Google Sheets.
    """
    return pd.read_csv(CSV_URL)

def obtener_opciones_codigos(df):
    """
    Genera las opciones de códigos de IE, combinando las opciones iniciales con los valores únicos de los códigos de IE.
    """
    opciones_codigos = ['Promedio', 'Moda', 'Mediana'] + [codigo for codigo in df['Código IE'].unique() if codigo not in ['Promedio', 'Moda', 'Mediana']]
    return opciones_codigos

def obtener_datos_pretest_posttest(datos_codigo):
    """
    Obtiene los datos de Pretest y Posttest de un código de IE.
    """
    if 'Pretest' in datos_codigo['Momento'].values and 'Posttest' in datos_codigo['Momento'].values:
        pretest = datos_codigo[datos_codigo['Momento'] == 'Pretest'].iloc[0, 2:]
        posttest = datos_codigo[datos_codigo['Momento'] == 'Posttest'].iloc[0, 2:]

        pretest_numeric = pretest.map(MAPPING)
        posttest_numeric = posttest.map(MAPPING)
        pretest_numeric = pd.concat([pretest_numeric, pd.Series([pretest_numeric.iloc[0]])], ignore_index=True)
        posttest_numeric = pd.concat([posttest_numeric, pd.Series([posttest_numeric.iloc[0]])], ignore_index=True)
        categorias = list(pretest.index)
        return pretest_numeric, posttest_numeric, categorias
    return None, None, None

def crear_grafico_radar(pretest_numeric, posttest_numeric, categorias, codigo):
    """
    Crea un gráfico de radar comparando los datos de Pretest y Posttest.
    """

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=pretest_numeric.values,
        theta=categorias + [categorias[0]],  # Cerrar el gráfico
        fill='toself',
        name='Pretest',
        line_color=COLORS['pretest']['line'],
        fillcolor=COLORS['pretest']['fill']
    ))

    fig.add_trace(go.Scatterpolar(
        r=posttest_numeric.values,
        theta=categorias + [categorias[0]],  # Cerrar el gráfico
        fill='toself',
        name='Posttest',
        line_color=COLORS['posttest']['line'],
        fillcolor=COLORS['posttest']['fill']
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 8],
                tickvals=list(MAPPING.values()),
                ticktext=list(MAPPING.keys()),
                tick0=0,
                dtick=1
            )
        ),
        showlegend=True,
        title=f'Comparación Pretest y Posttest para {codigo}',
        height=700,
        width=900
    )

    return fig