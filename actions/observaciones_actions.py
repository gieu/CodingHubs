import random
import streamlit as st
import pandas as pd
import plotly.express as px

import plotly.graph_objects as go
import numpy as np

from utils.chart_config import get_chart_config

chart_config = get_chart_config()

def instantaneas(instantaneas):
    df = instantaneas.copy()

    st.subheader("Instantáneas")

    df = df.dropna(subset=["accion_docente_cat"])
    df = df[df["Número de instantánea"] <= 10]

    col1, col2 = st.columns(2)

    # Count how many occurrences of each category per instant and moment
    df_counts = (
        df.groupby(["momento", "Número de instantánea", "accion_docente_cat"])
        .size()
        .reset_index(name="count")
    )

    # Calculate percentages per instant within each moment
    df_counts["percent"] = (
        df_counts.groupby(["momento", "Número de instantánea"])["count"]
        .apply(lambda x: 100 * x / x.sum())
        .reset_index(drop=True)
    )

    # Split into two datasets
    for momento in df_counts["momento"].unique():
        df_momento = df_counts[df_counts["momento"] == momento]

        fig = px.line(
            df_momento,
            x="Número de instantánea",
            y="percent",
            color="accion_docente_cat",
            markers=True,
            title=f"Distribución porcentual de observaciones - {momento}",
            labels={
                "percent": "Porcentaje (%)",
                "Número de instantánea": "Instantánea",
            },
        )

        fig.update_layout(
            yaxis=dict(range=[0, 100]),
            legend_title_text="Observación",
            template="plotly_white",
            xaxis=dict(tickmode="linear", dtick=1),
        )

        if momento == "Pre":
            col1.plotly_chart(fig, config=chart_config, key=random.random())

        if momento == "Post":
            col2.plotly_chart(fig, config=chart_config, key=random.random())

    df_heat = instantaneas.copy()
    df_heat = df_heat[df_heat["Número de instantánea"] <= 10]

    # Ensure numeric and clean
    df_heat["Número de instantánea"] = pd.to_numeric(
        df_heat["Número de instantánea"], errors="coerce"
    )
    df_heat = df_heat.dropna(subset=["Número de instantánea", "accion_docente_clean"])

    # Calculate percentages per instantánea and momento
    df_counts = (
        df_heat.groupby(["momento", "Número de instantánea", "accion_docente_clean"])
        .size()
        .reset_index(name="count")
    )

    df_counts["percent"] = (
        df_counts.groupby(["momento", "Número de instantánea"])["count"]
        .apply(lambda x: 100 * x / x.sum())
        .reset_index(drop=True)
    )

    # Keep consistent y order by overall frequency
    ordered_actions = df_counts["accion_docente_clean"].value_counts().index.tolist()
    df_counts["accion_docente_clean"] = pd.Categorical(
        df_counts["accion_docente_clean"], categories=ordered_actions, ordered=True
    )

    # --- Create pivot tables per momento ---
    pivot_pre = df_counts[df_counts["momento"] == "Pre"].pivot(
        index="accion_docente_clean", columns="Número de instantánea", values="percent"
    )
    pivot_post = df_counts[df_counts["momento"] == "Post"].pivot(
        index="accion_docente_clean", columns="Número de instantánea", values="percent"
    )

    # --- Define same color scale as before (replace if needed) ---
    color_scale = "Purples"

    pivot_pre = pivot_pre.fillna(0)
    pivot_post = pivot_post.fillna(0)

    for momento in ["Pre", "Post"]:
        if momento == "Pre":
            data = pivot_pre
        else:
            data = pivot_post

        # --- Create side-by-side heatmaps (facets manually) ---
        fig = px.imshow(
            data,
            labels=dict(x="Instantánea", y="Acción del docente", color="Porcentaje"),
            x=data.columns,
            color_continuous_scale=color_scale,
            text_auto=".1f",
        )

        fig.update_layout(
            title=f"¿Qué está haciendo el docente? (Distribución porcentual por instantánea) - {momento}",
            # height=850,
            # margin=dict(l=280, r=40, t=80, b=10),
            coloraxis_colorbar=dict(title="Porcentaje"),
            template="plotly_white",
            title_x=0.3,
            xaxis=dict(tickmode="linear", dtick=1),
        )

        fig.update_traces(
            texttemplate="%{z:0.1f}%",
            hovertemplate="Acción: %{y}<br>Momento/Inst: %{x}<br>%{z:.1f}%<extra></extra>",
            textfont=dict(size=12),
        )

        fig.update_yaxes(autorange="reversed")

        st.plotly_chart(fig, config=chart_config, key=random.random())


