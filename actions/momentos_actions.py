"""Gráficas de la pestaña Momentos - Encuentros Colaborativos 2026.

Fuente: hoja "Afirmaciones EC" (una fila por encuentro x momento x afirmación).
Columnas usadas: id_respuesta, momento, afirmacion, respuesta.
"""
import textwrap

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from actions.graficas_jesus_actions import ETIQUETAS_ACCIONES
from utils.chart_config import get_chart_config

chart_config = get_chart_config()

GREEN_SCALE = ['#E8F5E8', '#C8E6C8', '#A5D6A7', '#81C784', '#66BB6A', '#4CAF50', '#43A047', '#388E3C', '#2E7D32', '#1B5E20']

# Fragmento único del texto de la afirmación -> conducta asociada al "qué" (en orden de aparición en el eje Y).
CONDUCTAS_QUE = {
    'relatan anécdotas': 'Anécdotas',
    'estrategias que conocen o han implementado para la enseñanza del pensamiento computacional': 'Estrategias',
    'vocabulario técnico': 'Vocabulario',
    'necesidades, intereses o características de sus estudiantes': 'Características estudiantes',
    'preguntas o buscan consejo sobre cómo responder mejor a los retos de sus estudiantes': 'Preguntas estudiantes',
    'reflexionan sobre brechas de género': 'Reflexión género',
    'diferencias o desigualdades entre niñas y niños': 'Diferencias género',
    'estrategias orientadas a cerrar brechas de género': 'Estrategias género',
}


# Igual para las conductas asociadas al "cómo" (en el orden de sus categorías).
CONDUCTAS_COMO = {
    'utilizan y expresan el humor': 'Humor',
    'palabras de ánimo': 'Ánimo',
    'valoran o agradecen': 'Valoración',
    'destacan las habilidades': 'Destacar habilidades',
    'invitan a otros a participar': 'Solicitar opinión',
    'recomiendan u ofrecen recursos': 'Recursos didácticos',
    'acompañan el desarrollo de una actividad': 'Acompañar actividad',
    'piden ayuda': 'Pedir ayuda',
    'reconocen que están aprendiendo': 'Reconocer aprendizaje',
    'reflexionan sobre cambios o mejoras': 'Reflexión mejoras',
    'plantean una perspectiva diferente': 'Perspectiva diferente',
    'contribuyen activamente': 'Contribución activa',
    'asume un rol predominante': 'Rol predominante',
}


def _conducta(afirmacion, catalogo):
    texto = str(afirmacion).lower()
    for fragmento, conducta in catalogo.items():
        if fragmento in texto:
            return conducta
    return None


def mapa_calor_conductas_que(df):
    """Mapa de calor: en cuántos encuentros se observó cada conducta del "qué" en cada momento."""
    _mapa_calor_conductas(df, CONDUCTAS_QUE)


def mapa_calor_conductas_como(df):
    """Mapa de calor: en cuántos encuentros se observó cada conducta del "cómo" en cada momento."""
    _mapa_calor_conductas(df, CONDUCTAS_COMO)


def barras_conductas_que(df):
    """Barras del "qué": % de observaciones por momento y total por conducta (mismas cifras del mapa de calor)."""
    _barras_conductas(df, CONDUCTAS_QUE)


def barras_conductas_como(df):
    """Barras del "cómo": % de observaciones por momento y total por conducta (mismas cifras del mapa de calor)."""
    _barras_conductas(df, CONDUCTAS_COMO)


def _frecuencias_conductas(df, catalogo):
    """Tabla conducta x momento con el número de encuentros en que la conducta se observó.

    Devuelve (pivot, total_encuentros, momentos), o None si faltan columnas o no hay datos.
    """
    columnas = ["id_respuesta", "momento", "afirmacion", "respuesta"]
    faltantes = [c for c in columnas if c not in df.columns]
    if faltantes:
        st.warning(f"Faltan columnas en los datos: {', '.join(faltantes)}")
        return None

    datos = df[columnas].copy()
    datos["conducta"] = datos["afirmacion"].apply(_conducta, catalogo=catalogo)
    datos = datos.dropna(subset=["conducta"])
    datos["momento"] = pd.to_numeric(datos["momento"].astype(str).str.extract(r"(\d+)")[0], errors="coerce")
    datos = datos.dropna(subset=["momento"])
    if datos.empty:
        st.warning("No hay datos válidos para las gráficas de conductas.")
        return None
    datos["momento"] = datos["momento"].astype(int)

    # Observada = cualquier respuesta distinta de "Ninguno"; las respuestas vacías cuentan como no observadas.
    respuesta = datos["respuesta"].astype("string").str.strip()
    datos["observada"] = respuesta.notna() & (respuesta.str.lower() != "ninguno") & (respuesta != "")

    total_encuentros = int(datos["id_respuesta"].nunique())

    # Frecuencia = número de encuentros (id_respuesta) con la conducta observada en el momento.
    observadas = datos[datos["observada"]].drop_duplicates(subset=["id_respuesta", "momento", "conducta"])
    momentos = sorted(datos["momento"].unique())
    pivot = (
        pd.crosstab(observadas["conducta"], observadas["momento"])
        .reindex(index=list(catalogo.values()), columns=momentos, fill_value=0)
    )
    return pivot, total_encuentros, momentos


