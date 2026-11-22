"""Agregaciones de la encuesta de Bucaramanga, sin datos personales."""
import re
import textwrap

import pandas as pd
import plotly.express as px

SURVEY_URL = 'https://docs.google.com/spreadsheets/d/1NEywB_s8a6bF-g-sNE33T6fm9W5NOLxqoyVKDM-fGCQ/export?format=csv'
SOURCE_URL = 'https://docs.google.com/spreadsheets/d/1NEywB_s8a6bF-g-sNE33T6fm9W5NOLxqoyVKDM-fGCQ/edit'
AGREEMENT = ['Totalmente en desacuerdo', 'En desacuerdo', 'Neutro', 'De acuerdo', 'Totalmente de acuerdo']
COLORS = ['#CC6600', '#F39C12', '#B0BEC5', '#1DB2E8', '#00A651']
GROUPS = [
    ('Formación, materiales y acompañamiento', 'A continuación, indique su nivel de acuerdo con las siguientes afirmaciones relacionadas con la formación', AGREEMENT),
    ('Dificultad de las transiciones entre escenarios', 'Con el objetivo de mejorar el juego', ['Muy difícil', 'Difícil', 'Moderada', 'Fácil', 'Muy fácil', 'No aplica']),
    ('Autonomía, sostenibilidad y capacidades docentes', 'Por favor, evalúe los siguientes enunciados', AGREEMENT),
    ('Comportamientos observados en estudiantes', 'A continuación, indique su nivel de acuerdo con las siguientes afirmaciones sobre los comportamientos', AGREEMENT),
    ('Desarrollo de conocimientos, habilidades y confianza', 'Como resultado de su participación en el acompañamiento', ['Sin aumento', 'Aumento ligero', 'Aumento', 'Aumento sustancial']),
    ('Aplicación de lo aprendido en el aula', 'Como resultado de su participación en las actividades de desarrollo profesional', ['Sin aplicación', 'Resultados mixtos', 'Aplicación exitosa']),
    ('Uso de recursos de Nodos de Pensamiento Computacional', 'En su práctica docente en el periodo comprendido entre agosto y noviembre de este año,', ['Nunca', '1-2 veces', '3-5 veces', '6-10 veces', 'Más de 10 veces']),
]
BARRIERS = [
    'Manejo del tiempo durante las sesiones',
    'Extensión o complejidad de las reglas de cada escenario',
    'Acceso o disponibilidad de materiales',
    'Dificultades de atención y concentración de los estudiantes',
    'Dificultades socioemocionales de los estudiantes',
    'Falta de tiempo disponible en el horario escolar',
    'Ninguna',
]


def clean(series):
    return series.astype('string').str.strip().replace('', pd.NA).dropna()


def response_label(value):
    if value.startswith('Mis conocimientos, habilidades y confianza'):
        if 'sustancialmente' in value:
            return 'Aumento sustancial'
        if 'ligeramente' in value:
            return 'Aumento ligero'
        if 'no han aumentado' in value.lower():
            return 'Sin aumento'
        if 'han aumentado en' in value:
            return 'Aumento'
    if value.startswith('He aplicado con éxito'):
        return 'Aplicación exitosa'
    if value.startswith('He intentado aplicar'):
        return 'Resultados mixtos'
    if value.startswith('No he intentado aplicar'):
        return 'Sin aplicación'
    return value


def distribution(df, prefix):
    records = []
    for column in df.columns:
        if not column.startswith(prefix) or '[' not in column:
            continue
        label = column.rsplit('[', 1)[-1].rstrip('] ').strip()
        values = clean(df[column]).map(response_label)
        for answer, count in values.value_counts().items():
            records.append({'Indicador': label, 'Respuesta': answer, 'n': int(count),
                            'Base': len(values), 'Porcentaje': count / len(values) * 100})
    return pd.DataFrame(records, columns=['Indicador', 'Respuesta', 'n', 'Base', 'Porcentaje'])


def wrapped(value, width=58):
    return '<br>'.join(textwrap.wrap(value, width))


