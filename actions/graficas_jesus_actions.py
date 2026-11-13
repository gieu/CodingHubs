"""Gráficas Jesús - Encuentros Colaborativos 2026.

Documento de trabajo para las gráficas solicitadas

Recibe el DataFrame de instantáneas ya con columnas renombradas
(ver RENAME_INSTANTANEAS en app_pages/encuentros_colaborativos_2026.py):
    Encuentro, idEncuentro, numInstantanea, accionMomento, quienDirige,
    participaPares, participaDocentes, participaMentores, participaNA,
    participantes, comentario, ...

"""
import textwrap

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils.chart_config import get_chart_config

chart_config = get_chart_config()


def graficas_jesus(df):
    if df is None or df.empty:
        st.warning("No hay datos de instantáneas disponibles.")
        return

    grafica_heatmap_acciones(df)
    grafica_lineas_participantes(df)
    grafica_distribucion_genero(df)
    grafica_quien_dirige(df)


# Mismo estilo que el mapa de calor de la pestaña Instantáneas
BLUE_SCALE = ['#E8F6FA', '#D1EEEF', '#B9E5F4', '#A2DCF0', '#8BD3EC', '#74CAE8', '#5DC1E4', '#46BAD2', '#3FA8BD', '#3896A8']

# Acción (texto de la hoja) -> etiqueta corta. El orden de este diccionario es el orden del eje Y.
ETIQUETAS_ACCIONES = {
    'Dialogan activamente entre pares': 'Dialogan entre pares',
    'Realizan una actividad práctica': 'Realizan actividad práctica',
    'Un(a) docente hace una participación o intervención': 'Docente participa o interviene',
    'Escuchan una explicación temática de un par experto': 'Explicación de par experto',
    'Escuchan una explicación temática de un Coding Hub': 'Explicación de Coding Hub',
    'Escuchan instrucciones para el desarrollo de una actividad de un par experto': 'Instrucciones de par experto',
    'Escuchan instrucciones para el desarrollo de una actividad de un Coding Hub': 'Instrucciones de Coding Hub',
    'Escuchan una explicación temática de un facilitador del encuentro (ej. mentor)': 'Explicación de facilitador',
    'Escuchan instrucciones para el desarrollo de una actividad de un facilitador del encuentro (ej. mentor)': 'Instrucciones de facilitador',
    'Observan material audiovisual (ej. video explicativo sobre nodos o pensamiento computacional)': 'Observan material audiovisual',
    'Observan material audiovisual (ej. video explicativo sobre los Hubs o pensamiento computacional)': 'Observan material audiovisual',
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


def _envolver(texto, ancho=36):
    return "<br>".join(textwrap.wrap(str(texto), ancho))


def _etiqueta(accion):
    return ETIQUETAS_ACCIONES.get(accion) or _envolver(accion)


def grafica_heatmap_acciones(df):
    """Mapa de calor: frecuencia de cada acción del momento por número de instantánea."""
    st.subheader("📊 Mapa de Calor - Acción Momento vs Instantáneas")
    columnas = ["numero_instantanea", "accion_momento"]
    faltantes = [c for c in columnas if c not in df.columns]
    if faltantes:
        st.warning(f"Faltan columnas en los datos: {', '.join(faltantes)}")
        return

    datos = df[columnas].copy()
    datos["numero_instantanea"] = pd.to_numeric(datos["numero_instantanea"], errors="coerce")
    datos["accion_momento"] = datos["accion_momento"].astype("string").str.strip()
    datos = datos.dropna(subset=columnas)
    datos = datos[datos["accion_momento"] != ""]
    if datos.empty:
        st.warning("No hay suficientes datos para generar el mapa de calor.")
        return
    datos["numero_instantanea"] = datos["numero_instantanea"].astype(int)

    frecuencias = (
        datos.groupby(["accion_momento", "numero_instantanea"]).size().reset_index(name="Frecuencia")
    )
    pivot_data = frecuencias.pivot(
        index="accion_momento", columns="numero_instantanea", values="Frecuencia"
    ).fillna(0).astype(int)
    orden = [a for a in ETIQUETAS_ACCIONES if a in pivot_data.index]
    orden += [a for a in pivot_data.index if a not in orden]
    pivot_data = pivot_data.reindex(orden)

    fig = px.imshow(
        pivot_data.values,
        x=pivot_data.columns,
        y=[_etiqueta(a) for a in pivot_data.index],
        color_continuous_scale=BLUE_SCALE,
        title="Frecuencia de Acciones por Instantánea",
        labels=dict(x="Número de Instantánea", y="Acción Momento", color="Frecuencia"),
        aspect="auto",
    )
    fig.update_layout(
        height=max(560, 34 * len(pivot_data.index) + 180),
        yaxis_title="Acción Momento",
        xaxis_title="Número de Instantánea",
        font=dict(size=16),
        xaxis=dict(
            tickmode="array",
            tickvals=list(pivot_data.columns),
            ticktext=[str(int(x)) for x in pivot_data.columns],
            dtick=1,
            tickfont=dict(size=14),
        ),
        yaxis=dict(tickfont=dict(size=12), automargin=True),
        margin=dict(l=230, r=40, t=80, b=55),
        title=dict(font=dict(size=18)),
    )
    fig.update_traces(text=pivot_data.values, texttemplate="%{text}", textfont={"size": 14})
    st.plotly_chart(fig, use_container_width=True, config=chart_config)


PARTICIPANTES = {
    'participa_coding_hub_masters': ('Coding Hubs Masters', '#46BAD2'),
    'participa_docentes_acompanados': ('Docentes Acompañados', '#00A651'),
    'participa_mentores': ('Mentores', '#ff7f00'),
    'participa_no_aplica': ('No Aplica', '#271D67'),
}


def grafica_lineas_participantes(df):
    """Líneas: observaciones por instantánea en que participa cada tipo de participante."""
    st.subheader("📊 Participación por Tipo de Participante")
    columnas = ["numero_instantanea", *PARTICIPANTES]
    faltantes = [c for c in columnas if c not in df.columns]
    if faltantes:
        st.warning(f"Faltan columnas en los datos: {', '.join(faltantes)}")
        return

    datos = df.copy()
    # Una observación por instantánea registrada (la hoja trae una fila por acción).
    if "id_respuesta" in datos.columns:
        datos = datos.drop_duplicates(subset=["id_respuesta", "numero_instantanea"])
    datos["numero_instantanea"] = pd.to_numeric(datos["numero_instantanea"], errors="coerce")
    datos = datos.dropna(subset=["numero_instantanea"])
    if datos.empty:
        st.warning("No hay datos válidos de participación para mostrar.")
        return
    datos["numero_instantanea"] = datos["numero_instantanea"].astype(int)

    numeros = list(range(int(datos["numero_instantanea"].min()), int(datos["numero_instantanea"].max()) + 1))
    filas = []
    for col, (nombre, _) in PARTICIPANTES.items():
        llena = datos[col].astype("string").str.strip().replace("", pd.NA).notna()
        conteo = llena.groupby(datos["numero_instantanea"]).sum().reindex(numeros, fill_value=0)
        filas += [{"Instantáneas": n, "Tipo de Participante": nombre, "Cantidad de Observaciones": int(v)}
                  for n, v in conteo.items()]
    largo = pd.DataFrame(filas)

    fig = px.line(
        largo,
        x="Instantáneas",
        y="Cantidad de Observaciones",
        color="Tipo de Participante",
        markers=True,
        color_discrete_map={nombre: color for nombre, color in PARTICIPANTES.values()},
        category_orders={"Tipo de Participante": [n for n, _ in PARTICIPANTES.values()]},
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=8, line=dict(width=2, color="white")))
    fig.update_layout(
        height=500,
        legend=dict(title="Tipo de Participante", orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        xaxis=dict(tickmode="array", tickvals=numeros, ticktext=[str(n) for n in numeros]),
        yaxis=dict(rangemode="tozero", dtick=1),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True, config=chart_config)


CATEGORIAS_GENERO = ['Hombres y mujeres por igual', 'No aplica', 'Principalmente los hombres', 'Principalmente las mujeres']
COLORES_GENERO = {
    'Hombres y mujeres por igual': '#46BAD2',
    'No aplica': '#271D67',
    'Principalmente los hombres': '#00A651',
    'Principalmente las mujeres': '#ff7f00',
}


def _categoria_genero(fila):
    """Clasifica según qué casillas de género están llenas."""
    h, m, na = fila["participa_hombres"], fila["participa_mujeres"], fila["participa_genero_no_aplica"]
    if h and m and not na:
        return 'Hombres y mujeres por igual'
    if h and not m and not na:
        return 'Principalmente los hombres'
    if m and not h and not na:
        return 'Principalmente las mujeres'
    if na and not h and not m:
        return 'No aplica'
    return None


def _preparar_genero(df, columna_x):
    """Una observación por instantánea registrada (id_respuesta + numero_instantanea) con su categoría de género."""
    datos = df.copy()
    # La hoja trae una fila por acción; el género y el momento se repiten en cada una.
    if "id_respuesta" in datos.columns:
        datos = datos.drop_duplicates(subset=["id_respuesta", "numero_instantanea"])
    datos["numero_instantanea"] = pd.to_numeric(datos["numero_instantanea"], errors="coerce")
    datos = datos.dropna(subset=["numero_instantanea", columna_x])
    for c in ["participa_hombres", "participa_mujeres", "participa_genero_no_aplica"]:
        datos[c] = datos[c].astype("string").str.strip().replace("", pd.NA).notna()
    datos["categoria"] = datos.apply(_categoria_genero, axis=1)
    return datos.dropna(subset=["categoria"])


def _barras_apiladas(conteo, columna_x, titulo, titulo_x, ticks=None, etiquetas=None,
                    col_color="categoria", leyenda="Tipo de Participación por Género",
                    colores=None, orden=None):
    fig = px.bar(
        conteo,
        x=columna_x,
        y="Cantidad_Observaciones",
        color=col_color,
        title=titulo,
        labels={
            columna_x: titulo_x,
            "Cantidad_Observaciones": "Observaciones de instantáneas",
            col_color: leyenda,
        },
        color_discrete_map=colores or COLORES_GENERO,
        category_orders={col_color: orden or CATEGORIAS_GENERO},
        text="Cantidad_Observaciones",
    )
    fig.update_traces(texttemplate="%{text}", textposition="inside", textfont=dict(size=12))
    for traza in fig.data:
        color_texto = "white" if traza.marker.color in ("#271D67", "#8E44AD") else "#111111"
        traza.update(textfont=dict(color=color_texto), insidetextfont=dict(color=color_texto))
    xaxis = dict(tickmode="array", tickvals=ticks, ticktext=etiquetas) if ticks is not None else {}
    fig.update_layout(
        height=650,
        xaxis_title=titulo_x,
        yaxis_title="Observaciones de instantáneas",
        legend=dict(title="", orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        font=dict(size=12),
        xaxis=xaxis,
        yaxis=dict(rangemode="tozero", dtick=1),
        barmode="stack",
    )
    st.plotly_chart(fig, use_container_width=True, config=chart_config)


def grafica_distribucion_genero(df):
    """Barras apiladas: tipo de participación por género en cada instantánea."""
    st.subheader("📊 Distribución en Instantáneas")
    columnas = ["participa_hombres", "participa_mujeres", "participa_genero_no_aplica", "numero_instantanea"]
    faltantes = [c for c in columnas if c not in df.columns]
    if faltantes:
        st.warning(f"Faltan columnas en los datos: {', '.join(faltantes)}")
        return

    datos = _preparar_genero(df, "numero_instantanea")
    if datos.empty:
        st.warning("No hay datos válidos de participación por género para mostrar.")
        return
    datos["numero_instantanea"] = datos["numero_instantanea"].astype(int)
    conteo = datos.groupby(["numero_instantanea", "categoria"]).size().reset_index(name="Cantidad_Observaciones")
    numeros = sorted(conteo["numero_instantanea"].unique())
    _barras_apiladas(
        conteo, "numero_instantanea",
        "Distribución de Tipos de Participación por Género en Instantáneas",
        "Instantáneas", numeros, [str(n) for n in numeros],
    )


ETIQUETAS_DIRECCION = {
    'Sí, un(a) Coding Hub Master': 'Coding Hubs Masters',
    'Sí, un(a) docente acompañado(a)': 'Docentes Acompañados',
    'Sí, un mentor(a)': 'Mentores',
    'No, se da interacción entre varios/as docentes de manera balanceada': 'Dirección compartida entre docentes',
    'No ocurre interacción y/o ninguna persona dirige este momento': 'No Aplica',
}
COLORES_DIRECCION = {
    'Coding Hubs Masters': '#46BAD2',
    'Docentes Acompañados': '#00A651',
    'Mentores': '#ff7f00',
    'Dirección compartida entre docentes': '#8E44AD',
    'No Aplica': '#271D67',
}


def grafica_quien_dirige(df):
    """Barras apiladas: quién dirige la participación en cada instantánea."""
    st.subheader("📊 Dirección de Encuentros")
    columnas = ["quien_dirige", "numero_instantanea"]
    faltantes = [c for c in columnas if c not in df.columns]
    if faltantes:
        st.warning(f"Faltan columnas en los datos: {', '.join(faltantes)}")
        return

    datos = df.copy()
    # Una observación por instantánea registrada (la hoja trae una fila por acción).
    if "id_respuesta" in datos.columns:
        datos = datos.drop_duplicates(subset=["id_respuesta", "numero_instantanea"])
    datos["numero_instantanea"] = pd.to_numeric(datos["numero_instantanea"], errors="coerce")
    datos["quien_dirige"] = datos["quien_dirige"].astype("string").str.strip()
    datos = datos.dropna(subset=columnas)
    datos = datos[datos["quien_dirige"] != ""]
    if datos.empty:
        st.warning("No hay datos válidos de 'quien_dirige' para mostrar.")
        return
    datos["numero_instantanea"] = datos["numero_instantanea"].astype(int)
    datos["quien_dirige"] = datos["quien_dirige"].replace(ETIQUETAS_DIRECCION).astype(str)

    conteo = datos.groupby(["numero_instantanea", "quien_dirige"]).size().reset_index(name="Cantidad_Observaciones")
    numeros = sorted(conteo["numero_instantanea"].unique())
    _barras_apiladas(
        conteo, "numero_instantanea",
        "Dirección de Encuentros por Instantánea",
        "Instantáneas", numeros, [str(n) for n in numeros],
        col_color="quien_dirige", leyenda="Quién dirige la participación",
        colores=COLORES_DIRECCION, orden=list(COLORES_DIRECCION),
    )


# def grafica_ejemplo(df):
#     st.subheader("Título de la gráfica")
#     conteo = df["quienDirige"].value_counts().reset_index()
#     conteo.columns = ["Quien dirige", "Cantidad"]
#     fig = px.bar(conteo, x="Quien dirige", y="Cantidad")
#     st.plotly_chart(fig, use_container_width=True)