def observaciones_generales(obs_generales):
    st.subheader("Observaciones Generales")
    objetivos_map = {
        "objetivos_aprend": {
            "positive_words": ["sí"],
            "negative_words": ["no"],
            "clean_name": "Objetivos de Aprendizaje",
            "category": "Inicio de clase",
        },
        "conoc_previos": {
            "positive_words": ["sí"],
            "negative_words": ["no"],
            "clean_name": "Conocimientos Previos",
            "category": "Inicio de clase",
        },
        "conceptos_clave": {
            "positive_words": ["sí"],
            "negative_words": ["no"],
            "clean_name": "Conceptos Clave",
            "category": "Inicio de clase",
        },
        "vocabulario_comp": {
            "positive_words": ["sí"],
            "negative_words": ["no"],
            "clean_name": "Vocabulario adecuado",
            "category": "Desarrollo de clase",
        },
        "conexion_vida": {
            "positive_words": ["sí"],
            "negative_words": ["no"],
            "clean_name": "Conexión con la vida diaria",
            "category": "Desarrollo de clase",
        },
        "prep_material": {
            "positive_words": ["sí"],
            "negative_words": ["no"],
            "clean_name": "Preparación de materiales",
            "category": "Desarrollo de clase",
        },
        "gestion_material": {
            "positive_words": ["sí"],
            "negative_words": ["no"],
            "clean_name": "Gestión de materiales",
            "category": "Desarrollo de clase",
        },
        "valoracion_esfuerzo": {
            "positive_words": ["sí"],
            "negative_words": ["no"],
            "clean_name": "Valoración del esfuerzo",
            "category": "Desarrollo de clase",
        },
        "apoyo_estudiantes": {
            "positive_words": ["sí"],
            "negative_words": ["no"],
            "clean_name": "Apoyo a estudiantes",
            "category": "Desarrollo de clase",
        },
        "uso_grafico_anclaje": {
            "positive_words": ["sí"],
            "negative_words": ["no"],
            "clean_name": "Gráfico de anclaje",
            "category": "Cierre de clase",
        },
        "metacognicion": {
            "positive_words": ["sí"],
            "negative_words": ["no"],
            "clean_name": "Metacognición y reflexión",
            "category": "Cierre de clase",
        },
    }

    clean_objetivos = obs_generales.copy()

    def clean_column_values(value, positive_words, negative_words):
        if pd.isna(value):
            return "No"
        value = value.lower().strip()
        if any(pos_word in value for pos_word in positive_words):
            return "Sí"
        if any(neg_word in value for neg_word in negative_words):
            return "No"
        return "No"

    # clean column values
    for col, mapping in objetivos_map.items():
        clean_objetivos[col] = clean_objetivos[col].str.lower().str.strip()
        clean_objetivos[col] = clean_objetivos[col].fillna("No")
        clean_objetivos[col] = clean_objetivos[col].apply(
            lambda x: clean_column_values(
                x, mapping["positive_words"], mapping["negative_words"]
            )
        )

    for col, mapping in objetivos_map.items():
        for momento in ["Pre", "Post"]:
            mask = clean_objetivos["momento"] == momento
            pos_count = (clean_objetivos.loc[mask, col] == "Sí").sum()
            neg_count = (clean_objetivos.loc[mask, col] == "No").sum()
            total = pos_count + neg_count
            percentage = (pos_count / total * 100) if total > 0 else 0
            key = "pre_percentage" if momento == "Pre" else "post_percentage"
            objetivos_map[col][key] = percentage
    # Flatten data for plotting and record section starts
    categories = []
    pretest = []
    posttest = []
    section_starts = []
    sections = []

    for col, mapping in objetivos_map.items():
        sections.append(mapping["category"])
        categories.append(mapping["clean_name"])
        pretest.append(mapping["pre_percentage"])
        posttest.append(mapping["post_percentage"])
        if mapping["category"] not in section_starts:
            section_starts.append(len(categories) - 1)

    # Create figure
    fig = go.Figure()

    # Add connecting lines
    for i in range(len(categories)):
        fig.add_trace(
            go.Scatter(
                x=[pretest[i], posttest[i]],
                y=[[sections[i], sections[i]], [categories[i], categories[i]]],
                mode="markers+lines",
                line=dict(color="lightgray", width=2),
                showlegend=False,
            )
        )

    full_sections = []

    for section in sections:
        full_sections.append(section)
        full_sections.append(section)

    # Add pretest and posttest markers + labels
    fig.add_trace(
        go.Scatter(
            x=pretest,
            y=[sections, categories],
            mode="markers+text",
            name="Pretest",
            marker=dict(color="cornflowerblue", size=10),
            text=[
                f"{v:.1f}" for v in pretest
            ],  # [f"{z}: {v:.1f}" for v, z in zip(pretest, sections)],
            textposition="middle left",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=posttest,
            y=[sections, categories],
            mode="markers+text",
            name="Postest",
            marker=dict(color="orchid", size=10),
            text=[f"{v:.1f}" for v in posttest],
            textposition="middle right",
        )
    )

    # Update y-axis gridlines
    fig.update_yaxes(gridcolor="lightgrey", gridwidth=1, showgrid=True)

    # Layout: reverse y to keep provided order top->bottom, increase left margin
    fig.update_layout(
        title="Porcentaje de docentes observados en cada práctica",
        xaxis_title="Docentes observados",
        xaxis=dict(range=[0, 110], ticksuffix="%"),
        template="simple_white",
        # height=700,
        yaxis_title="",
        yaxis=dict(autorange="reversed"),  # keep categories in the order we defined
        margin=dict(l=300, r=20, t=60, b=50),
        legend=dict(
            orientation="v",
            yanchor="bottom",
            y=0.8,
            xanchor="left",
            x=1.03,
            title="Momento",
        ),
    )

    st.plotly_chart(fig, config=chart_config, key=random.random())

    st.subheader("Uso de guías de aprendizaje")

    clean_obs = obs_generales.copy()
    clean_obs["momento"] = clean_obs["momento"].replace(
        {"Pre": "Pretest", "Post": "Postest"}
    )

    clean_obs["momento"] = pd.Categorical(
        clean_obs["momento"], categories=["Pretest", "Postest"], ordered=True
    )

    # Porcentaje de docentes que usan guías de aprendizaje (guia_pedagogica) (Sí/No)
    guia_counts = (
        clean_obs.groupby(["momento", "guia_pedagogica"], observed=True)
        .size()
        .reset_index(name="count")
    )
    guia_totals = (
        guia_counts.groupby("momento")["count"].sum().reset_index(name="total")
    )
    guia_counts = guia_counts.merge(guia_totals, on="momento")
    guia_counts["percentage"] = (guia_counts["count"] / guia_counts["total"]) * 100

    st.write(
        f"Total de clases: Pretest: {len(clean_obs[clean_obs['momento'] == 'Pretest'])} - Postest: {len(clean_obs[clean_obs['momento'] == 'Postest'])}"
    )

    fig = px.bar(
        guia_counts,
        x="guia_pedagogica",
        y="percentage",
        color="momento",
        barmode="group",
        title="Porcentaje de docentes que usan guías de aprendizaje",
        text_auto=".1f",
        labels={
            "percentage": "Porcentaje (%)",
            "guia_pedagogica": "Uso de Guía Pedagógica",
            "momento": "Momento",
        },
        category_orders={"momento": ["Pretest", "Postest"]},
    )
    fig.update_layout(legend_title_text="Momento")

    fig.update_yaxes(range=[0, 100])
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, config=chart_config, key=random.random())

    # Dispersión de grado observado (grado) vs grado de guía (grado_guia) por momento
    st.subheader("Grado observado vs Grado de guía")

    grado_guia = obs_generales.copy()

    grado_guia["momento"] = grado_guia["momento"].replace(
        {"Pre": "Pretest", "Post": "Postest"}
    )
    grado_guia["momento"] = pd.Categorical(
        grado_guia["momento"], categories=["Pretest", "Postest"], ordered=True
    )

    grado_numerico = grado_guia["grado_guia"].str.extract(r"(\d+)").astype(float)
    grado_guia["grado_guia"] = grado_numerico

    grado_guia["grado"] = grado_guia["grado"].str.extract(r"(\d+)").astype(float)

    fig = px.box(
        grado_guia,
        x="grado",
        y="grado_guia",
        color="momento",
        title="Grado observado vs Grado de guía",
        labels={
            "grado": "Grado Observado",
            "grado_guia": "Grado de Guía",
            "momento": "Momento",
        },
        category_orders={"momento": ["Pretest", "Postest"]},
    )
    fig.update_layout(legend_title_text="Momento")
    fig.update_xaxes(tickmode="linear", dtick=1)

    st.plotly_chart(fig, config=chart_config, key=random.random())

    # Quienes sí usan la guía (guia_pedagogica == "Sí"), distribución vs sexo docente, grado observado, asignatura (y por momento), una gráfica por variable
    st.subheader("Distribución de docentes que usan guías de aprendizaje")

    guia_usuarios = obs_generales[obs_generales["guia_pedagogica"] == "Sí"].copy()
    guia_usuarios["momento"] = guia_usuarios["momento"].replace(
        {"Pre": "Pretest", "Post": "Postest"}
    )
    st.write(
        f"Total de clases: Pretest: {len(guia_usuarios[guia_usuarios['momento'] == 'Pretest'])} - Postest: {len(guia_usuarios[guia_usuarios['momento'] == 'Postest'])}"
    )
    guia_usuarios["momento"] = pd.Categorical(
        guia_usuarios["momento"], categories=["Pretest", "Postest"], ordered=True
    )
    guia_usuarios["grado"] = guia_usuarios["grado"].str.extract(r"(\d+)").astype(int)
    variables = {
        "sexo_docente": "Sexo del Docente",
        "grado": "Grado Observado",
        "asignatura": "Asignatura",
    }
    for var, var_name in variables.items():
        conteo_var = (
            guia_usuarios.groupby(["momento", var], observed=True)
            .size()
            .reset_index(name="count")
        )
        total_var = (
            conteo_var.groupby("momento", observed=True)["count"]
            .sum()
            .reset_index(name="total")
        )
        conteo_var = conteo_var.merge(total_var, on="momento")
        conteo_var["percentage"] = (conteo_var["count"] / conteo_var["total"]) * 100

        fig = px.bar(
            conteo_var,
            x=var,
            y="percentage",
            color="momento",
            barmode="group",
            title=f"Distribución de docentes que usan guías por {var_name}",
            text_auto=".1f",
            labels={
                "percentage": "Porcentaje (%)",
                var: var_name,
                "momento": "Momento",
            },
            category_orders={"momento": ["Pretest", "Postest"]},
        )
        fig.update_layout(legend_title_text="Momento")

        # Show all x axis labels
        fig.update_xaxes(
            tickmode="array", tickvals=conteo_var[var], ticktext=conteo_var[var]
        )

        # axis from high to low

        fig.update_yaxes(range=[0, 100])
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, config=chart_config, key=random.random())
        

