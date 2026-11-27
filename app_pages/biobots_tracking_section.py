"""Bloque de seguimiento de Bucaramanga, independiente de la encuesta."""
import pandas as pd
import streamlit as st

from utils import biobots_tracking as tracking


@st.cache_data(ttl=300, show_spinner='Cargando seguimiento de Bucaramanga…')
def load_tracking():
    return tracking.prepare(pd.read_csv(tracking.CSV_URL))


def render(style_figure, plot):
    st.header('Implementación y acompañamiento · Bucaramanga')
    st.caption('Corte reportado: 19 de noviembre de 2026, 5:00 p. m. (hora de Colombia).')
    try:
        data = load_tracking()
    except Exception:
        st.error('No fue posible cargar el seguimiento de Bucaramanga. Verifica el acceso a la hoja y que contenga una fila por docente y las columnas de seguimiento.')
        st.markdown(f'[Abrir fuente de seguimiento]({tracking.SOURCE_URL})')
        return
    if data.empty:
        st.info('No hay docentes registrados en el seguimiento.')
        return
    cols = st.columns(3)
    cols[0].metric('Docentes en seguimiento', len(data))
    for col, group in zip(cols[1:], tracking.GROUPS):
        col.metric(group, int(data['Grupo'].eq(group).sum()))
    unclassified = int(data['Grupo'].eq('Sin clasificación').sum())
    if unclassified:
        st.warning(f'{unclassified} docentes sin clasificación de priorización: se incluyen en el total, pero no en las comparaciones entre grupos.')
    st.caption('Los campos vacíos se muestran como “sin registro”. Las comparaciones usan el total de docentes de cada grupo como base; no permiten atribuir diferencias a la priorización.')

    def show(fig, key, height=520, legend=False):
        fig = style_figure(fig, height=height)
        if legend:
            fig.update_layout(margin=dict(t=155, b=85))
        plot(fig, key)

    show(tracking.distribution_figure(data), 'buca_tracking_distribution')
    missing_total = int(data['Total'].isna().sum())
    st.caption(f'Base: {len(data) - missing_total} docentes con total registrado. Sin registro del total: {missing_total}. Se cuentan implementaciones registradas; no se infiere que equivalgan a días distintos.')

    show(tracking.accompaniment_figure(data), 'buca_tracking_accompaniment', legend=True)
    missing = ', '.join(f"{group}: {int(data.loc[data['Grupo'].eq(group), 'Acompañamiento'].isna().sum())} sin registro" for group in tracking.GROUPS)
    st.caption(f'Base: todos los docentes de cada grupo. {missing}. Los vacíos no se cuentan como cero sesiones.')

    relation = tracking.accompaniment_implementation_figure(data)
    if relation is not None:
        show(relation, 'buca_tracking_relation', height=560, legend=True)
        used = int(data.dropna(subset=['Acompañamiento', 'Total'])['Grupo'].isin(tracking.GROUPS).sum())
        st.caption(f'Base: {used} docentes clasificados con sesiones de acompañamiento e implementaciones registradas; se excluyen {len(data) - used} sin esos datos o sin clasificación. Cada punto es un docente y la línea negra es el promedio de implementaciones por número de sesiones. La relación es descriptiva y no demuestra que el acompañamiento cause más implementación.')

    show(tracking.goals_figure(data), 'buca_tracking_goals')
    st.caption('Implementación inicial: frecuencia positiva en al menos un escenario. Secuencia hasta E3: frecuencia positiva en E2 exploración, E2 programación y E3. Estos indicadores describen registros de implementación, no resultados de aprendizaje.')

    show(tracking.heatmap_figure(data), 'buca_tracking_heatmap', height=max(600, len(data) * 30 + 190))
    st.caption('Docentes ordenados por total de implementaciones. La columna E2 suma las fases de exploración y programación. Los identificadores son visuales y pueden cambiar al actualizarse los datos. Las celdas vacías indican ausencia de registro, no cero implementaciones.')

    show(tracking.coverage_figure(data), 'buca_tracking_coverage')
    st.caption(f'Base: {len(data)} docentes. Cada escenario cuenta a cada docente una sola vez cuando su frecuencia registrada es mayor que cero.')

    comparison = tracking.coverage_figure(data, grouped=True)
    if comparison is not None:
        show(comparison, 'buca_tracking_comparison', height=560, legend=True)
        st.caption('Cada barra muestra porcentaje y cantidad/base dentro del grupo. Una diferencia entre grupos es descriptiva y no demuestra un efecto de la priorización.')
        with st.expander('Ver cifras de cobertura por grupo'):
            st.dataframe(tracking.coverage(data, grouped=True), hide_index=True, use_container_width=True)
    else:
        st.info('No hay docentes clasificados para comparar los grupos.')
    with st.expander('Fuente y criterios del seguimiento'):
        st.markdown(f'[Seguimiento de gamificación de Bucaramanga]({tracking.SOURCE_URL}). Actualización en caché cada cinco minutos. El corte es el reportado para esta entrega; la hoja es una fuente viva y sus cambios posteriores no quedan congelados por esa fecha. No se utiliza el Excel local ni se muestran datos personales.')