def _mapa_calor_conductas(df, catalogo):
    resultado = _frecuencias_conductas(df, catalogo)
    if resultado is None:
        return
    pivot, total_encuentros, momentos = resultado

    fig = px.imshow(
        pivot.values,
        x=momentos,
        y=list(pivot.index),
        color_continuous_scale=GREEN_SCALE,
        # Escala fija 0..total de encuentros: así el máximo posible se ve aunque ninguna celda lo alcance.
        range_color=[0, total_encuentros],
        labels=dict(x="Momento", y="Conductas", color="Frecuencia"),
        aspect="auto",
    )
    fig.update_coloraxes(colorbar=dict(tickmode="linear", tick0=0, dtick=1))
    fig.update_layout(
        height=max(520, 50 * len(pivot.index) + 140),
        font=dict(size=16),
        xaxis=dict(tickmode="array", tickvals=momentos, ticktext=[str(m) for m in momentos], tickfont=dict(size=14)),
        yaxis=dict(tickfont=dict(size=13), automargin=True),
        margin=dict(l=230, r=40, t=30, b=55),
    )
    fig.update_traces(
        text=pivot.values, texttemplate="%{text}", textfont={"size": 14},
        hovertemplate="%{y}<br>Momento %{x}<br>Encuentros: %{z} de " + str(total_encuentros) + "<extra></extra>",
    )
    st.plotly_chart(fig, use_container_width=True, config=chart_config)
    st.caption(f"Se observaron {total_encuentros} encuentros, por eso la escala va de 0 a {total_encuentros} "
               f"(el máximo posible, aunque ninguna conducta lo alcance). Frecuencia = en cuántos de esos encuentros "
               "la conducta se observó en el momento (respuesta distinta de \"Ninguno\"; las respuestas vacías no cuentan).")


def _barras_conductas(df, catalogo):
    resultado = _frecuencias_conductas(df, catalogo)
    if resultado is None:
        return
    pivot, total_encuentros, momentos = resultado

    # Una observación = una conducta observada en un encuentro y momento (cada celda del mapa de calor suma las que tiene).
    total = int(pivot.values.sum())
    if total == 0:
        st.info("No se observó ninguna conducta de este grupo, así que no hay barras que mostrar.")
        return

    por_momento = pivot.sum(axis=0).rename("Observaciones").reset_index()
    por_momento.columns = ["Momento", "Observaciones"]
    por_momento["Porcentaje"] = (por_momento["Observaciones"] / total * 100).round(1)
    por_conducta = pivot.sum(axis=1).rename("Observaciones").reset_index()
    por_conducta.columns = ["Conducta", "Observaciones"]
    por_conducta = por_conducta.sort_values("Observaciones", ascending=True)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            por_momento, x="Momento", y="Porcentaje", text="Porcentaje",
            title="Porcentaje de conductas observadas por momento",
            labels={"Momento": "Número de momento", "Porcentaje": "Porcentaje (%)"},
            color="Porcentaje", color_continuous_scale=GREEN_SCALE,
            hover_data={"Observaciones": True},
        )
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(
            showlegend=False, height=420, coloraxis_showscale=False,
            xaxis=dict(tickmode="array", tickvals=momentos, ticktext=[str(m) for m in momentos]),
            yaxis=dict(title="Porcentaje (%)", range=[0, por_momento["Porcentaje"].max() * 1.2]),
        )
        st.plotly_chart(fig, use_container_width=True, config=chart_config)
    with col2:
        fig = px.bar(
            por_conducta, x="Observaciones", y="Conducta", text="Observaciones", orientation="h",
            title="Frecuencia total por conducta",
            labels={"Observaciones": "Observaciones", "Conducta": ""},
            color="Observaciones", color_continuous_scale=GREEN_SCALE,
        )
        fig.update_traces(texttemplate="%{text}", textposition="outside")
        fig.update_layout(
            showlegend=False, height=420, coloraxis_showscale=False,
            xaxis=dict(range=[0, por_conducta["Observaciones"].max() * 1.15]),
            yaxis=dict(automargin=True),
        )
        st.plotly_chart(fig, use_container_width=True, config=chart_config)
    st.caption(f"Una observación = una conducta observada en un encuentro y un momento (cada número del mapa de calor "
               f"suma una por encuentro). Total: {total} observaciones en {total_encuentros} encuentros. "
               "El porcentaje por momento es sobre ese total.")


