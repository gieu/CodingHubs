import marimo

__generated_with = "0.17.0"
app = marimo.App(width="full")


@app.cell
def _():
    import pandas as pd
    import urllib
    return pd, urllib


@app.cell
def _(urllib):
    BASE_URL = (
        "https://docs.google.com/spreadsheets/d/1QqNppXXmSonnTDs3uplG3DtgvWW3pEjExcOh2Q_xb4M/gviz/tq?tqx=out:csv&sheet="
        + urllib.parse.quote_plus("Reporte de mentoría Coding Hubs")
    )
    # Los nombres de los docentes están en otra hoja
    NOMBRES_URL = "https://docs.google.com/spreadsheets/d/1QqNppXXmSonnTDs3uplG3DtgvWW3pEjExcOh2Q_xb4M/gviz/tq?tqx=out:csv&sheet=group_xt7jo03"
    ASISTENCIA_URL = "https://docs.google.com/spreadsheets/d/1T90vs6pBy12IpLvbxV4X-UhPUj2mDbxY/gviz/tq?tqx=out:csv&sheet=Asistencia%20CHM"
    BITACORA_AVANCES = (
        "https://docs.google.com/spreadsheets/d/1VGDTDAdsqRcaWDWqn6gwvw2q-wY3gQEB7JilCXW2qh0/gviz/tq?tqx=out:csv"
    )
    return ASISTENCIA_URL, BASE_URL, BITACORA_AVANCES, NOMBRES_URL


@app.cell
def _(ASISTENCIA_URL, BASE_URL, BITACORA_AVANCES, NOMBRES_URL, pd):
    base = pd.read_csv(BASE_URL)
    nombres = pd.read_csv(NOMBRES_URL)
    asistencia = pd.read_csv(ASISTENCIA_URL)
    bitacora = pd.read_csv(BITACORA_AVANCES)

    # drop empty columns
    base.dropna(how="all", axis=1, inplace=True)
    nombres.dropna(how="all", axis=1, inplace=True)
    asistencia.dropna(how="all", axis=1, inplace=True)
    bitacora.dropna(how="all", axis=1, inplace=True)
    return asistencia, base, bitacora, nombres


@app.cell
def _(base):
    base
    return


@app.cell
def _(nombres):
    nombres
    return


@app.cell
def _(base, nombres):
    base_completa = nombres.merge(base, left_on="_parent_index", right_on="_index")
    base_completa
    return (base_completa,)


@app.cell
def _(base_completa):
    base_filtrada = base_completa[
        base_completa["Información Institución Educativa/Docentes Asistentes/Rol"] == "Docente"
    ].copy()
    # revisar
    base_filtrada
    return (base_filtrada,)


@app.cell
def _(base_filtrada):
    base_filtrada["Reporte de acciones de acompañamiento/Indique la duración del acompañamiento, en minutos."] = (
        base_filtrada[
            "Reporte de acciones de acompañamiento/Indique la duración del acompañamiento, en minutos."
        ].astype(int)
    )

    base_filtrada["Información Institución Educativa/Docentes Asistentes/Docentes"] = base_filtrada[
        "Información Institución Educativa/Docentes Asistentes/Docentes"
    ].replace(
        {
            "Amanda Galindo Carrill": "Amanda Galindo Carrillo",
            "Andrés Felipe Osorio Gonzalez": "Andrés Felipe Osorio González",
            "Angelica Maria Gomez Henao": "Angélica María Gomez Henao",
            "Bach Sebastian Castañeda Reyes": "Bach Sebastián Castañeda Reyes",
            "Cristian Camilo Perez Arias": "Cristian Camilo Pérez Arias",
            "Daniel Felipe Naranjo Perez": "Daniel Felipe Naranjo Pérez",
            "Diego Fernando Garcia Florez": "Diego Fernando García Flórez",
            "Hector Alejandro Ruiz": "Héctor Alejandro Ruiz Villa",
            "Joly Patricia Duque Lopez": "Joly Patricia Duque López",
            "Julieth Johanna Cordon Sierra": "Julieth Johanna Cordón Sierra",
            "Leonardo Montes Marin": "Leonardo Montes Marín",
            "Lina Marcela Buitrago Chalarcá": "Lina Marcela Buitrago Chalarca",
            "Lorena Alvarez Ocampo": "Lorena Álvarez Ocampo",
            "Monica del Rocio Moreno Guerrero": "Mónica del Rocío Moreno Guerrero",
            "Nini Johanna Gutierrez": "Nini Johanna Gutiérrez Moreno",
            "Norma Constanza Valencia Angel": "Norma Constanza Valencia Ángel",
            "Sam Lopez": "Sam López Gómez",
        }
    )
    base_filtrada
    return


