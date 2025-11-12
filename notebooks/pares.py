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
    BASE_URL = "https://docs.google.com/spreadsheets/d/1QqNppXXmSonnTDs3uplG3DtgvWW3pEjExcOh2Q_xb4M/gviz/tq?tqx=out:csv&sheet="+ urllib.parse.quote_plus("Reporte de mentoría Coding Hubs")
    # Los nombres de los docentes están en otra hoja
    NOMBRES_URL = "https://docs.google.com/spreadsheets/d/1QqNppXXmSonnTDs3uplG3DtgvWW3pEjExcOh2Q_xb4M/gviz/tq?tqx=out:csv&sheet=group_xt7jo03"	
    ASISTENCIA_URL = "https://docs.google.com/spreadsheets/d/1T90vs6pBy12IpLvbxV4X-UhPUj2mDbxY/gviz/tq?tqx=out:csv&sheet=Asistencia%20CHM"
    BITACORA_AVANCES = "https://docs.google.com/spreadsheets/d/1VGDTDAdsqRcaWDWqn6gwvw2q-wY3gQEB7JilCXW2qh0/gviz/tq?tqx=out:csv"

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
def _():
    # revisar Bach Sebastián Castañeda Reyes duplicado
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
def _():
    # group duplicates in caracterizacion and desafio by aggregating numerical columns with sum and categorical columns with first
    # def aggregate_caracterizacion(df, id_col):
    #     agg_dict = {}
    #     for col in df.columns:
    #         if col == id_col:
    #             continue
    #         elif pd.api.types.is_numeric_dtype(df[col]):
    #             agg_dict[col] = "sum"
    #         else:
    #             agg_dict[col] = lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0]
    #     aggregated_df = df.groupby(id_col).agg(agg_dict).reset_index()
    #     # 1 hot encode "Línea del proyecto"
    #     df["Línea del proyecto"] = df["Línea del proyecto"].apply(
    #         lambda x: x.split(",")[0] if pd.notnull(x) else x
    #     )

    #     linea_dummies = pd.get_dummies(df["Línea del proyecto"], prefix="linea", dtype=int)
    #     linea_dummies[id_col] = df[id_col]
    #     linea_agg = linea_dummies.groupby(id_col).sum().reset_index()
    #     aggregated_df = pd.merge(aggregated_df, linea_agg, on=id_col, how="left")
    #     return aggregated_df


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


    # caracterizacion_agg = aggregate_caracterizacion(caracterizacion, id_cols["caracterizacion"])
    # desafio_agg = aggregate_desafio(desafio, id_cols["desafio"])
    return


@app.cell
def _(asistencia, base_completa, bitacora_final, id_cols, pd):
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
    for i, df in enumerate([base_completa, asistencia, bitacora_final]):
        id_col = id_cols[list(id_cols.keys())[i]]
        df[id_col] = df[id_col].astype(str)
        df[id_col] = df[id_col].str.strip()
        df[id_col] = df[id_col].str.replace("\.", "", regex=True)

    dataframes = [base_completa, asistencia, bitacora_final]
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
def _(caracterizacion, id_cols):
    caracterizacion[caracterizacion.duplicated(subset=[id_cols["caracterizacion"]], keep=False)]
    return


@app.cell
def _():
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
        "Codigo": "base",
        "Mentor": "base",
        "UG": "base",
        "Region": "base",
        "Departamento": "base",
        "Zona": "base",
        "Centro de interés": "base",
        "Género": "base",
        "Género.1": "base",
        "Nombre completo del par Experto": "base",
        "Identificación": "base",
        "De acuerdo con la asignatura que orienta, defina el área que aplica (STEM)": "base",
        "Categoría Junior o Senior 2024": "base",
        "Categoría Senior o Expert 2025": "base",
        "¿El grupo de estudiantes para 2025 es el mismo con el que se hizo la transferencia en el 2024?": "base",
        "Grados": "base",
        "Nivelación Junior - 1": "formacion",
        "Nivelación Junior - 2": "formacion",
        "Nivelación Junior - Total": "formacion",
        "Taller 1-Marzo": "formacion",
        "Nivelación Senior - Expert": "formacion",
        "Nivelaciones TOTAL": "formacion",
        "Total horas de mentoría ": "formacion",
        "Total mentorías ": "formacion",
        "Masterclass #1 ¡Potencia tu impacto en el aula! ": "formacion",
        "Taller2": "formacion",
        "Masterclass Hackeando el código": "formacion",
        "Encuentro colaborativo 1": "formacion",
        "Total Horas 2025": "formacion",
        "Horas 2024": "formacion",
        "iniciativa_Inventario de Biodiversidad": "desafio",
        "iniciativa_Medición de área en la escuela": "desafio",
        "iniciativa_Monitoreo de actividad física": "desafio",
        "Cantidad de estudiantes de sexo masculino": "desafio",
        "Cantidad de estudiantes de sexo femenino": "desafio",
        "Cantidad de estudiantes con discapacidad o trastornos del aprendizaje que participaron.": "desafio",
        "tiempo_promedio_duracion_sesion": "bitacora",
        "frecuencia_uso_guia_semanas": "bitacora",
        "num_usos_guia": "bitacora",
        "linea_1. Futuro sostenible": "codigo_en_accion",
        "linea_2. Experiencias Interactivas Educativas": "codigo_en_accion",
        "linea_3. Juegos Interactivos": "codigo_en_accion",
        "# Niñas presentando el proyecto en CA": "codigo_en_accion",
        "# Niños presentando el proyecto en CA": "codigo_en_accion",
    }
    return (cols_to_keep_by_source,)