# ==========================================
# LÍNEAS: CONDUCTAS DEL "QUÉ" Y DEL "CÓMO" POR TIPO DE PARTICIPANTE (hoja Momentos EC)
# ==========================================
GRUPOS_COMO = {
    'Construcción de ambiente colaborativo': ['Humor', 'Ánimo', 'Valoración', 'Destacar habilidades'],
    'Habilidades de mentoría y disposición a aprender': [
        'Solicitar opinión', 'Recursos didácticos', 'Acompañar actividad',
        'Pedir ayuda', 'Reconocer aprendizaje', 'Reflexión mejoras',
    ],
    'Comunicación en espacios de aprendizaje': ['Perspectiva diferente', 'Contribución activa', 'Rol predominante'],
}
GRUPOS_QUE = {
    'Transferencia de la experticia': ['Anécdotas', 'Estrategias', 'Vocabulario'],
    'Instrucción centrada en el estudiante': ['Características estudiantes', 'Preguntas estudiantes'],
    'Enfoque de género': ['Reflexión género', 'Diferencias género', 'Estrategias género'],
}
PARTICIPANTES_LINEAS = {'CHM': 'Coding Hub Master', 'DA': 'Docente acompañado'}
COLORES_PARTICIPANTES_LINEAS = {'Coding Hub Master': '#46BAD2', 'Docente acompañado': '#ff7f00'}


def lineas_conductas_que(df):
    """Líneas por conducta del "qué": % de encuentros en que cada tipo de participante la tuvo, por momento."""
    _lineas_conductas(df, CONDUCTAS_QUE, GRUPOS_QUE)


def lineas_conductas_como(df):
    """Líneas por conducta del "cómo": % de encuentros en que cada tipo de participante la tuvo, por momento."""
    _lineas_conductas(df, CONDUCTAS_COMO, GRUPOS_COMO)


def _lineas_conductas(df, catalogo, grupos):
    columnas = ["id_respuesta", "momento", "afirmacion", "respuesta", "rol"]
    faltantes = [c for c in columnas if c not in df.columns]
    if faltantes:
        st.warning(f"Faltan columnas en los datos: {', '.join(faltantes)}")
        return

    datos = df[columnas].copy()
    total_encuentros = datos["id_respuesta"].nunique()
    datos["conducta"] = datos["afirmacion"].apply(_conducta, catalogo=catalogo)
    datos["momento"] = pd.to_numeric(datos["momento"].astype(str).str.extract(r"(\d+)")[0], errors="coerce")
    datos = datos.dropna(subset=["conducta", "momento"])
    datos["momento"] = datos["momento"].astype(int)
    # Un código "D5" aparece como rol "D": se toma como Docente acompañado.
    datos["rol"] = datos["rol"].astype("string").str.strip().replace({"D": "DA"})
    respuesta = datos["respuesta"].astype("string").str.strip()
    observada = respuesta.notna() & (respuesta.str.lower() != "ninguno") & (respuesta != "")
    # Solo cuentan las observaciones atribuidas a un tipo de participante.
    datos = datos[observada & datos["rol"].isin(PARTICIPANTES_LINEAS)]
    datos = datos.drop_duplicates(subset=["id_respuesta", "momento", "conducta", "rol"])
    if total_encuentros == 0:
        st.warning("No hay datos válidos para las gráficas de conductas por participante.")
        return

    momentos = [1, 2, 3, 4, 5]
    cuentas = datos.groupby(["conducta", "rol", "momento"]).size()
    for grupo, conductas in grupos.items():
        filas = []
        for conducta in conductas:
            for rol, nombre in PARTICIPANTES_LINEAS.items():
                for momento in momentos:
                    n = int(cuentas.get((conducta, rol, momento), 0))
                    filas.append({
                        "Conducta": conducta, "Tipo de Participante": nombre, "Momento": momento,
                        "Porcentaje de Encuentros (%)": round(n / total_encuentros * 100, 1),
                        "Encuentros": n,
                    })
        largo = pd.DataFrame(filas)
        st.markdown(f"**{grupo}**")
        fig = px.line(
            largo,
            x="Momento",
            y="Porcentaje de Encuentros (%)",
            color="Tipo de Participante",
            facet_col="Conducta",
            facet_col_wrap=3,
            facet_row_spacing=0.2,
            markers=True,
            color_discrete_map=COLORES_PARTICIPANTES_LINEAS,
            category_orders={"Conducta": conductas, "Tipo de Participante": list(PARTICIPANTES_LINEAS.values())},
            hover_data={"Encuentros": True},
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=8, line=dict(width=2, color="white")))
        filas_fig = (len(conductas) + 2) // 3
        fig.update_layout(height=340 * filas_fig + 60, legend=dict(title="Tipo de Participante"))
        fig.update_yaxes(range=[0, 100])
        fig.update_xaxes(tickmode="array", tickvals=momentos, ticktext=[str(m) for m in momentos])
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        st.plotly_chart(fig, use_container_width=True, config=chart_config)
    st.caption(f"% = encuentros (de {total_encuentros}) en que al menos una persona de ese tipo mostró la conducta en el momento "
               "(respuesta distinta de \"Ninguno\").")