@app.cell
def _(asistencia):
    asistencia
    return


@app.cell
def _(bitacora):
    bitacora
    return


@app.cell
def _(bitacora):
    bitacora["¿De qué grado es la guía que eligió la/el par experto?"].value_counts()
    return


@app.cell
def _(bitacora):
    bitacora["tiempo_promedio_duracion_sesion"] = (
        bitacora[
            "¿Cuánto es el tiempo promedio para el desarrollo de una sesión de la guía? (en horas académicas)"
        ]
        .str.extract(r"(\d+)")
        .astype(float)
    )
    return


@app.cell
def _(bitacora):
    bitacora["frecuencia_uso_guia_semanas"] = bitacora[
        "¿Con qué frecuencia utiliza la guía la/el par experto?"
    ].map(
        {
            "Cada semana": 1,
            "Cada dos semanas": 0.5,
            "Cada mes": 0.25,
            "Cada tres semanas": 0.33,
            "Más de una vez a la semana": 2,
        }
    )
    return


@app.cell
def _(bitacora):
    bitacora_final = (
        bitacora.groupby("Docente de la institución educativa")
        .agg(
            {
                "tiempo_promedio_duracion_sesion": "mean",
                "frecuencia_uso_guia_semanas": "mean",
                "_uuid": len,
                "¿De qué grado es la guía que eligió la/el par experto?": set,
            }
        )
        .reset_index()
    )

    bitacora_final.rename(
        columns={
            "_uuid": "num_usos_guia",
            "¿De qué grado es la guía que eligió la/el par experto?": "guias_usadas",
        },
        inplace=True,
    )

    bitacora_final["Docente de la institución educativa"] = bitacora_final[
        "Docente de la institución educativa"
    ].replace(
        {
            "Angelica Maria Gomez Henao": "Angélica María Gomez Henao",
            "Bach Sebastian Castañeda Reyes": "Bach Sebastián Castañeda Reyes",
            "Leonardo Montes Marin": "Leonardo Montes Marín",
            "Sam Lopez": "Sam López Gómez",
        }
    )
    return (bitacora_final,)


@app.cell
def _(bitacora_final):
    bitacora_final
    return


@app.cell
def _():
    id_cols = {
        "base": "Información Institución Educativa/Docentes Asistentes/Docentes",
        "asistencia": "Nombre",
        "bitacora": "Docente de la institución educativa",
    }
    return (id_cols,)


@app.cell
def _(base_filtrada, pd):
    # group duplicates in base numerical columns with sum and categorical columns with mode
    def aggregate_base(df, id_col):
        agg_dict = {}
        for col in df.columns:
            if col == id_col:
                continue
            elif pd.api.types.is_numeric_dtype(df[col]):
                agg_dict[col] = "sum"
            else:
                agg_dict[col] = lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0]
        aggregated_df = df.groupby(id_col).agg(agg_dict).reset_index()
        # 1 hot encode
        # df["Línea del proyecto"] = df["Línea del proyecto"].apply(
        #     lambda x: x.split(",")[0] if pd.notnull(x) else x
        # )

        # linea_dummies = pd.get_dummies(df["Línea del proyecto"], prefix="linea", dtype=int)
        # linea_dummies[id_col] = df[id_col]
        # linea_agg = linea_dummies.groupby(id_col).sum().reset_index()
        # aggregated_df = pd.merge(aggregated_df, linea_agg, on=id_col, how="left")
        return aggregated_df


    # def aggregate_desafio(df, id_col):
    #     agg_dict = {}
    #     for col in df.columns:
    #         if col == id_col:
    #             continue
    #         elif pd.api.types.is_numeric_dtype(df[col]):
    #             agg_dict[col] = "sum"
    #         else:
    #             agg_dict[col] = lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0]

    #     aggregated_df = df.groupby(id_col).agg(agg_dict).reset_index()
    #     # 1 hot encode 'Nombre del tipo de iniciativa de Playground'
    #     iniciativa_dummies = pd.get_dummies(
    #         df["Nombre del tipo de iniciativa de Playground"], prefix="iniciativa", dtype=int
    #     )
    #     iniciativa_dummies[id_col] = df[id_col]
    #     iniciativa_agg = iniciativa_dummies.groupby(id_col).sum().reset_index()
    #     aggregated_df = pd.merge(aggregated_df, iniciativa_agg, on=id_col, how="left")
    #     return aggregated_df


    base_agg = aggregate_base(base_filtrada, "Información Institución Educativa/Docentes Asistentes/Docentes")
    return (base_agg,)