def stacked_figure(table, title, order):
    data = table.copy()
    if data['Base'].nunique() == 1:
        data['Etiqueta'] = data['Indicador'].map(wrapped)
        base = int(data['Base'].iloc[0])
        title = f'{title}<br><span style="font-size:14px;font-weight:normal">{base} respuestas por pregunta</span>'
    else:
        data['Etiqueta'] = data.apply(
            lambda r: f"{wrapped(r['Indicador'])}<br>(n={r['Base']})", axis=1
        )
    palette = dict(zip(order, COLORS if len(order) == 5 else (
        COLORS + ['#ECEFF1'] if len(order) == 6 else ['#F39C12', '#B0BEC5', '#1DB2E8', '#00A651'])))
    if order == ['Sin aplicación', 'Resultados mixtos', 'Aplicación exitosa']:
        palette = dict(zip(order, ['#F39C12', '#B0BEC5', '#00A651']))
    for value in data['Respuesta'].unique():
        palette.setdefault(value, '#78909C')
    fig = px.bar(data, x='Porcentaje', y='Etiqueta', color='Respuesta', orientation='h',
                 custom_data=['n', 'Base'], title=title,
                 category_orders={'Respuesta': order, 'Etiqueta': list(data['Etiqueta'].unique())},
                 color_discrete_map=palette)
    fig.update_traces(hovertemplate='%{y}<br>%{x:.1f}% · %{customdata[0]} de %{customdata[1]}<extra>%{fullData.name}</extra>')
    # Las anotaciones no se ocultan ni se reducen al ancho del segmento.
    offsets = {}
    small_labels = {}
    for trace in fig.data:
        for label, percentage in zip(trace.y, trace.x):
            start = offsets.get(label, 0)
            center = start + float(percentage) / 2
            offsets[label] = start + float(percentage)
            shift = 0
            if percentage < 4:
                index = small_labels.get(label, 0)
                shift = 16 if index % 2 == 0 else -16
                small_labels[label] = index + 1
            value = f'{percentage:.1f}%' if percentage >= 0.1 else f'{percentage:.3g}%'
            fig.add_annotation(
                x=center, y=label, text=value,
                showarrow=False, xanchor='center', yanchor='middle', yshift=shift,
                font=dict(size=12, color='#203447'),
                bgcolor='rgba(255,255,255,0.92)',
                bordercolor='rgba(44,62,80,0.20)', borderwidth=1, borderpad=2,
            )
    fig.update_layout(
        barmode='stack',
        legend=dict(
            orientation='h', x=0, xanchor='left', y=1.02, yanchor='bottom',
            itemclick=False, itemdoubleclick=False,
            font=dict(size=12, color='#203447'), bgcolor='rgba(255,255,255,0.95)',
        ),
        legend_title_text='',
    )
    fig.update_xaxes(range=[0, 100], ticksuffix='%', title='Porcentaje de respuestas válidas')
    fig.update_yaxes(title='', automargin=True)
    return fig


APPLICATION_LABELS = [
    ('Lidero sesiones', 'Lidero sesiones de juego'),
    ('Identifico subhabilidades', 'Identifico subhabilidades de PC'),
    ('Integro oportunidades', 'Integro conocimientos matemáticos'),
    ('equidad de género', 'Promuevo equidad de género'),
    ('gestión de aula', 'Gestiono el aula para implementar'),
]


def application_figure(table):
    """Barras agrupadas: resultados mixtos vs. aplicación exitosa por área."""
    data = table[table['Respuesta'].isin(['Resultados mixtos', 'Aplicación exitosa'])].copy()

    def short(indicator):
        return next((label for key, label in APPLICATION_LABELS if key in indicator), indicator)

    data['Área'] = data['Indicador'].map(short).map(lambda v: wrapped(v, 18))
    data['Respuesta'] = data['Respuesta'].replace({'Aplicación exitosa': 'Aplicado con éxito'})
    areas = list(dict.fromkeys(data['Área']))
    base = int(data['Base'].max())
    fig = px.bar(data, x='Área', y='Porcentaje', color='Respuesta', barmode='group',
                 custom_data=['n', 'Base'], text=data['Porcentaje'].map(lambda p: f'{p:.1f}%'),
                 category_orders={'Área': areas, 'Respuesta': ['Resultados mixtos', 'Aplicado con éxito']},
                 color_discrete_map={'Resultados mixtos': '#1DB2E8', 'Aplicado con éxito': '#F39C12'},
                 title=f'Aplicación del aprendizaje en la práctica docente · N={base}')
    fig.update_traces(textposition='outside', cliponaxis=False, textfont=dict(size=12, color='#203447'),
                      hovertemplate='%{x}<br>%{y:.1f}% · %{customdata[0]} de %{customdata[1]}<extra>%{fullData.name}</extra>')
    fig.update_yaxes(range=[0, 100], ticksuffix='%', title='Porcentaje de docentes')
    fig.update_xaxes(title='Áreas de aplicación')
    fig.update_layout(legend=dict(title='', itemclick=False, itemdoubleclick=False))
    return fig


def barrier_counts(series):
    values = clean(series)
    counts = dict.fromkeys(BARRIERS + ['Otras dificultades'], 0)
    for value in values:
        remainder = value
        for option in BARRIERS:
            pattern = r'(?:^|,\s*)' + re.escape(option) + r'(?=,|$)'
            if re.search(pattern, remainder, flags=re.IGNORECASE):
                counts[option] += 1
                remainder = re.sub(pattern, '', remainder, flags=re.IGNORECASE)
        if remainder.strip(' ,.;'):
            counts['Otras dificultades'] += 1
    return pd.DataFrame([{'Factor': k, 'n': v, 'Base': len(values),
                          'Porcentaje': v / len(values) * 100}
                         for k, v in counts.items() if v]).sort_values('n', ascending=False) if len(values) else pd.DataFrame()