@app.cell
def _(cols_to_keep_by_source, merged_df):
    raw_merged = merged_df[[col for col in merged_df.columns if col in cols_to_keep_by_source.keys()]]
    return (raw_merged,)


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
        "codigo_base": "codigo_base",
        "mentor_base": "mentor_base",
        "ug_base": "ug_base",
        "region_base": "region_base",
        "departamento_base": "departamento_base",
        "zona_base": "zona_base",
        "centro_de_interes_base": "centro_de_interes_base",
        "genero_base": "genero_rector_base",
        "nombre_completo_del_par_experto_base": "nombre_base",
        "identificacion_base": "identificacion_base",
        "genero1_base": "genero_par_experto_base",
        "de_acuerdo_con_la_asignatura_que_orienta_defina_el_area_que_aplica_stem_base": "area_stem_base",
        "categoria_junior_o_senior_2024_base": "categoria_2024_base",
        "categoria_senior_o_expert_2025_base": "categoria_2025_base",
        "el_grupo_de_estudiantes_para_2025_es_el_mismo_con_el_que_se_hizo_la_transferencia_en_el_2024_base": "mismo_grupo_2025_base",
        "grados_base": "grados_base",
        "nivelacion_junior__1_formacion": "nivelacion_junior_1_formacion",
        "nivelacion_junior__2_formacion": "nivelacion_junior_2_formacion",
        "nivelacion_junior__total_formacion": "nivelacion_junior_total_formacion",
        "taller_1marzo_formacion": "taller_1_formacion",
        "nivelacion_senior__expert_formacion": "nivelacion_senior_expert_formacion",
        "nivelaciones_total_formacion": "nivelaciones_total_formacion",
        "total_horas_de_mentoria_formacion": "total_horas_de_mentoria_formacion",
        "total_mentorias_formacion": "total_mentorias_formacion",
        "masterclass_1_potencia_tu_impacto_en_el_aula_formacion": "masterclass_1_formacion",
        "taller2_formacion": "taller_2_formacion",
        "masterclass_hackeando_el_codigo_formacion": "masterclass_2_formacion",
        "encuentro_colaborativo_1_formacion": "encuentro_colaborativo_1_formacion",
        "total_horas_2025_formacion": "total_horas_2025_formacion",
        "horas_2024_formacion": "horas_2024_formacion",
        "cantidad_de_estudiantes_de_sexo_masculino_desafio": "estudiantes_masculino_desafio",
        "cantidad_de_estudiantes_de_sexo_femenino_desafio": "estudiantes_femenino_desafio",
        "cantidad_de_estudiantes_con_discapacidad_o_trastornos_del_aprendizaje_que_participaron_desafio": "estudiantes_discapacidad_desafio",
        "iniciativa_inventario_de_biodiversidad_desafio": "iniciativa_biodiversidad_desafio",
        "iniciativa_medicion_de_area_en_la_escuela_desafio": "iniciativa_medicion_desafio",
        "iniciativa_monitoreo_de_actividad_fisica_desafio": "iniciativa_actividad_fisica_desafio",
        "frecuencia_uso_guia_semanas_bitacora": "frecuencia_uso_guia_semanas_bitacora",
        "num_usos_guia_bitacora": "num_usos_guia_bitacora",
        "_ninas_presentando_el_proyecto_en_ca_codigo_en_accion": "estudiantes_femenino_codigo_en_accion",
        "_ninos_presentando_el_proyecto_en_ca_codigo_en_accion": "estudiantes_masculino_codigo_en_accion",
        "linea_1_futuro_sostenible_codigo_en_accion": "linea_futuro_sostenible_codigo_en_accion",
        "linea_2_experiencias_interactivas_educativas_codigo_en_accion": "linea_experiencias_codigo_en_accion",
        "linea_3_juegos_interactivos_codigo_en_accion": "linea_juegos_codigo_en_accion",
    }
    return (rename_dict,)


@app.cell
def _(raw_merged, rename_dict):
    final_df = raw_merged.rename(columns=rename_dict)
    final_df
    return (final_df,)


@app.cell
def _(final_df):
    final_df["categoria_2025_base"] = (
        final_df["categoria_2025_base"]
        .str.lower()
        .map(
            {
                "grupo senior": "Grupo Junior",
                "grupo expert": "Grupo Senior",
            }
        )
    )
    final_df["genero_par_experto_base"] = (
        final_df["genero_par_experto_base"]
        .str.lower()
        .map({"hombre": "hombre", "mujer": "mujer"})
        .fillna("mujer")
    )
    final_df["area_stem_base"] = final_df["area_stem_base"].replace(
        {
            "Tecnología e informática": "Tecnología/Informática",
            "Preescocolar": "Primaria",
            "Tecnología e Informática, Matemáticas": "Tecnología/Informática",
        }
    )
    return


@app.cell
def _(final_df):
    final_df["area_stem_base"].value_counts()
    return


@app.cell
def _(final_df):
    final_df
    return


@app.cell
def _(final_df):
    final_df.to_csv("../data/limpieza/implementacion_limpio.csv", index=False)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