@app.cell
def _(base_agg):
    base_agg
    return


@app.cell
def _(asistencia, base_agg, bitacora_final, id_cols, pd):
    def merge_dataframes(dfs, id_cols):
        merged_df = dfs[0].copy()
        for i in range(1, len(dfs)):
            print(
                f"Merging dataframe {i} on {id_cols[list(id_cols.keys())[i]]}, dataframe: {list(id_cols.keys())[i]}"
            )
            merged_df = pd.merge(
                merged_df,
                dfs[i],
                left_on=id_cols[list(id_cols.keys())[0]],
                right_on=id_cols[list(id_cols.keys())[i]],
                how="left",
                suffixes=("", f"_{list(id_cols.keys())[i]}"),
            )
        return merged_df


    # Make all ids into object type to avoid merge issues
    for i, df in enumerate([base_agg, asistencia, bitacora_final]):
        id_col = id_cols[list(id_cols.keys())[i]]
        df[id_col] = df[id_col].astype(str)
        df[id_col] = df[id_col].str.strip()
        df[id_col] = df[id_col].str.replace("\.", "", regex=True)

    dataframes = [base_agg, asistencia, bitacora_final]
    merged_df = merge_dataframes(dataframes, id_cols)
    return dataframes, merged_df


@app.cell
def _(merged_df):
    merged_df
    return


@app.cell
def _(dataframes, id_cols):
    # check for repeated id values
    for df_id, dataframe in zip(id_cols.keys(), dataframes):
        print(f"Checking duplicates in {df_id} dataframe")
        print(f"with id column: {id_cols[df_id]}")
        idcol = id_cols[df_id]
        duplicated_ids = dataframe[dataframe.duplicated(subset=[idcol], keep=False)][idcol].unique()
        if len(duplicated_ids) > 0:
            print(f"Warning: The following IDs are duplicated in the {df_id} dataframe: {duplicated_ids}")
    return


@app.cell
def _(merged_df):
    merged_df.columns.tolist()
    return


@app.cell
def _(merged_df):
    merged_df
    return


@app.cell
def _():
    cols_to_keep_by_source = {
        "Información Institución Educativa/Docentes Asistentes/Docentes": "base",
        "Datos de identificación del mentor(a)/Nombre del mentor": "base",
        "Información Institución Educativa/Instituciones": "base",
        "Reporte de acciones de acompañamiento/Indique la duración del acompañamiento, en minutos.": "base",
        "Reporte de acciones de acompañamiento/Tema desarrollado en la mentoría/Plan de área": "base",
        "Reporte de acciones de acompañamiento/Tema desarrollado en la mentoría/Apoyo en la implementación de guías de pensamiento computacional (guías de Colombia programa)": "base",
        "Reporte de acciones de acompañamiento/Tema desarrollado en la mentoría/Revisión de recursos para el fomento del Pensamiento Computacional": "base",
        "Reporte de acciones de acompañamiento/Tema desarrollado en la mentoría/Planeación de actividades desconectadas": "base",
        "Reporte de acciones de acompañamiento/Tema desarrollado en la mentoría/Planeación deactividades conectadas": "base",
        "Reporte de acciones de acompañamiento/Tema desarrollado en la mentoría/Socialización del Plan de acompañamiento Institucional PAI": "base",
        "Reporte de acciones de acompañamiento/Tema desarrollado en la mentoría/Avance de acciones del PAI": "base",
        "Reporte de acciones de acompañamiento/Tema desarrollado en la mentoría/Apoyo al desarrollo de proyectos para el Tinkering Challenge": "base",
        "Reporte de acciones de acompañamiento/Tema desarrollado en la mentoría/Implementación acciones en pro de la equidad de género": "base",
        "Reporte de acciones de acompañamiento/Tema desarrollado en la mentoría/Planeación de clases con estrategias didácticas para la enseñanza del pensamiento computacional (Usa Modifica Crea, PRIMM, Preguntas de Parsons, Ondas semánticas, Programación en vivo, entre otras)": "base",
        "Reporte de acciones de acompañamiento/Tema desarrollado en la mentoría/Apoyo para preparar estudiantes para el CodeFest": "base",
        "Reporte de acciones de acompañamiento/Tema desarrollado en la mentoría/Planeación de clases incorporando prácticas de la taxonomía de Weintrop en otras áreas STEM": "base",
        "Reporte de acciones de acompañamiento/Tema desarrollado en la mentoría/Nivelación de contenidos para docentes nuevos o que no asisten a taller": "base",
        "Reporte de acciones de acompañamiento/Tema desarrollado en la mentoría/Apoyo en la preparación de espacios de experticia colaborativa": "base",
        "Cédula": "asistencia",
        "Categoría del docente": "asistencia",
        "Sexo": "asistencia",
        "Asistencia a Taller 1: Radio + pines": "asistencia",
        "Asistencia a taller 2: Habilidades de mentoría": "asistencia",
        "Asistencia a taller 2 nivel Senior pro: IA + microbit y simulación computacional y física": "asistencia",
        "Encuentro colaborativo 1": "asistencia",
        "Año Ingreso CH": "asistencia",
        "tiempo_promedio_duracion_sesion": "bitacora",
        "frecuencia_uso_guia_semanas": "bitacora",
        "num_usos_guia": "bitacora",
        "guias_usadas": "bitacora",
    }
    return (cols_to_keep_by_source,)


