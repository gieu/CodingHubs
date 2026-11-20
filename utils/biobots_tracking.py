"""Seguimiento de Bucaramanga: cálculos por docente y gráficas agregadas."""
import unicodedata

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

SOURCE_URL = 'https://docs.google.com/spreadsheets/d/1zRHI0l8VT1N9YarIez96LfJakxr2T4Wl/edit?gid=54809533#gid=54809533'
CSV_URL = 'https://docs.google.com/spreadsheets/d/1zRHI0l8VT1N9YarIez96LfJakxr2T4Wl/export?format=csv&gid=54809533'
SCENARIOS = {
    'E1': 'Numero de veces implementado E1',
    'E2 · Exploración': 'Numero de veces implementado E2 - Exploración',
    'E2 · Programación': 'Numero de veces implementado E2 fase de programación',
    'E3': 'Numero de veces implementado E3 - Programación',
    'E4': 'Numero de veces implementado E4',
    'E5': 'Numero de veces implementado E5',
}
GROUPS = ['Priorizados', 'No priorizados']
PALETTE = {'Priorizados': '#F39C12', 'No priorizados': '#1DB2E8'}


def normalized(value):
    return ' '.join(''.join(c for c in unicodedata.normalize('NFKD', str(value))
                           if not unicodedata.combining(c)).lower().split())


def prepare(raw):
    def column(prefix):
        matches = [c for c in raw if normalized(c).startswith(normalized(prefix))]
        if len(matches) != 1:
            raise ValueError(f'No se identificó una columna única para: {prefix}')
        return matches[0]

    name = column('Nombres completos')
    source = raw.loc[raw[name].notna() & raw[name].astype(str).str.strip().ne('')].copy()
    ids = source[column('Número de identificación')].astype('string').str.strip()
    if ids.isna().any() or ids.eq('').any() or ids.duplicated().any():
        raise ValueError('El seguimiento debe tener una fila por docente con identificación única.')
    data = pd.DataFrame(index=source.index)
    data['Grupo'] = source[column('Priorizados')].map(normalized).map({'si': GROUPS[0], 'no': GROUPS[1]}).fillna('Sin clasificación')
    fields = dict(SCENARIOS, Total='Total de número de veces que implemento el juego',
                  Acompañamiento='Sesiones de acompañamiento')
    for label, prefix in fields.items():
        values = source[column(prefix)].astype('string').str.strip().replace('', pd.NA)
        numeric = pd.to_numeric(values, errors='coerce')
        if (values.notna() & numeric.isna()).any() or (numeric.dropna() < 0).any() or (numeric.dropna() % 1 != 0).any():
            raise ValueError(f'Hay frecuencias inválidas en {label}.')
        data[label] = numeric.astype(float)
    return data.reset_index(drop=True)


def coverage(data, grouped=False):
    records = []
    groups = [(g, data[data['Grupo'].eq(g)]) for g in GROUPS] if grouped else [('Total', data)]
    for group, frame in groups:
        if frame.empty:
            continue
        for scenario in SCENARIOS:
            count = int(frame[scenario].gt(0).sum())
            records.append(dict(Grupo=group, Escenario=scenario, n=count, Base=len(frame),
                                Porcentaje=100 * count / len(frame),
                                Sin_registro=int(frame[scenario].isna().sum())))
    return pd.DataFrame(records)


def top_legend(fig):
    fig.update_layout(legend=dict(orientation='h', x=0, y=1.02, yanchor='bottom'), legend_title_text='')
    return fig


def bar_labels(fig):
    fig.update_traces(textposition='outside', cliponaxis=False, textfont=dict(size=12, color='#203447'))
    return fig


def distribution_figure(data):
    counts = data['Total'].dropna().value_counts().sort_index()
    fig = px.bar(x=counts.index, y=counts.values, text=counts.values,
                 color_discrete_sequence=['#1DB2E8'], title='Distribución de implementaciones por docente')
    fig.update_xaxes(title='Número total de implementaciones registradas', dtick=1)
    fig.update_traces(hovertemplate='%{x} implementaciones<br>%{y} docentes<extra></extra>')
    fig.update_yaxes(title='Número de docentes', dtick=1, rangemode='tozero')
    return bar_labels(fig)