def observaciones_ti(obs_generales):
    df = obs_generales.copy()
    st.subheader("Actividades conectadas y desconectadas")

    # Porcentaje de docentes que usan actividades conectadas y desconectadas, ambas o ninguna (act_desconectada_presente, act_conectada_presente)
    # Color by momento

    df["Ambas actividades"] = np.where(
        (df["act_desconectada_presente"].str.lower().str.contains("sí"))
        & (df["act_conectada_presente"].str.lower().str.contains("sí")),
        True,
        False,
    )
    df["Ninguna actividad"] = np.where(
        (df["act_desconectada_presente"].str.lower().str.contains("no"))
        & (df["act_conectada_presente"].str.lower().str.contains("no")),
        True,
        False,
    )

    df["act_desconectada_presente"] = (
        df["act_desconectada_presente"].str.lower().str.contains("sí")
        & ~df["Ambas actividades"]
    )
    df["act_conectada_presente"] = (
        df["act_conectada_presente"].str.lower().str.contains("sí")
        & ~df["Ambas actividades"]
    )

    conteo_df = (
        df.groupby("momento")
        .agg(
            Actividad_Conectada=("act_conectada_presente", "sum"),
            Actividad_Desconectada=("act_desconectada_presente", "sum"),
            Ambas_Actividades=("Ambas actividades", "sum"),
            Ninguna_Actividad=("Ninguna actividad", "sum"),
        )
        .reset_index()
    )

    conteo_df["Total"] = conteo_df[
        [
            "Actividad_Conectada",
            "Actividad_Desconectada",
            "Ambas_Actividades",
            "Ninguna_Actividad",
        ]
    ].sum(axis=1)

    # Normalize each row by its total (so it sums to 100%)
    for col in [
        "Actividad_Conectada",
        "Actividad_Desconectada",
        "Ambas_Actividades",
        "Ninguna_Actividad",
    ]:
        conteo_df[col] = conteo_df[col] / conteo_df["Total"] * 100

    conteo_df_melted = conteo_df.drop(columns=["Total"]).melt(
        id_vars="momento", var_name="Tipo de Actividad", value_name="Porcentaje"
    )
    # Map momento values to match observaciones_stem and set order
    conteo_df_melted["momento"] = conteo_df_melted["momento"].replace(
        {"Pre": "Pretest", "Post": "Postest"}
    )
    conteo_df_melted["momento"] = pd.Categorical(
        conteo_df_melted["momento"], categories=["Pretest", "Postest"], ordered=True
    )

    st.write(
        f"Total de clases: Pretest: {len(df[df['momento'] == 'Pre'])} - Postest: {len(df[df['momento'] == 'Post'])}"
    )

    fig = px.bar(
        conteo_df_melted,
        x="Tipo de Actividad",
        y="Porcentaje",
        color="momento",
        barmode="group",
        title="Porcentaje de docentes por tipo de actividad",
        text_auto=".1f",
        labels={
            "Porcentaje": "Porcentaje (%)",
            "Tipo de Actividad": "Tipo de Actividad",
            "momento": "Momento",
        },
        category_orders={"momento": ["Pretest", "Postest"]},
    )
    fig.update_layout(legend_title_text="Momento")

    # Clean x axis labels
    fig.update_xaxes(
        ticktext=[
            "Conectada",
            "Desconectada",
            "Ambas",
            "Ninguna",
        ],
        tickvals=[
            "Actividad_Conectada",
            "Actividad_Desconectada",
            "Ambas_Actividades",
            "Ninguna_Actividad",
        ],
    )
    # Update traces to make text outside bars
    fig.update_yaxes(range=[0, 100])
    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, config=chart_config, key=random.random())
    # Practicas en actividades desconectadas (act_desconectada_compartir, act_desconectada_cierre, act_desconectada_eficacia)
    st.subheader("Prácticas en actividades desconectadas")
    practicas = {
        "act_desconectada_compartir": "Las/los estudiantes comparten la solución",
        "act_desconectada_cierre": "Onda semántica",
        "act_desconectada_eficacia": "Aplicación efectiva de conceptos y/o subhabilidades",
    }

    # Convertir las columnas a booleanas ("sí" → True)
    for col in practicas.keys():
        df[col] = df[col].astype(str).str.lower().str.contains("sí")

    # Contar cuántos "sí" hay por momento
    conteo_practicas = (
        df.groupby("momento").agg({col: "sum" for col in practicas}).reset_index()
    )

    # Filtrar docentes con actividades desconectadas o ambas
    mask = (df["act_desconectada_presente"] == True) | (df["Ambas actividades"] == True)

    # Calcular el total por momento
    totales_por_momento = df[mask].groupby("momento").size().reset_index(name="Total")

    # Hacer merge con conteo_practicas
    conteo_practicas = conteo_practicas.merge(
        totales_por_momento, on="momento", how="left"
    )

    # Si hay momentos sin coincidencias, rellenar con 0 o el tamaño total (según lo que necesites)
    conteo_practicas["Total"] = conteo_practicas["Total"].fillna(0)

    st.write(
        f"Total de clases con actividades desconectadas: Pretest: {int(totales_por_momento[totales_por_momento['momento']=='Pre']['Total'].values[0]) if 'Pre' in totales_por_momento['momento'].values else 0} - Postest: {int(totales_por_momento[totales_por_momento['momento']=='Post']['Total'].values[0]) if 'Post' in totales_por_momento['momento'].values else 0}"
    )


    # Convertir a porcentaje
    for col in practicas.keys():
        conteo_practicas[col] = conteo_practicas[col] / conteo_practicas["Total"] * 100

    # Dar formato para graficar
    conteo_practicas_melted = conteo_practicas.melt(
        id_vars="momento",
        value_vars=list(practicas.keys()),
        var_name="Práctica",
        value_name="Porcentaje",
    )

    # Reemplazar los nombres técnicos por los descriptivos
    conteo_practicas_melted["Práctica"] = conteo_practicas_melted["Práctica"].map(
        practicas
    )

    # Normalize momento labels and ordering
    conteo_practicas_melted["momento"] = conteo_practicas_melted["momento"].replace(
        {"Pre": "Pretest", "Post": "Postest"}
    )
    conteo_practicas_melted["momento"] = pd.Categorical(
        conteo_practicas_melted["momento"],
        categories=["Pretest", "Postest"],
        ordered=True,
    )

    fig = px.bar(
        conteo_practicas_melted,
        x="Práctica",
        y="Porcentaje",
        color="momento",
        barmode="group",
        title="Porcentaje de docentes que aplican cada práctica en actividades desconectadas",
        text_auto=".1f",
        labels={
            "Porcentaje": "Porcentaje (%)",
            "Práctica": "Práctica",
            "momento": "Momento",
        },
        category_orders={"momento": ["Pretest", "Postest"]},
    )
    fig.update_layout(legend_title_text="Momento")
    # Update traces to make text outside bars
    fig.update_yaxes(range=[0, 100])
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, config=chart_config, key=random.random())

    st.markdown("### Prácticas en actividades conectadas")

    # Columnas de interés (ya están en snake_case)
    cols_conectadas = [
        "act_conectada_predecir",
        "act_conectada_ejecutar_replicar",
        "act_conectada_ejecutar_entregar",
        "act_conectada_investigar_libre",
        "act_conectada_investigar_guiada",
        "act_conectada_investigar_compartir",
        "act_conectada_modificar_ind",
        "act_conectada_modificar_docente",
        "act_conectada_modificar_apoyo",
        "act_conectada_hacer_ind",
        "act_conectada_hacer_apoyo",
        "act_conectada_hacer_replicar",
    ]

    # PRIM
    labels_conectadas = {
        "act_conectada_predecir": ["Predecir (presenta código y pregunta qué hará)", "P"],
        "act_conectada_ejecutar_replicar": ["Ejecutar: replican código presentado", "R"],
        "act_conectada_ejecutar_entregar": ["Ejecutar: docente entrega código", "R"],
        "act_conectada_investigar_libre": ["Investigar: exploración libre", "I"],
        "act_conectada_investigar_guiada": ["Investigar: exploración guiada", "I"],
        "act_conectada_investigar_compartir": ["Investigar: comparten hallazgos", "I"],
        "act_conectada_modificar_ind": ["Modificar: cambios independientes", "M"],
        "act_conectada_modificar_docente": ["Modificar: liderado por docente", "M"],
        "act_conectada_modificar_apoyo": ["Modificar: con apoyo ocasional", "M"],
        "act_conectada_hacer_ind": ["Hacer: reto individual", "M "],
        "act_conectada_hacer_apoyo": ["Hacer: reto con apoyo", "M "],
        "act_conectada_hacer_replicar": ["Hacer: replican solución del docente", "M "],
    }

    mask_primm = df[cols_conectadas].notna().any(axis=1)

    totales_por_momento = (
        df[mask_primm].groupby("momento").size().reset_index(name="Total")
    )

    st.write(
        f"Total de clases con actividades PRIMM: Pretest: {int(totales_por_momento[totales_por_momento['momento']=='Pre']['Total'].values[0]) if 'Pre' in totales_por_momento['momento'].values else 0} - Postest: {int(totales_por_momento[totales_por_momento['momento']=='Post']['Total'].values[0]) if 'Post' in totales_por_momento['momento'].values else 0}"
    )

    for col in cols_conectadas:
        df[col] = (~df[col].isna()) * 1

    melted = df.melt(
        id_vars=["momento", "doc_docente"],  # mantiene el contexto
        value_vars=cols_conectadas,
        var_name="col",
        value_name="valor"
    )


    melted["label"] = melted["col"].map(lambda c: labels_conectadas[c][0])
    melted["grupo"] = melted["col"].map(lambda c: labels_conectadas[c][1])

    melted = melted[melted["valor"] == 1]

    df_primm = (
        melted.groupby(["momento", "grupo"])
        .agg({"doc_docente": "nunique", "valor": "sum"})
        .reset_index()
        .rename(columns={"doc_docente": "total_grupo"})
    )

    df_primm = df_primm.merge(totales_por_momento, on="momento", how="left")
    df_primm["porcentaje"] = df_primm["total_grupo"] / df_primm["Total"] * 100

    df_primm["momento"] = df_primm["momento"].replace({"Pre": "Pretest", "Post": "Postest"})

    df_primm["momento"] = pd.Categorical(
        df_primm["momento"],
        categories=["Pretest", "Postest"],
        ordered=True,
    )
    df_primm['grupo_espanol'] = df_primm['grupo'].replace({
        'P': 'P (Predecir)',
        'R': 'R (Ejecutar)',
        'I': 'I (Investigar)',
        'M': 'M (Modificar)',
        'M ': 'M (Hacer)'
    })

    fig_general = px.bar(
        df_primm,
        x="grupo_espanol",
        y="porcentaje",
        color="momento",
        barmode="group",  # barras lado a lado por momento
        title="Distribución por grupo PRIMM y momento",
        text="porcentaje",
        labels={
            "porcentaje": "Porcentaje (%)",
            "grupo": "Grupo PRIMM",
            "grupo_espanol": "Grupo PRIMM",
            "momento": "Momento",
        },
        range_y=[0, 100],
        text_auto=".1f",
        category_orders={"momento": ["Pretest", "Postest"]},

    )
    Order = ["P (Predecir)", "R (Ejecutar)", "I (Investigar)", "M (Modificar)", "M (Hacer)"]
    fig_general.update_xaxes(categoryorder="array", categoryarray=Order)
    fig_general.update_traces(textposition="outside")

    st.plotly_chart(fig_general, config=chart_config, key=random.random())
    
    # Distribución por práctica dentro de cada grupo PRIMM
    st.markdown("### Distribución por práctica dentro de cada grupo PRIMM")
    for group in ["R", "I", "M", "M "]:
        df_group = melted[melted["grupo"] == group]

        conteo_practicas = (
            df_group.groupby(["momento", "label"])["valor"]
            .sum()
            .reset_index()
        )

        conteo_practicas["momento"] = conteo_practicas["momento"].replace(
            {"Pre": "Pretest", "Post": "Postest"}
        )

        totales_por_momento = df_primm[df_primm["grupo"] == group][["momento", "total_grupo"]]

        st.write(
            f"Total de clases en grupo {group}: Pretest: {int(totales_por_momento[totales_por_momento['momento']=='Pretest']['total_grupo'].values[0]) if 'Pretest' in totales_por_momento['momento'].values else 0} - Postest: {int(totales_por_momento[totales_por_momento['momento']=='Postest']['total_grupo'].values[0]) if 'Postest' in totales_por_momento['momento'].values else 0}"
        )

        conteo_practicas = conteo_practicas.merge(
            totales_por_momento, on="momento", how="left"
        )
        conteo_practicas["porcentaje"] = (
            conteo_practicas["valor"] / conteo_practicas["total_grupo"] * 100
        )

        conteo_practicas["momento"] = pd.Categorical(
            conteo_practicas["momento"],
            categories=["Pretest", "Postest"],
            ordered=True,
        )

        fig = px.bar(
            conteo_practicas,
            x="label",
            y="porcentaje",
            color="momento",
            barmode="group",
            title=f"Distribución de prácticas en grupo {group}",
            text_auto=".1f",
            labels={
                "porcentaje": "Porcentaje (%)",
                "label": "Práctica",
                "momento": "Momento",
            },
            category_orders={"momento": ["Pretest", "Postest"]},
        )
        fig.update_yaxes(range=[0, 100])
        fig.update_traces(textposition="outside")

        st.plotly_chart(fig, config=chart_config, key=random.random())

    st.subheader("Estrategias conectadas")

    # Columnas de estrategias conectadas
    cols_estrategias = [
        "estrategia_pares",
        "estrategia_parsons",
        "estrategia_vivo",
        "estrategia_lectura",
        "estrategia_evaluacion",
        "estrategia_proyectos",
        "estrategia_diseno",
        "estrategia_tinkering",
        "estrategia_ninguna",
    ]

    labels_estrategias = {
        "estrategia_pares": "Programación por pares",
        "estrategia_parsons": "Preguntas de Parsons",
        "estrategia_vivo": "Programación en vivo",
        "estrategia_lectura": "Lectura de código",
        "estrategia_evaluacion": "Evaluación de pares",
        "estrategia_proyectos": "Aprendizaje Basado en Proyectos",
        "estrategia_diseno": "Pensamiento de Diseño",
        "estrategia_tinkering": "Tinkering",
        "estrategia_ninguna": "No se observa ninguna estrategia",
    }

    df[cols_estrategias] = df[cols_estrategias].apply(lambda col: ~pd.isna(col))

    mask_conectadas = (df["act_conectada_presente"] == True) | (
        df["Ambas actividades"] == True
    )
    totales_por_momento = (
        df[mask_conectadas].groupby("momento").size().reset_index(name="Total")
    )

    st.write(
        f"Total de clases con actividades conectadas: Pretest: {int(totales_por_momento[totales_por_momento['momento']=='Pre']['Total'].values[0]) if 'Pre' in totales_por_momento['momento'].values else 0} - Postest: {int(totales_por_momento[totales_por_momento['momento']=='Post']['Total'].values[0]) if 'Post' in totales_por_momento['momento'].values else 0}"
    )

    conteo_estrategias = (
        df.groupby("momento")
        .agg({col: "sum" for col in cols_estrategias})
        .reset_index()
    )

    conteo_estrategias = conteo_estrategias.merge(
        totales_por_momento, on="momento", how="left"
    )
    for col in cols_estrategias:
        conteo_estrategias[col] = (
            conteo_estrategias[col] / conteo_estrategias["Total"] * 100
        )

    conteo_estrategias_melted = conteo_estrategias.melt(
        id_vars="momento",
        value_vars=cols_estrategias,
        var_name="Estrategia",
        value_name="Porcentaje",
    )
    conteo_estrategias_melted["Estrategia"] = conteo_estrategias_melted[
        "Estrategia"
    ].map(labels_estrategias)
    conteo_estrategias_melted["momento"] = conteo_estrategias_melted["momento"].replace(
        {"Pre": "Pretest", "Post": "Postest"}
    )
    conteo_estrategias_melted["momento"] = pd.Categorical(
        conteo_estrategias_melted["momento"],
        categories=["Pretest", "Postest"],
        ordered=True,
    )

    fig = px.bar(
        conteo_estrategias_melted,
        x="Estrategia",
        y="Porcentaje",
        color="momento",
        barmode="group",
        title="Porcentaje de docentes que aplican cada estrategia en actividades conectadas",
        text_auto=".1f",
        labels={
            "Porcentaje": "Porcentaje (%)",
            "Estrategia": "Estrategia",
            "momento": "Momento",
        },
        category_orders={"momento": ["Pretest", "Postest"]},
    )
    # Normalize momento labels and set legend title
    # Update traces to make text outside bars
    fig.update_yaxes(range=[0, 100])
    fig.update_traces(textposition="outside")
    fig.update_layout(legend_title_text="Momento")
    st.plotly_chart(fig, config=chart_config, key=random.random())