@app.cell
def _(cols_to_keep_by_source, merged_df):
    raw_merged = merged_df[[col for col in merged_df.columns if col in cols_to_keep_by_source.keys()]]
    return (raw_merged,)


@app.cell
def _(raw_merged):
    raw_merged["Información Institución Educativa/Docentes Asistentes/Docentes"].nunique()
    return


@app.cell
def _(raw_merged):
    raw_merged
    return


@app.cell
def _(asistencia, base_agg, pd):
    aligned_names = pd.concat(
        [
            base_agg["Información Institución Educativa/Docentes Asistentes/Docentes"],
            asistencia["Nombre"].sort_values(ascending=True).reset_index()["Nombre"],
        ],
        axis=1,
        ignore_index=True,
    )
    # Find names that do not match per row
    aligned_names.columns = ["base", "asistencia"]
    aligned_names["base"] = aligned_names["base"].str.strip()
    aligned_names["asistencia"] = aligned_names["asistencia"].str.strip()
    aligned_names["match"] = aligned_names["base"] == aligned_names["asistencia"]
    mismatched_names = aligned_names[~aligned_names["match"]]
    mismatched_names
    return (mismatched_names,)


@app.cell
def _(mismatched_names):
    # map base to asistencia on mismatches
    mismatch_map = {x["base"]: x["asistencia"] for _, x in mismatched_names.iterrows()}
    mismatch_map
    return


@app.cell
def _(base_agg, bitacora_final):
    nombres_base = base_agg["Información Institución Educativa/Docentes Asistentes/Docentes"].tolist()
    nombres_bitacora = bitacora_final["Docente de la institución educativa"].tolist()

    # Find nombres in bitacora that are not in base
    nombres_no_en_base = [nombre for nombre in nombres_bitacora if nombre not in nombres_base]
    nombres_no_en_base
    return


@app.cell
def _(raw_merged):
    raw_merged
    return


@app.cell
def _(cols_to_keep_by_source, raw_merged):
    # Normalize column names, lower case, remove duplicated spaces, replace spaces with underscores, remove special characters, remove accents, add source as suffix
    import unicodedata


    def normalize_column_name(col_name):
        suffix = cols_to_keep_by_source.get(col_name, "")
        col_name = col_name.lower()
        col_name = " ".join(col_name.split())
        col_name = col_name.replace(" ", "_")
        col_name = "".join(c for c in unicodedata.normalize("NFD", col_name) if unicodedata.category(c) != "Mn")
        col_name = "".join(c for c in col_name if c.isalnum() or c == "_")
        col_name = f"{col_name}_{suffix}" if suffix else col_name
        return col_name


    raw_merged.columns = [normalize_column_name(col) for col in raw_merged.columns]
    raw_merged
    return


@app.cell
def _(raw_merged):
    raw_merged.columns.to_list()
    return