def accompaniment_figure(data):
    fig = go.Figure()
    valid = data['Acompañamiento'].dropna()
    levels = list(range(int(valid.max()) + 1)) if not valid.empty else [0]
    for group in GROUPS:
        frame = data[data['Grupo'].eq(group)]
        if frame.empty:
            continue
        counts = frame['Acompañamiento'].value_counts().reindex(levels, fill_value=0)
        percentages = counts / len(frame) * 100
        fig.add_trace(go.Scatter(
            x=levels, y=percentages, mode='lines+markers', name=f'{group} ({len(frame)} docentes)',
            line=dict(color=PALETTE[group]), customdata=counts,
            hovertemplate='%{x} sesiones<br>%{y:.1f}% · %{customdata} docentes<extra>%{fullData.name}</extra>',
        ))
        for x, y in zip(levels, percentages):
            fig.add_annotation(x=x, y=float(y), text=f'{y:.1f}%', showarrow=False,
                               yshift=14 if group == GROUPS[0] else -16,
                               font=dict(size=12, color='#203447'), bgcolor='rgba(255,255,255,0.92)', borderpad=2)
    fig.update_layout(title='Frecuencia porcentual de acompañamiento',
                      legend=dict(itemclick=False, itemdoubleclick=False))
    fig.update_xaxes(title='Número de sesiones de acompañamiento', dtick=1)
    fig.update_yaxes(title='Porcentaje de docentes del grupo', ticksuffix='%', range=[-8, 108], tickvals=list(range(0, 101, 20)))
    return top_legend(fig)


def goals_figure(data):
    initial = data[list(SCENARIOS)].gt(0).any(axis=1)
    sequence = data[['E2 · Exploración', 'E2 · Programación', 'E3']].gt(0).all(axis=1)
    counts = [int(initial.sum()), int(sequence.sum())]
    table = pd.DataFrame({'Meta': ['Al menos una<br>implementación registrada', 'Secuencia registrada<br>hasta E3'], 'n': counts})
    table['Porcentaje'] = table['n'] / len(data) * 100
    fig = px.bar(table, x='Meta', y='Porcentaje', color='Meta',
                 color_discrete_sequence=['#1DB2E8', '#00A651'],
                 text=[f'{v:.1f}% · {n} de {len(data)}' for v, n in zip(table['Porcentaje'], counts)],
                 title='Cumplimiento de metas de implementación')
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title='')
    fig.update_yaxes(title='Porcentaje de docentes', ticksuffix='%', range=[0, 115])
    return bar_labels(fig)


def heatmap_figure(data):
    values = data.sort_values('Total', ascending=False, na_position='last')[list(SCENARIOS)]
    labels = [f'Docente {i+1:02d}' for i in range(len(values))]
    texts = [[str(int(v)) if pd.notna(v) else 'Sin registro' for v in row] for row in values.to_numpy()]
    fig = go.Figure(go.Heatmap(z=values.to_numpy(), x=list(SCENARIOS), y=labels,
                              colorscale=[[0, '#E3F2FD'], [0.45, '#1DB2E8'], [1, '#0D47A1']],
                              zmin=0, colorbar=dict(title='Veces'), hoverongaps=False,
                              hovertemplate='%{y}<br>%{x}: %{z} implementaciones<extra></extra>'))
    # Anotaciones también en celdas vacías, sin convertirlas en cero.
    for row, label in enumerate(labels):
        for col, scenario in enumerate(SCENARIOS):
            fig.add_annotation(x=scenario, y=label, text=texts[row][col], showarrow=False,
                               font=dict(size=11, color='#203447'), bgcolor='rgba(255,255,255,0.9)')
    fig.update_layout(title='Frecuencia de implementación por docente y escenario')
    fig.update_yaxes(autorange='reversed', title='Docentes (identificadores visuales anónimos)')
    fig.update_xaxes(title='', side='top')
    return fig


def coverage_figure(data, grouped=False):
    table = coverage(data, grouped)
    if table.empty:
        return None
    table['Etiqueta'] = table.apply(lambda r: f"{r['Porcentaje']:.1f}% · {r['n']}/{r['Base']}", axis=1)
    fig = px.bar(table, x='Escenario', y='Porcentaje', color='Grupo' if grouped else None,
                 barmode='group', text='Etiqueta', custom_data=['n', 'Base', 'Sin_registro'],
                 color_discrete_map=PALETTE, color_discrete_sequence=['#1DB2E8'],
                 title='Cobertura por escenario: priorizados vs. no priorizados' if grouped else 'Cobertura de implementación por escenario')
    fig.update_traces(hovertemplate='%{x}<br>%{y:.1f}% · %{customdata[0]} de %{customdata[1]} docentes<br>Sin registro: %{customdata[2]}<extra>%{fullData.name}</extra>')
    fig.update_yaxes(title='Porcentaje de docentes del grupo' if grouped else 'Porcentaje de docentes', ticksuffix='%', range=[0, 115])
    fig.update_xaxes(title='', tickvals=list(SCENARIOS), ticktext=[s.replace(' · ', '<br>') for s in SCENARIOS], automargin=True)
    return top_legend(bar_labels(fig))