def observaciones_stem(obs_generales):
    df = obs_generales.copy()
    st.subheader("Subhabilidades y Weintrop")
    st.write(
        f"Total de clases: Pretest {len(df[df['momento'] == 'Pre'])} - Postest {len(df[df['momento'] == 'Post'])}"
    )

    # === 1️⃣ Column groups ===
    subhabilidades_col = "subhabilidades_comp"
    weintrop_main_cols = [
        "practicas_datos",
        "practicas_programacion",
        "simulaciones",
        "pensamiento_sistemico",
    ]

    # === 2️⃣ Convert to boolean ("sí" → True, "no"/NaN → False) ===
    df[subhabilidades_col] = (
        df[subhabilidades_col].astype(str).str.lower().str.contains("sí")
    )
    for col in weintrop_main_cols:
        df[col] = df[col].astype(str).str.lower().str.contains("sí")

    # === 3️⃣ Compute summary columns ===
    df["Weintrop"] = df[weintrop_main_cols].any(axis=1)
    df["Subhabilidades"] = df[subhabilidades_col]

    df["Ambas"] = df["Weintrop"] & df["Subhabilidades"]
    df["Solo_Subhabilidades"] = df["Subhabilidades"] & ~df["Weintrop"]
    df["Solo_Weintrop"] = df["Weintrop"] & ~df["Subhabilidades"]
    df["Ninguna"] = ~df["Weintrop"] & ~df["Subhabilidades"]

    # === 4️⃣ Count per momento ===
    conteo_df = (
        df.groupby("momento")
        .agg(
            Subhabilidades=("Solo_Subhabilidades", "sum"),
            Weintrop=("Solo_Weintrop", "sum"),
            Ambas=("Ambas", "sum"),
            Ninguna=("Ninguna", "sum"),
        )
        .reset_index()
    )

    # === 5️⃣ Normalize per momento ===
    conteo_df["Total"] = conteo_df[
        ["Subhabilidades", "Weintrop", "Ambas", "Ninguna"]
    ].sum(axis=1)
    for col in ["Subhabilidades", "Weintrop", "Ambas", "Ninguna"]:
        conteo_df[col] = conteo_df[col] / conteo_df["Total"] * 100

    # === 6️⃣ Prepare for plot ===
    melted = conteo_df.drop(columns=["Total"]).melt(
        id_vars="momento", var_name="Tipo de práctica", value_name="Porcentaje"
    )

    # Cambiar nombres visibles a Pretest y Postest
    melted["momento"] = melted["momento"].replace({"Pre": "Pretest", "Post": "Postest"})

    fig = px.bar(
        melted,
        x="Tipo de práctica",
        y="Porcentaje",
        color="momento",
        barmode="group",
        title="Distribución de docentes según tipo de práctica (Subhabilidades vs Weintrop)",
        text_auto=".1f",
        labels={
            "Porcentaje": "Porcentaje (%)",
            "Tipo de práctica": "Tipo de práctica",
            "momento": "Momento",
        },
        category_orders={"momento": ["Pretest", "Postest"]},
    )
    fig.update_xaxes(
        ticktext=[
            "Solo<br>Subhabilidades",
            "Solo<br>Weintrop",
            "Ambas",
            "Ninguna",
        ],
        tickvals=["Subhabilidades", "Weintrop", "Ambas", "Ninguna"],
    )
    # Update traces to make text outside bars
    fig.update_yaxes(range=[0, 100])
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, config=chart_config, key=random.random())

    st.subheader("Detalle de subhabilidades aplicadas")

    subhabilidades = [
        "descomposicion",
        "patrones",
        "algoritmico",
        "depuracion",
        "abstraccion",
        "logico",
    ]

    for col in subhabilidades:
        df[col] = df[col].astype(str).str.lower().str.contains("sí")

    df_filtrado = df[df["Subhabilidades"] | df["Ambas"]].copy()

    # Contar ocurrencias por momento y subhabilidad (solo si están marcadas como True)
    conteo_subhabilidades = (
        df_filtrado.groupby("momento")[subhabilidades].sum().reset_index()
    )
    # Calcular total por momento (para normalizar)
    totales_por_momento = (
        df_filtrado.groupby("momento").size().reset_index(name="Total")
    )
    st.write(
        f"Total de clases: Pretest {totales_por_momento[totales_por_momento['momento'] == 'Pre'].sum()['Total']} - Postest {totales_por_momento[totales_por_momento['momento'] == 'Post'].sum()['Total']}"
    )

    # Merge para obtener los totales junto a los conteos
    conteo_subhabilidades = conteo_subhabilidades.merge(
        totales_por_momento, on="momento", how="left"
    )

    # Normalizar a porcentaje
    for col in subhabilidades:
        conteo_subhabilidades[col] = (
            conteo_subhabilidades[col] / conteo_subhabilidades["Total"] * 100
        )

    # Reformatear a formato largo para graficar
    conteo_subhabilidades_melted = conteo_subhabilidades.melt(
        id_vars="momento",
        value_vars=subhabilidades,
        var_name="Subhabilidad",
        value_name="Porcentaje",
    )

    label_map = {
        "descomposicion": "Descomposición",
        "patrones": "Patrones",
        "algoritmico": "Algorítmico",
        "depuracion": "Depuración",
        "abstraccion": "Abstracción",
        "logico": "Lógico",
    }
    # Cambiar nombres visibles a Pretest y Postest
    conteo_subhabilidades_melted["momento"] = conteo_subhabilidades_melted[
        "momento"
    ].replace({"Pre": "Pretest", "Post": "Postest"})

    conteo_subhabilidades_melted["Subhabilidad"] = conteo_subhabilidades_melted[
        "Subhabilidad"
    ].map(label_map)

    fig = px.bar(
        conteo_subhabilidades_melted,
        x="Subhabilidad",
        y="Porcentaje",
        color="momento",
        barmode="group",
        title="Distribución de prácticas de Subhabilidades por Momento",
        text_auto=".1f",
        labels={
            "Porcentaje": "Porcentaje (%)",
            "Subhabilidad": "Subhabilidad",
            "momento": "Momento",
        },
        category_orders={"momento": ["Pretest", "Postest"]},
    )

    fig.update_layout(legend_title_text="Momento")
    # Update traces to make text outside bars
    fig.update_yaxes(range=[0, 100])
    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, config=chart_config, key=random.random())

    st.subheader("Detalle de prácticas de Weintrop aplicadas")

    # Define main Weintrop practice columns
    main_weintrop_cols = [
        "practicas_datos",
        "practicas_programacion",
        "simulaciones",
        "pensamiento_sistemico",
    ]

    # Filter: docentes that did subhabilidades or ambas
    mask = (df["Weintrop"] == True) | (df["Ambas"] == True)
    df_filtrado = df[mask].copy()

    # Count occurrences per momento
    conteo_weintrop = (
        df_filtrado.groupby("momento")[main_weintrop_cols].sum().reset_index()
    )

    # Compute totals per momento
    totales_por_momento = (
        df_filtrado.groupby("momento").size().reset_index(name="Total")
    )
    st.write(
        f"Total de clases por momento: Pretest {totales_por_momento[totales_por_momento['momento'] == 'Pre'].sum()['Total']} - Postest {totales_por_momento[totales_por_momento['momento'] == 'Post'].sum()['Total']}"
    )

    # Merge to normalize
    conteo_weintrop = conteo_weintrop.merge(
        totales_por_momento, on="momento", how="left"
    )

    # Normalize to percentage
    for col in main_weintrop_cols:
        conteo_weintrop[col] = conteo_weintrop[col] / conteo_weintrop["Total"] * 100

    # Melt for plotting
    conteo_melted = conteo_weintrop.melt(
        id_vars="momento",
        value_vars=main_weintrop_cols,
        var_name="Dimensión",
        value_name="Porcentaje",
    )

    # Rename columns for display
    label_map = {
        "practicas_datos": "Prácticas de Datos",
        "practicas_programacion": "Prácticas de Programación",
        "simulaciones": "Simulaciones",
        "pensamiento_sistemico": "Pensamiento Sistémico",
    }
    conteo_melted["Dimensión"] = conteo_melted["Dimensión"].map(label_map)

    # Clean moment order and labels
    conteo_melted["momento"] = conteo_melted["momento"].replace(
        {"Pre": "Pretest", "Post": "Postest"}
    )
    conteo_melted["momento"] = pd.Categorical(
        conteo_melted["momento"], categories=["Pretest", "Postest"], ordered=True
    )

    # Plot
    fig_overall = px.bar(
        conteo_melted,
        x="Dimensión",
        y="Porcentaje",
        color="momento",
        barmode="group",
        text_auto=".1f",
        title="Distribución general de prácticas de Weintrop",
        category_orders={"momento": ["Pretest", "Postest"]},
    )
    fig_overall.update_layout(legend_title_text="Momento")
    # Update traces to make text outside bars
    fig_overall.update_yaxes(range=[0, 100])
    fig_overall.update_traces(textposition="outside")
    st.plotly_chart(fig_overall, config=chart_config, key=random.random())

    # Define subcomponents per dimension
    weintrop_dims = {
        "Prácticas de Datos": [
            "recoleccion_datos",
            "patrones_datos",
            "organizacion_datos",
            "visualizacion_datos",
        ],
        "Prácticas de Programación": [
            "descomposicion_prog",
            "instrucciones_prog",
            "codificacion",
            "depuracion_prog",
        ],
        "Simulaciones": ["uso_simuladores", "evaluacion_simulaciones"],
        "Pensamiento Sistémico": [
            "datos_numericos",
            "relaciones_numericas",
            "impacto_variables",
        ],
    }

    # Define pretty labels for plotting
    label_map = {
        "recoleccion_datos": "Recolección de datos",
        "patrones_datos": "Patrones en datos",
        "organizacion_datos": "Organización de datos",
        "visualizacion_datos": "Visualización de datos",
        "descomposicion_prog": "Descomposición (prog)",
        "instrucciones_prog": "Instrucciones paso a paso",
        "codificacion": "Codificación",
        "depuracion_prog": "Depuración (prog)",
        "uso_simuladores": "Uso de simuladores",
        "evaluacion_simulaciones": "Evaluación de simulaciones",
        "datos_numericos": "Datos numéricos",
        "relaciones_numericas": "Relaciones numéricas",
        "impacto_variables": "Impacto de variables",
    }

    for (dim, cols), main_col in zip(weintrop_dims.items(), main_weintrop_cols):
        # Filter teachers that did that dimension or ambas
        df_dim = df[df[main_col]].copy()
        # Count per momento
        for col in cols:
            df_dim[col] = df_dim[col].astype(str).str.lower().str.contains("sí")

        conteo_dim = df_dim.groupby("momento")[cols].sum().reset_index()

        # Normalize
        totales_dim = df_dim.groupby("momento").size().reset_index(name="Total")
        st.write(
            f"Total de clases con {dim}: Pretest {totales_dim[totales_dim['momento'] == 'Pre'].sum()['Total']} - Postest {totales_dim[totales_dim['momento'] == 'Post'].sum()['Total']}"
        )
        conteo_dim = conteo_dim.merge(totales_dim, on="momento", how="left")
        for col in cols:
            conteo_dim[col] = conteo_dim[col] / conteo_dim["Total"] * 100

        # Melt and label
        conteo_melt = conteo_dim.melt(
            id_vars="momento",
            value_vars=cols,
            var_name="Práctica",
            value_name="Porcentaje",
        )
        conteo_melt["Práctica"] = conteo_melt["Práctica"].map(label_map)
        conteo_melt["momento"] = conteo_melt["momento"].replace(
            {"Pre": "Pretest", "Post": "Postest"}
        )
        conteo_melt["momento"] = pd.Categorical(
            conteo_melt["momento"], categories=["Pretest", "Postest"], ordered=True
        )

        # Plot per dimension
        fig = px.bar(
            conteo_melt,
            x="Práctica",
            y="Porcentaje",
            color="momento",
            barmode="group",
            text_auto=".1f",
            title=f"{dim}: distribución por subpráctica",
            category_orders={"momento": ["Pretest", "Postest"]},
        )
        fig.update_layout(legend_title_text="Momento")
        # Update traces to make text outside bars
        fig.update_yaxes(range=[0, 100])
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, config=chart_config, key=random.random())