@app.cell
def _():
    rename_dict = {
        "informacion_institucion_educativadocentes_asistentesdocentes_base": "nombre_docente_base",
        "datos_de_identificacion_del_mentoranombre_del_mentor_base": "nombre_mentor_base",
        "informacion_institucion_educativainstituciones_base": "institucion_educativa_base",
        "reporte_de_acciones_de_acompanamientoindique_la_duracion_del_acompanamiento_en_minutos_base": "duracion_acompanamiento_minutos_base",
        "reporte_de_acciones_de_acompanamientotema_desarrollado_en_la_mentoriaplan_de_area_base": "plan_de_area_base",
        "reporte_de_acciones_de_acompanamientotema_desarrollado_en_la_mentoriaapoyo_en_la_implementacion_de_guias_de_pensamiento_computacional_guias_de_colombia_programa_base": "apoyo_implementacion_guias_pc_base",
        "reporte_de_acciones_de_acompanamientotema_desarrollado_en_la_mentoriarevision_de_recursos_para_el_fomento_del_pensamiento_computacional_base": "revision_recursos_fomento_pc_base",
        "reporte_de_acciones_de_acompanamientotema_desarrollado_en_la_mentoriaplaneacion_de_actividades_desconectadas_base": "planeacion_actividades_desconectadas_base",
        "reporte_de_acciones_de_acompanamientotema_desarrollado_en_la_mentoriaplaneacion_deactividades_conectadas_base": "planeacion_actividades_conectadas_base",
        "reporte_de_acciones_de_acompanamientotema_desarrollado_en_la_mentoriasocializacion_del_plan_de_acompanamiento_institucional_pai_base": "socializacion_pai_base",
        "reporte_de_acciones_de_acompanamientotema_desarrollado_en_la_mentoriaavance_de_acciones_del_pai_base": "avance_acciones_pai_base",
        "reporte_de_acciones_de_acompanamientotema_desarrollado_en_la_mentoriaapoyo_al_desarrollo_de_proyectos_para_el_tinkering_challenge_base": "apoyo_tinkering_challenge_base",
        "reporte_de_acciones_de_acompanamientotema_desarrollado_en_la_mentoriaimplementacion_acciones_en_pro_de_la_equidad_de_genero_base": "implementacion_acciones_equidad_genero_base",
        "reporte_de_acciones_de_acompanamientotema_desarrollado_en_la_mentoriaplaneacion_de_clases_con_estrategias_didacticas_para_la_ensenanza_del_pensamiento_computacional_usa_modifica_crea_primm_preguntas_de_parsons_ondas_semanticas_programacion_en_vivo_entre_otras_base": "estrategias_pc_base",
        "reporte_de_acciones_de_acompanamientotema_desarrollado_en_la_mentoriaapoyo_para_preparar_estudiantes_para_el_codefest_base": "apoyo_preparacion_codefest_base",
        "reporte_de_acciones_de_acompanamientotema_desarrollado_en_la_mentoriaplaneacion_de_clases_incorporando_practicas_de_la_taxonomia_de_weintrop_en_otras_areas_stem_base": "planeacion_clases_taxonomia_weintrop_base",
        "reporte_de_acciones_de_acompanamientotema_desarrollado_en_la_mentorianivelacion_de_contenidos_para_docentes_nuevos_o_que_no_asisten_a_taller_base": "nivelacion_contenidos_docentes_nuevos_base",
        "reporte_de_acciones_de_acompanamientotema_desarrollado_en_la_mentoriaapoyo_en_la_preparacion_de_espacios_de_experticia_colaborativa_base": "apoyo_espacios_experticia_colaborativa_base",
        "cedula_asistencia": "cedula_asistencia",
        "categoria_del_docente_asistencia": "categoria_docente_asistencia",
        "sexo_asistencia": "sexo_asistencia",
        "asistencia_a_taller_1_radio__pines_asistencia": "taller_1_asistencia",
        "asistencia_a_taller_2_habilidades_de_mentoria_asistencia": "taller_2_asistencia",
        "asistencia_a_taller_2_nivel_senior_pro_ia__microbit_y_simulacion_computacional_y_fisica_asistencia": "taller_2_senior_pro_asistencia",
        "encuentro_colaborativo_1_asistencia": "encuentro_colaborativo_1_asistencia",
        "ano_ingreso_ch_asistencia": "ano_ingreso_ch_asistencia",
        "tiempo_promedio_duracion_sesion_bitacora": "tiempo_promedio_duracion_sesion_bitacora",
        "frecuencia_uso_guia_semanas_bitacora": "frecuencia_uso_guia_semanas_bitacora",
        "num_usos_guia_bitacora": "num_usos_guia_bitacora",
        "guias_usadas_bitacora": "guias_usadas_bitacora",
    }
    return (rename_dict,)


@app.cell
def _(raw_merged, rename_dict):
    final_df = raw_merged.rename(columns=rename_dict)
    final_df
    return (final_df,)


@app.cell
def _(final_df):
    for col in ['taller_1_asistencia', 'taller_2_asistencia', 'taller_2_senior_pro_asistencia', 'encuentro_colaborativo_1_asistencia']:
        final_df.loc[:, col] = final_df.loc[:, col].fillna("").str.lower().map({'sí': True}).fillna(False)

    final_df
    return


@app.cell
def _(final_df):
    final_df
    return


@app.cell
def _(final_df):
    final_df.to_csv("../data/limpieza/implementacion_limpio_coding_hub.csv", index=False)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
