"""Resumen Ejecutivo - Encuentros Colaborativos 2026.

Mismas secciones de siempre (Resumen General, Análisis por Participante, Distribución por Género),
calculadas con las hojas de 2026:
  - Momentos EC: una fila por encuentro x momento x afirmación x persona (rol CHM / DA).
  - Docentes únicos: lista de asistentes por encuentro con su sexo.
"""
import pandas as pd
import streamlit as st

from actions.momentos_actions import CONDUCTAS_COMO, CONDUCTAS_QUE, _conducta

PARTICIPANTES = {'CHM': 'Coding Hub Masters', 'DA': 'Docentes acompañados'}


def _corto(institucion):
    return str(institucion).replace("Institución Educativa ", "").strip()


def _preparar(df):
    """Conductas observadas (respuesta distinta de "Ninguno") atribuidas a un tipo de participante."""
    datos = df.copy()
    datos["rol"] = datos["rol"].astype("string").str.strip().replace({"D": "DA"})  # código D5 = DA
    respuesta = datos["respuesta"].astype("string").str.strip()
    datos = datos[respuesta.notna() & (respuesta.str.lower() != "ninguno") & datos["rol"].isin(PARTICIPANTES)].copy()
    datos["participante"] = datos["rol"].map(PARTICIPANTES)
    datos["Conducta"] = datos["categoria"].astype(str).str.strip()
    datos["tipo"] = datos["afirmacion"].apply(lambda a: _conducta(a, CONDUCTAS_QUE) or _conducta(a, CONDUCTAS_COMO))
    datos["Número de momento"] = pd.to_numeric(datos["momento"].astype(str).str.extract(r"(\d+)")[0], errors="coerce")
    datos["Encuentro"] = datos["coding_hub"].apply(_corto)
    datos = datos.dropna(subset=["tipo", "Número de momento"])
    # Varias personas del mismo tipo comparten la respuesta: se cuenta una observación por tipo de participante.
    return datos.drop_duplicates(subset=["id_respuesta", "Número de momento", "afirmacion", "participante"])


def resumen_ejecutivo(df, df_docentes):
    st.header("📋 Resumen Ejecutivo - Encuentros Colaborativos 2026")
    requeridas = ["id_respuesta", "coding_hub", "momento", "categoria", "afirmacion", "respuesta", "rol"]
    faltantes = [c for c in requeridas if c not in df.columns]
    if df.empty or faltantes:
        st.warning("No hay datos disponibles para generar el resumen ejecutivo."
                   + (f" Faltan columnas: {', '.join(faltantes)}" if faltantes else ""))
        return

    todo = df.assign(Encuentro=df["coding_hub"].apply(_corto))
    seleccion = st.selectbox(
        "Selecciona el encuentro:",
        ["Todos los encuentros"] + sorted(todo["Encuentro"].dropna().unique()),
        help="Escoge el encuentro específico para el análisis ejecutivo",
    )
    if seleccion != "Todos los encuentros":
        todo = todo[todo["Encuentro"] == seleccion]
    datos = _preparar(todo)
    if datos.empty:
        st.warning("No hay datos de conductas observadas para el encuentro seleccionado.")
        return

    # RESUMEN GENERAL
    total_encuentros = todo["id_respuesta"].nunique()
    st.markdown("### **Resumen General:**")
    col1, col2 = st.columns(2)
    col1.markdown(f"**- Total de encuentros:** {total_encuentros}")
    col2.markdown(f"**- Tipos de participantes:** {datos['participante'].nunique()}")
    st.markdown("**Distribución por conducta:**")
    for conducta, pct in (datos["Conducta"].value_counts() / len(datos) * 100).round(1).items():
        st.markdown(f"- {conducta}: {pct}%")
    st.markdown("---")

    # ANÁLISIS POR PARTICIPANTE
    st.markdown("### **Análisis por Participante:**")
    columnas = st.columns(2)
    for col, participante in zip(columnas, PARTICIPANTES.values()):
        parte = datos[datos["participante"] == participante]
        if parte.empty:
            continue
        encuentros = parte["id_respuesta"].nunique()
        momento_activo = parte.groupby(["Encuentro", "Número de momento"]).size()
        (enc_activo, mom_activo), obs_activo = momento_activo.idxmax(), momento_activo.max()
        conductas = parte["Conducta"].value_counts()
        tipos = parte["tipo"].value_counts()
        with col:
            st.markdown(f"### **{participante}:**")
            st.markdown(f"- **Participación en encuentros:** {encuentros} de {total_encuentros} ({encuentros / total_encuentros * 100:.1f}%)")
            st.markdown(f"- **Momento más activo:** Momento {int(mom_activo)} - Encuentro {enc_activo} ({obs_activo} observaciones)")
            st.markdown(f"- **Conducta principal:** {conductas.index[0]} ({conductas.iloc[0] / len(parte) * 100:.1f}%)")
            st.markdown(f"- **Comportamiento predominante:** {tipos.index[0]}")
            st.markdown(f"- **Diversidad de comportamientos:** {tipos.size} tipos diferentes")
    st.markdown("---")

    # DISTRIBUCIÓN POR GÉNERO (lista de docentes únicos)
    if df_docentes is not None and {"id_respuesta", "codigo", "sexo"}.issubset(df_docentes.columns):
        ids = set(todo["id_respuesta"])
        personas = df_docentes[df_docentes["id_respuesta"].isin(ids)].drop_duplicates(["id_respuesta", "codigo"])
        if not personas.empty:
            st.markdown("### **Distribución por Género:**")
            conteo = personas["sexo"].astype(str).str.strip().str.title().value_counts()
            for genero, cantidad in conteo.items():
                st.markdown(f"- **{genero}:** {cantidad} participantes ({cantidad / len(personas) * 100:.1f}%)")
            if "No Aplica" in conteo.index:
                st.caption("\"No aplica\" = asistentes sin sexo registrado en la lista de docentes.")
