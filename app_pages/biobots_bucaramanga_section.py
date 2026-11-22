"""Sección de encuesta de docentes BioBots de Bucaramanga."""
import pandas as pd
import plotly.express as px
import streamlit as st

from utils.biobots_bucaramanga import (
    SURVEY_URL, SOURCE_URL, GROUPS, distribution, stacked_figure, application_figure, barrier_counts, wrapped,
)


@st.cache_data(ttl=300)
def load_survey():
    data = pd.read_csv(SURVEY_URL).dropna(how='all')
    data.columns = data.columns.str.strip()
    if not any(c.startswith(GROUPS[0][1]) for c in data.columns):
        raise ValueError('La hoja no contiene las preguntas esperadas de la encuesta.')
    return data


def render(style_figure, plot, analysis_callout):
    st.header('Encuesta docente · Bucaramanga')
    st.caption('Percepciones docentes sobre la formación, la implementación y el uso de BioBots en Bucaramanga.')
    try:
        data = load_survey()
    except Exception:
        st.error('No fue posible cargar la encuesta de Bucaramanga desde Google Sheets. Verifica que la hoja permita lectura y vuelve a intentarlo.')
        st.markdown(f'[Abrir fuente de la encuesta]({SOURCE_URL})')
        return
    if data.empty:
        st.info('La encuesta todavía no contiene respuestas.')
        return
    st.metric('Respuestas recibidas · Bucaramanga', len(data))
    st.caption('Cada gráfica usa las respuestas no vacías de cada pregunta (n). Los vacíos no se interpretan como cero ni como desacuerdo. Se cuentan respuestas, no docentes únicos. “No aplica” se conserva en las transiciones.')
    for index, (title, prefix, order) in enumerate(GROUPS):
        table = distribution(data, prefix)
        if table.empty:
            st.info(f'Sin respuestas disponibles: {title}.')
            continue
        fig = stacked_figure(table, title, order)
        plot(style_figure(fig, height=max(480, table['Indicador'].nunique() * 85 + 180)), f'bucaramanga_{index}')
        with st.expander(f'Ver cifras · {title}'):
            st.dataframe(table, hide_index=True, use_container_width=True)
        if index == 1:
            difficult = table[table['Respuesta'].isin(['Difícil', 'Muy difícil'])].groupby('Indicador')['Porcentaje'].sum()
            if not difficult.empty:
                analysis_callout(
                    f'La transición con mayor dificultad declarada es {difficult.idxmax().lower()}: {difficult.max():.1f}% la considera difícil o muy difícil.',
                    'El porcentaje incluye “No aplica” en la base; no equivale a una tasa de fracaso ni permite inferir cuántos completaron cada escenario.',
                    'Reforzar la explicación y la práctica guiada en esta transición.')
        if index == 3:
            st.caption('Estas respuestas reflejan percepciones docentes; no son una medición directa del aprendizaje ni una estimación causal del efecto de BioBots.')
        if index == 5:
            plot(style_figure(application_figure(table), height=520), 'bucaramanga_application')
            st.caption('Se muestran solo “Resultados mixtos” y “Aplicado con éxito”; “Sin aplicación” (si existe) se ve en la gráfica apilada de arriba.')
        if index == 6:
            st.caption('Este bloque puede tener una base menor que el resto de la encuesta. No se asume que quienes no respondieron nunca usaron los recursos.')
    columns = [c for c in data.columns if c.startswith('¿Qué factores dificultaron')]
    if columns:
        table = barrier_counts(data[columns[0]])
        if not table.empty:
            fig = px.bar(table, x=table['Factor'].map(lambda label: wrapped(label, width=20)), y='Porcentaje', text=table['Porcentaje'].map(lambda p: f'{p:.1f}%'),
                         custom_data=['n', 'Base'], color_discrete_sequence=['#1DB2E8'], title='Barreras para avanzar en los escenarios')
            fig.update_traces(textposition='outside', textfont=dict(size=12, color='#203447'), cliponaxis=False, hovertemplate='%{x}<br>%{y:.1f}% · %{customdata[0]} de %{customdata[1]}<extra></extra>')
            fig.update_yaxes(range=[0, 110], ticksuffix='%', title='Porcentaje de respuestas válidas')
            fig.update_xaxes(title='', tickangle=0, automargin=True,
                             tickfont=dict(size=12, color='#2C3E50'))
            fig = style_figure(fig, height=640)
            fig.update_layout(margin=dict(b=150))
            plot(fig, 'bucaramanga_barriers')
            st.caption('Selección múltiple: los porcentajes pueden sumar más de 100%. Las respuestas distintas de las opciones identificadas se agrupan en “Otras dificultades”.')
            with st.expander('Ver cifras · Barreras'):
                st.dataframe(table, hide_index=True, use_container_width=True)
    with st.expander('Fuente y criterios · Bucaramanga'):
        st.markdown(f'[Encuesta de profesores BioBots Bucaramanga]({SOURCE_URL}). Actualización cada cinco minutos. No se publican nombres, documentos ni respuestas abiertas. La página no utiliza el Excel local.')