# ==========================================
# BARRAS: PARTICIPACIÓN POR CONDUCTA Y GÉNERO (hojas Momentos EC + Docentes únicos)
# ==========================================
COLORES_GENERO = {'Masculino': '#119713', 'Femenino': '#FA960B'}


def barras_conductas_genero_que(df, df_docentes):
    _barras_conductas_genero(df, df_docentes, CONDUCTAS_QUE, 'qué')


def barras_conductas_genero_como(df, df_docentes):
    _barras_conductas_genero(df, df_docentes, CONDUCTAS_COMO, 'cómo')


def _barras_conductas_genero(df, df_docentes, catalogo, nombre_grupo):
    """Entre las personas que mostraron cada conducta, qué % es Femenino y qué % Masculino.

    Persona = código dentro de un encuentro (id_respuesta + codigo). El sexo sale de la hoja Docentes únicos.
    """
    columnas = ["id_respuesta", "momento", "afirmacion", "respuesta", "rol", "codigo"]
    faltantes = [c for c in columnas if c not in df.columns]
    if faltantes:
        st.warning(f"Faltan columnas en los datos: {', '.join(faltantes)}")
        return
    if df_docentes is None or not {"id_respuesta", "codigo", "sexo"}.issubset(df_docentes.columns):
        st.warning("No hay datos de sexo (hoja Docentes únicos) para esta gráfica.")
        return

    datos = df[columnas].copy()
    datos["conducta"] = datos["afirmacion"].apply(_conducta, catalogo=catalogo)
    datos = datos.dropna(subset=["conducta"])
    respuesta = datos["respuesta"].astype("string").str.strip()
    observada = respuesta.notna() & (respuesta.str.lower() != "ninguno") & (respuesta != "")
    datos["codigo"] = datos["codigo"].astype("string").str.strip()
    # Solo observaciones atribuidas a una persona (con código).
    datos = datos[observada & datos["codigo"].notna() & (datos["codigo"] != "")]
    if datos.empty:
        st.info("No hay conductas de este grupo atribuidas a personas.")
        return

    # Un código "D5" aparece como rol "D": se toma como Docente acompañado.
    datos["rol"] = datos["rol"].astype("string").str.strip().replace({"D": "DA"})
    datos["Participante"] = datos["rol"].map(PARTICIPANTES_LINEAS)

    sexos = df_docentes[["id_respuesta", "codigo", "sexo"]].copy()
    sexos["codigo"] = sexos["codigo"].astype("string").str.strip()
    sexos["sexo"] = sexos["sexo"].astype("string").str.strip().str.title()
    sexos = sexos.drop_duplicates(subset=["id_respuesta", "codigo"])
    datos = datos.merge(sexos, on=["id_respuesta", "codigo"], how="left")

    total_obs = len(datos)
    datos = datos[datos["sexo"].isin(COLORES_GENERO)]
    sin_sexo = total_obs - len(datos)
    if datos.empty:
        st.info("No hay observaciones con sexo registrado para esta gráfica.")
        return
    datos = datos.rename(columns={"sexo": "Género", "conducta": "Conducta"})
    datos["persona"] = datos["id_respuesta"].astype(str) + "|" + datos["codigo"].astype(str)

    def _porcentajes(base, claves):
        por_genero = base.groupby(claves + ["Género"])["persona"].nunique().rename("Personas").reset_index()
        total = base.groupby(claves)["persona"].nunique().rename("Total").reset_index()
        tabla = por_genero.merge(total, on=claves)
        tabla["Porcentaje"] = (tabla["Personas"] / tabla["Total"] * 100).round(1)
        return tabla

    orden = [c for c in catalogo.values() if c in set(datos["Conducta"])]
    todos = _porcentajes(datos, ["Conducta"])
    por_participante = _porcentajes(datos.dropna(subset=["Participante"]), ["Conducta", "Participante"])

    fig = px.bar(
        todos, x="Conducta", y="Porcentaje", color="Género", barmode="group", text="Porcentaje",
        title=f"Participación por conducta del {nombre_grupo} y género (todos los participantes)",
        labels={"Porcentaje": "% de las personas que mostraron la conducta"},
        color_discrete_map=COLORES_GENERO,
        category_orders={"Conducta": orden, "Género": list(COLORES_GENERO)},
        hover_data={"Personas": True, "Total": True},
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(height=480, yaxis=dict(range=[0, 115]), xaxis=dict(tickangle=-30, automargin=True))
    st.plotly_chart(fig, use_container_width=True, config=chart_config)

    if not por_participante.empty:
        fig = px.bar(
            por_participante, x="Conducta", y="Porcentaje", color="Género", barmode="group", text="Porcentaje",
            facet_row="Participante",
            title=f"Participación por conducta del {nombre_grupo} y género, por tipo de participante",
            labels={"Porcentaje": "% de las personas que mostraron la conducta"},
            color_discrete_map=COLORES_GENERO,
            category_orders={"Conducta": orden, "Género": list(COLORES_GENERO),
                             "Participante": list(PARTICIPANTES_LINEAS.values())},
            hover_data={"Personas": True, "Total": True},
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(height=700, yaxis=dict(range=[0, 115]), yaxis2=dict(range=[0, 115]),
                          xaxis=dict(tickangle=-30, automargin=True), xaxis2=dict(tickangle=-30))
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        st.plotly_chart(fig, use_container_width=True, config=chart_config)

    st.caption(
        "Una persona = un código dentro de un encuentro. El porcentaje es, entre las personas que mostraron la conducta "
        "(al menos una vez en cualquier momento), la proporción de cada género. "
        f"El sexo viene de la hoja Docentes únicos; {sin_sexo} de {total_obs} observaciones no tienen sexo "
        "registrado ahí y quedan fuera."
    )


# ==========================================
# BURBUJAS: ACCIONES POR MOMENTO (hoja de instantáneas)
# ==========================================
GRUPOS_ACCIONES = {
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
        'Escuchan una explicación temática de un Coding Hub',
        'Escuchan instrucciones para el desarrollo de una actividad de un par experto',
        'Escuchan instrucciones para el desarrollo de una actividad de un Coding Hub',
        'Escuchan una explicación temática de un facilitador del encuentro (ej. mentor)',
        'Escuchan instrucciones para el desarrollo de una actividad de un facilitador del encuentro (ej. mentor)',
    ],
    'Otras': [
        'Observan un ejemplo, demostración o modelamiento',
        'Observan material audiovisual (ej. video explicativo sobre nodos o pensamiento computacional)',
        'Observan material audiovisual (ej. video explicativo sobre los Hubs o pensamiento computacional)',
        'Conversan sobre un tema personal o no relacionado con el encuentro',
        'Están distraídos o desconectados de las actividades',
        'Otra',
    ],
}
COLORES_GRUPOS_ACCIONES = {
    'Transferencia y Diálogo': '#7D3C98',
    'Actividades y Recursos': '#D81B84',
    'Escucha': '#2E86DE',
    'Otras': '#D4A935',
}


def _envolver(texto, ancho=18):
    return "<br>".join(textwrap.wrap(str(texto), ancho))


def burbujas_acciones_momento(df):
    """Mapa de burbujas: % de instantáneas de cada momento en que se registró cada acción."""
    columnas = ["id_respuesta", "numero_instantanea", "accion_momento", "en_que_momento"]
    faltantes = [c for c in columnas if c not in df.columns]
    if faltantes:
        st.warning(f"Faltan columnas en los datos: {', '.join(faltantes)}")
        return

    datos = df[columnas].dropna(subset=["numero_instantanea", "en_que_momento"]).copy()
    datos["momento"] = pd.to_numeric(datos["en_que_momento"].astype(str).str.extract(r"Momento\s*(\d+)")[0], errors="coerce")
    datos = datos.dropna(subset=["momento"])
    datos["momento"] = datos["momento"].astype(int)
    if datos.empty:
        st.warning("No hay datos válidos para el mapa de burbujas.")
        return

    # Nombre de cada momento (texto después del guion en "Momento 1 - Bienvenida y Rompehielos").
    nombres = (
        datos.assign(nombre=datos["en_que_momento"].astype(str).str.split(" - ", n=1).str[-1].str.strip())
        .groupby("momento")["nombre"].first()
    )
    # Observaciones = instantáneas registradas (una por id_respuesta + numero_instantanea).
    totales = datos.drop_duplicates(subset=["id_respuesta", "numero_instantanea"]).groupby("momento").size()
    acciones = datos.dropna(subset=["accion_momento"]).copy()
    acciones["accion_momento"] = acciones["accion_momento"].astype(str).str.strip()
    acciones = acciones.drop_duplicates(subset=["id_respuesta", "numero_instantanea", "accion_momento"])
    cuentas = acciones.groupby(["accion_momento", "momento"]).size().reset_index(name="n")
    cuentas["total"] = cuentas["momento"].map(totales)
    cuentas["Porcentaje"] = cuentas["n"] / cuentas["total"] * 100

    grupo_de = {a: g for g, lista in GRUPOS_ACCIONES.items() for a in lista}
    cuentas["Grupo"] = cuentas["accion_momento"].map(grupo_de).fillna("Otras")
    orden = [a for lista in GRUPOS_ACCIONES.values() for a in lista if a in set(cuentas["accion_momento"])]
    orden += [a for a in cuentas["accion_momento"].unique() if a not in orden]
    etiqueta = {a: ETIQUETAS_ACCIONES.get(a) or _envolver(a, 36) for a in orden}
    cuentas["Accion"] = cuentas["accion_momento"].map(etiqueta)
    etiquetas_y = list(dict.fromkeys(etiqueta[a] for a in orden))

    momentos = sorted(totales.index)
    ticktext = [f"M{m}<br>{_envolver(nombres.get(m, ''), 18)}" for m in momentos]
    sizeref = 2.0 * cuentas["Porcentaje"].max() / (54 ** 2)

    fig = go.Figure()
    for grupo, color in COLORES_GRUPOS_ACCIONES.items():
        parte = cuentas[cuentas["Grupo"] == grupo]
        if parte.empty:
            continue
        fig.add_trace(go.Scatter(
            x=parte["momento"], y=parte["Accion"], mode="markers+text", name=grupo,
            marker=dict(color=color, size=parte["Porcentaje"], sizemode="area", sizeref=sizeref,
                        sizemin=8, opacity=0.85, line=dict(width=0)),
            text=parte["Porcentaje"].round().astype(int).astype(str) + "%",
            textposition="middle center", textfont=dict(color="white", size=11),
            customdata=parte[["accion_momento", "n", "total", "Porcentaje", "Grupo"]],
            hovertemplate=("<b>%{customdata[0]}</b><br>Momento: M%{x}<br>Grupo: %{customdata[4]}<br>"
                           "%{customdata[1]} de %{customdata[2]} instantáneas<br>%{customdata[3]:.1f}%<extra></extra>"),
        ))
    fig.update_layout(
        height=max(620, 36 * len(etiquetas_y) + 220),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(size=13, color="#4A5568"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, title=""),
        margin=dict(l=245, r=45, t=95, b=110),
        xaxis=dict(title="", tickmode="array", tickvals=momentos, ticktext=ticktext, side="top",
                   range=[min(momentos) - 0.55, max(momentos) + 0.55], showgrid=False, zeroline=False,
                   tickfont=dict(size=11, color="#5A6473")),
        yaxis=dict(title="", categoryorder="array", categoryarray=list(reversed(etiquetas_y)),
                   showgrid=False, zeroline=False, tickfont=dict(size=11, color="#5A6473"), automargin=True),
    )
    st.plotly_chart(fig, use_container_width=True, config=chart_config)
    st.caption("Tamaño = % de instantáneas del momento en que se registró la acción. Una instantánea puede registrar "
               "varias acciones, por eso los porcentajes de un momento no suman 100%. "
               "Instantáneas por momento: " + ", ".join(f"M{m} = {int(totales[m])}" for m in momentos) + ".")
