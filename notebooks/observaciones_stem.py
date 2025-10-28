import marimo

__generated_with = "0.17.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import pandas as pd
    import re
    return pd, re


@app.cell
def _(pd):
    base = pd.read_csv("../data/limpieza/observaciones_stem.csv", skiprows=[0, 2])
    base2 = pd.read_csv("../data/limpieza/observaciones_stem_post.csv", skiprows=[0, 2])
    return base, base2


@app.cell
def _(base2):
    base2
    return


@app.cell
def _(base2):
    base3 = base2.rename(columns={
        "Seleccione la institución educativa y docente a observar - Mentor": "Nombre del mentor(a)",
        "Seleccione la institución educativa y docente a observar - Institución Educativa": "Nombre de la institución educativa",
        "Seleccione la institución educativa y docente a observar - Nombre del/la docente observado": "Nombre del/la docente observado(a)",
        "Asignatura - Selected Choice": "Asignatura",
        "Número de documento de docente observado": "Número de documento de docente observado/a",
    
    })

    base3.columns = [col.replace(" - Selected Choice", "") if "Tecnologías digitales" in col else col for col in base3.columns]
    return (base3,)


@app.cell
def _(base3):
    base3
    return


@app.cell
def _(base, base3):
    [c for c in base3.columns if c not in base.columns]
    return


@app.cell
def _(base, base3):
    [c for c in base.columns if c not in base3.columns]
    return


@app.cell
def _(base, base3, pd):
    df = pd.concat([base, base3], ignore_index=True)
    return (df,)


@app.cell
def _(df):
    df
    return


@app.cell
def _(df):
    df_1 = df.loc[(df['Finalizado'] == True) | (df['Progreso'] >= 80), :]
    return (df_1,)


@app.cell
def _(df_1):
    df_2 = df_1.loc[df_1['Tipo de respuesta'] != 'Survey Preview', :]
    return (df_2,)


@app.cell
def _(df_2, re):
    df_2.columns = [re.sub('\\s+', ' ', _col.strip().replace('\n', ' ')) for _col in df_2.columns]
    return


@app.cell
def _(df_2):
    df_2
    return


@app.cell
def _(df_2):
    df_3 = df_2.rename(columns={"Fecha del acompañamiento Indique la fecha en que realizó el acompañamiento en aula. Use el formato dd/mm/aaaa": "Fecha"})
    return (df_3,)


@app.cell
def _(df_3):
    df_3
    return


@app.cell
def _(df_3):
    # Keep only last 2 per docente (Número de documento de docente observado/a), assign the column Momento (Pre o Post)
    df_4 = df_3.sort_values(by=['Número de documento de docente observado/a', 'Fecha'], ascending=[True, False])
    df_4 = df_4.groupby('Número de documento de docente observado/a').head(2).reset_index(drop=True)
    df_4 = df_4.sort_values(by=['Número de documento de docente observado/a', 'Fecha'], ascending=[True, True])
    df_4['Momento'] = df_4.groupby('Número de documento de docente observado/a').cumcount().map({0: 'Pre', 1: 'Post'})
    return (df_4,)


@app.cell
def _(df_4):
    df_4['Momento'].value_counts()
    return


@app.cell
def _(df_4, pd, re):
    def concatenate_columns(df, start_col, end_col, target_col):
        """
        Concatena los valores de las columnas desde start_col hasta end_col
        y los asigna a la columna target_col en cada fila.

        Args:
            df (pandas.DataFrame): DataFrame de entrada.
            start_col (str): Nombre de la primera columna a concatenar.
            end_col (str): Nombre de la última columna a concatenar.
            target_col (str): Nombre de la columna donde se guardará la concatenación.

        Returns:
            pandas.DataFrame: DataFrame con la columna target_col actualizada.
        """
        df = df.copy()
        if start_col not in df.columns or end_col not in df.columns:
            raise ValueError('Alguna de las columnas especificadas no existe en el DataFrame.')
        start_idx = df.columns.get_loc(start_col)
        end_idx = df.columns.get_loc(end_col)
        columns_to_concat = df.columns[start_idx:end_idx + 1]
        df[target_col] = df[columns_to_concat].astype(str).agg(' '.join, axis=1).str.replace('nan', '', regex=False)
        return df
    df_5 = concatenate_columns(df_4, 'Nombre de la institución educativa', 'Nombre de la institución educativa.1', 'Colegio')

    df_6 = concatenate_columns(df_5, 'Nombre del/la docente observado(a)', 'Nombre del/la docente observado(a).9', 'Nombre de docente observado/a')



    def _clean_column_values(df, column_name):
        """  # Convierte los valores a string y concatena por fila, manejando NaN
        Limpia los valores de una columna eliminando espacios al principio y al final,
        y reemplazando múltiples espacios consecutivos por un solo espacio.

        Args:
    # Llamar a la función
            df (pandas.DataFrame): DataFrame de entrada.
            column_name (str): Nombre de la columna cuyos valores se van a limpiar.

        Returns:
    # Función para limpiar espacios innecesarios en los valores de una columna
            pandas.DataFrame: DataFrame con la columna limpiada.
        """
        if column_name not in df.columns:
            raise ValueError(f"La columna '{column_name}' no existe en el DataFrame.")
        df[column_name] = df[column_name].apply(lambda x: re.sub('\\s+', ' ', str(x).strip()) if pd.notnull(x) else x)
        return df
    df_6 = _clean_column_values(df_6, 'Colegio')

    def drop_column_range(df, start_col, end_col):
        """
        Elimina un rango de columnas consecutivas desde start_col hasta end_col (inclusive).

        Args:  # Verifica que la columna exista
            df (pandas.DataFrame): DataFrame de entrada.
            start_col (str): Nombre de la primera columna a eliminar.
            end_col (str): Nombre de la última columna a eliminar.
      # Aplica la limpieza a cada valor de la columna
        Returns:
            pandas.DataFrame: DataFrame con las columnas eliminadas.
        """
        if start_col not in df.columns or end_col not in df.columns:
            raise ValueError('Alguna de las columnas especificadas no existe en el DataFrame.')
        start_idx = df.columns.get_loc(start_col)
        end_idx = df.columns.get_loc(end_col)
        columns_to_drop = df.columns[start_idx:end_idx + 1].tolist()
        df_dropped = df.drop(columns=columns_to_drop)
        return df_dropped

    df_6 = drop_column_range(df_6, 'Nombre de la institución educativa', 'Nombre de la institución educativa.1')

    df_6 = drop_column_range(df_6, 'Nombre del/la docente observado(a)', 'Nombre del/la docente observado(a).9')

    df_6 = drop_column_range(df_6, 'Apellido del destinatario', 'Idioma del usuario')
    return (df_6,)


@app.cell
def _(df_6):
    copia = df_6.copy()
    return (copia,)


@app.cell
def _(copia):
    copia
    return


@app.cell
def _(df_6, pd, re):
    lista_instantaneas = df_6.columns[df_6.columns.str.contains('Qué está haciendo el/la docente ahora')].tolist()

    instantaneas = pd.DataFrame()
    _i = 1
    for instantanea in lista_instantaneas:
        print(instantanea)
        columna = df_6.columns.get_loc(instantanea)
        tablita = df_6.iloc[:, columna:columna + 18].copy()
        tablita = tablita.rename(columns={instantanea: '¿Qué está haciendo el/la docente ahora?'})
        tablita = tablita.merge(df_6.loc[:, ['ID de respuesta', 'Número de documento de docente observado/a', 'Nombre de docente observado/a', 'Indique sexo del docente', '¿El/la docente trabaja con una guía pedagógica?', 'Asignatura', 'Colegio', 'Momento']], left_index=True, right_index=True)
        tablita.loc[:, 'Número de instantánea'] = _i

        tablita.columns = [re.sub("\.+[0-9]+", "", col) for col in tablita.columns]
        instantaneas = pd.concat([instantaneas, tablita], axis=0)
        _i = _i + 1
    return (instantaneas,)


@app.cell
def _(instantaneas):
    instantaneas.columns.tolist()
    return


@app.cell
def _(instantaneas):
    nuevo_orden = ['ID de respuesta', 'Número de instantánea', 'Momento', 'Número de documento de docente observado/a', 'Nombre de docente observado/a', 'Indique sexo del docente', '¿El/la docente trabaja con una guía pedagógica?', 'Asignatura', 'Colegio', '¿Qué está haciendo el/la docente ahora?', 'Indique con quiénes está interactuando el/la docente', '¿Con quiénes está interactuando el/la docente?', '¿Están los/las estudiantes respondiendo las preguntas y/o participando en las discusiones?', '¿Están los/las estudiantes escuchando atentamente al docente?', '¿Están los/las estudiantes tomando nota de las explicaciones o discusiones?', '¿Están los/las estudiantes haciendo preguntas y/o pidiendo ayuda al docente?', '¿Están los/las estudiantes socializando su trabajo?', '¿Quiénes están socializando su trabajo?', '¿Están los/las estudiantes distraídos, haciendo indisciplina o mostrando de alguna otra manera que no están involucrados en las actividades que lidera el/la docente?', '¿Quiénes no están involucrados en las actividades que lidera el/la docente?', '¿Están haciendo uso de herramientas computacionales?', '¿Quiénes están haciendo uso de herramientas computacionales?', '¿Están los/las estudiantes trabajando individualmente?', '¿Están los/las estudiantes trabajando en parejas o grupos?', '¿Quiénes están ejerciendo roles de liderazgo en el trabajo en parejas o grupos?', '¿Están los/las estudiantes realizando las actividades por sí mismos, sin ayuda del docente?', 'Agregue cualquier comentario adicional, que sea relevante para entender lo que está sucediendo en el aula en este instante de la clase']
    instantaneas_1 = instantaneas.reindex(columns=nuevo_orden)
    return (instantaneas_1,)


@app.cell
def _(instantaneas_1):
    instantaneas_1
    return


@app.cell
def _():
    rename_dict = {
        'Fecha de inicio': 'fecha_inicio',
        'Fecha de finalización': 'fecha_fin',
        'Momento': 'momento',
        'Colegio': 'colegio',
        'Tipo de respuesta': 'tipo_respuesta',
        'Dirección IP': 'ip',
        'Progreso': 'progreso',
        'Duración (en segundos)': 'duracion_seg',
        'Finalizado': 'finalizado',
        'Fecha registrada': 'fecha_registro',
        'ID de respuesta': 'id_respuesta',
        'Latitud de la ubicación': 'latitud',
        'Longitud de la ubicación': 'longitud',
        'Canal de la distribución': 'canal_dist',
        'Idioma del usuario': 'idioma',
        'Fecha': 'fecha_acomp',
        'Hora de inicio de la clase (Formato Hora Militar) Indique la hora en la que inició la clase acompañada.': 'hora_inicio',
        'Nombre del mentor(a)': 'mentor',
        'Número de documento de docente observado/a': 'doc_docente',
        'Nombre de docente observado/a': 'nombre_docente',
        'Indique sexo del docente': 'sexo_docente',
        'Asignatura': 'asignatura',
        'Otra': 'otra_asignatura',
        'Grado': 'grado',
        '¿El/la docente trabaja con una guía pedagógica?': 'guia_pedagogica',
        '¿A qué grado corresponde la guía pedagógica empleada?': 'grado_guia',
        '¿Con qué número de guía se trabaja?': 'num_guia',
        '¿Con qué sesión de la guía se trabaja?': 'sesion_guia',
        'Tema de la clase Si no se trabaja con una guía pedagógica, por favor indique el tema de la clase': 'tema_clase',
        'Número de estudiantes en total Número entero sin puntos': 'total_estudiantes',
        'Número de estudiantes de sexo femenino Número entero sin puntos': 'est_femenino',
        'Número de estudiantes de sexo masculino Número entero sin puntos': 'est_masculino',
        'Duración estimada de la clase (horas y minutos) Por favor escriba el tiempo estimado que debe durar la clase observada en formato horas y minutos (00:00). Por ejemplo, si la clase dura 50 minutos, debe colocar 00:50.': 'duracion_clase',
        'Tecnologías digitales disponibles en la clase Elija todas las que apliquen - Computadores portátiles': 'tech_portatiles',
        'Tecnologías digitales disponibles en la clase Elija todas las que apliquen - Computadores de escritorio': 'tech_escritorio',
        'Tecnologías digitales disponibles en la clase Elija todas las que apliquen - Tabletas': 'tech_tabletas',
        'Tecnologías digitales disponibles en la clase Elija todas las que apliquen - Celulares': 'tech_celulares',
        'Tecnologías digitales disponibles en la clase Elija todas las que apliquen - Tarjetas micro:bit': 'tech_microbit',
        'Tecnologías digitales disponibles en la clase Elija todas las que apliquen - Video proyector (Video Beam)': 'tech_proyector',
        'Tecnologías digitales disponibles en la clase Elija todas las que apliquen - No se hizo uso de tecnologías digitales': 'tech_ninguna',
        'Tecnologías digitales disponibles en la clase Elija todas las que apliquen - Otra': 'tech_otra',
        'Timing - Primer clic': 'click_inicio',
        '¿Se promueven los procesos de metacognición y reflexión?': 'metacognicion',
        'Timing - Último clic': 'click_fin',
        'Timing - Envío de página': 'envio_pagina',
        'Timing - Recuento de clics': 'num_clics',
        'Al cierre de la clase ¿Se hace uso de algún tipo de gráfico de anclaje o memoria colectiva?': 'uso_grafico_anclaje',
        'Al inicio de la clase ¿Cuántos minutos transcurren entre la hora de inicio y el momento en que el docente empieza a gestionar el aula para empezar la clase? Escriba la cantidad de minutos en números enteros. Nota: Las actividades gestión inicial como llamar a lista o seguir rutinas de inicio establecidas, se consideran parte de la clase.': 'min_inicio_gestion',
        '¿Se presentan los objetivos de aprendizaje de la lección?': 'objetivos_aprend',
        '¿Se exploran los conocimientos previos de los estudiantes y su conexión con los temas de la lección?': 'conoc_previos',
        '¿Se presentan claramente los conceptos claves que serán usados en la lección?': 'conceptos_clave',
        'Actividades que promueven subhabilidades del pensamiento computacional ¿Se realizan actividades que promueven el uso de abstracción, descomposición, pensamiento lógico, pensamiento algorítmico, depuración o reconocimiento de patrones por parte de los/las estudiantes? Marque sí, si en la clase se realiza alguna actividad práctica de la asignatura que busque promover alguna de las 6 subhabilidades del pensamiento computacional. Ej. En clase de matemáticas se pide a los a los/las estudiantes que sigan una secuencia de pasos específica para realizar una tarea (algoritmia) o que analicen la solución de un ejercicio a fin de encontrar algún error que se haya cometido durante el proceso (depuración).': 'subhabilidades_comp',
        'Fomento de las subhabilidades del pensamiento computacional Responda todas las preguntas y luego, si es posible, describa brevemente la actividad que se realizó en el aula y que permitió promover el uso de las subhabilidades de pensamiento computacional. Descomposición: ¿Durante la clase se realizan actividades que requieren descomponer un problema o proceso en partes más pequeñas? Ej. Se pide a los estudiantes que planteen las actividades generales que desarrollarán en cada etapa del método científico, antes de proponer y ejecutar un experimento.': 'descomposicion',
        'Reconocimiento de patrones: ¿Los/las estudiantes realizan actividades para encontrar patrones y relaciones entre elementos? Ej. Se pide a los/las estudiantes analizar las células animal y vegeta y luego crear un listado de las características comunes y las diferencias entre ellas.': 'patrones',
        'Pensamiento algorítmico: ¿La/El docente invita a los/las estudiantes a organizar y/o ejecutar una secuencia de pasos para llevar a cabo una tarea? Ej. Se entrega a los/las estudiantes un laboratorio de física que requiere el desarrollo secuencial de ciertas actividades y se monitorea el avance.': 'algoritmico',
        'Depuración: ¿La/El docente solicita a los/las estudiantes identificar y corregir errores en la ejecución de un proceso o tarea? Ej. Se pide a los/las estudiantes intercambiar sus respuestas a un taller, marcar las fallas detectadas en el trabajo de sus compañeros y darles una recomendación escrita sobre lo que deben hacer para corregirlas.': 'depuracion',
        'Abstracción: ¿Se solicita a las/los estudiantes identificar la información relevante sobre un tema y/o sintetizarla? Ej. Se presenta un problema situacional matemático y se pide a los/las estudiantes leer atentamente el enunciado y plantear la ecuación para solucionarlo.': 'abstraccion',
        'Pensamiento lógico: ¿Se requiere que las/los estudiantes evalúen si se cumplen o no algunas condiciones y/o que realicen tareas o tomen decisiones a partir de los resultados de esta evaluación? Ej. Se presenta a los estudiantes un listado de hábitos diarios para que los analicen y determinen cuáles de ellos podrían afectar positiva o negativamente al sistema excretor.': 'logico',
        'Por favor, mencione las actividades que se realizaron en la clase acompañada, que a su juicio, contribuyen al desarrollo de una o más subhabilidades del pensamiento computacional de los/las estudiantes.': 'actividades_comp',
        'Prácticas de Pensamiento Computacional - parte 1 ¿Se observan prácticas de datos? Marque sí si en la clase se recopilan datos mediante generan o recolectan datos haciendo uso de herramientas computacionales, organización y clasificación de datos, análisis de los patrones existentes en los datos, o si se generan tablas o gráficos a partir de datos.': 'practicas_datos',
        'Prácticas de Datos ¿Durante la clase se realizan actividades para recolectar datos con herramientas tecnológicas? Ej. Se utiliza la micro:bit para recolectar datos de temperatura o se ingresan registros de observaciones en una hoja de cálculo para hacerles posterior análisis.': 'recoleccion_datos',
        '¿Los/las estudiantes realizan actividades para encontrar patrones y relaciones en conjuntos de datos? Ej. hacen conteo de frecuencias y las comparan, o hacen análisis de medias y tendencias.': 'patrones_datos',
        '¿La/El docente invita a los/las estudiantes a organizar y clasificar datos? Ej. Se pide a los/las estudiantes organizar los registros de observaciones de mayor a menor para identificar valores máximos y mínimos.': 'organizacion_datos',
        '¿La/El docente propone realizar tablas, graficas o diagramas con los datos? Ej. Se pide a los/las estudiantes hacer una gráfica de barras o crear un gráfico estadístico utilizando herramientas de una hoja de cálculo o de forma desconectada': 'visualizacion_datos',
        'Por favor, mencione las actividades asociadas a las prácticas de datos que se hayan desarrollado en la clase acompañada.': 'actividades_datos',
        'Prácticas de Pensamiento Computacional - parte 2 ¿Se observan prácticas de programación? Marque sí si en la clase se invita a los/las estudiantes a dividir un problema en otros más pequeños, si se crean instrucciones paso a paso para resolver un problema, si se codifica (en bloques o en texto), o si se prueban y evalúan los resultados de una posible solución a fin de plantear mejoras.': 'practicas_programacion',
        'Programación ¿Los/las estudiantes realizan actividades que implican descomponer los problemas en partes más pequeñas?': 'descomposicion_prog',
        '¿Los/las estudiantes crean instrucciones paso a paso para resolver un problema?': 'instrucciones_prog',
        '¿Los/las estudiantes utilizan un lenguaje de programación para codificar la solución a un problema?': 'codificacion',
        '¿Los/las estudiantes ejecutan, depuran, y hacen ajustes o mejoras a sus programas?': 'depuracion_prog',
        'Por favor, mencione las actividades asociadas a programación que se hayan desarrollado en la clase acompañada.': 'actividades_programacion',
        'Prácticas de Pensamiento Computacional - parte 3 ¿Se observa el uso de simulaciones computacionales? Marque sí si en la clase se hace uso de aplicaciones interactivas para entender o probar fenómenos científicos o del mundo físico, o si se discuten las limitaciones que tienen una simulación en contraste con las condiciones del mundo real.': 'simulaciones',
        'Simulaciones ¿Los/las estudiantes usan simuladores computacionales?': 'uso_simuladores',
        '¿La/El docente brinda espacios para que los/las estudiantes evalúen las simulaciones computacionales? Ej. se les invita a considerar si hay otros factores que pudieran agregarse o modificarse para hacer una simulación más precisa que lo que permite la herramienta.': 'evaluacion_simulaciones',
        'Por favor, mencione las actividades asociadas a simulaciones computacionales que se hayan desarrollado en la clase acompañada.': 'actividades_simulaciones',
        'Prácticas de Pensamiento Computacional - parte 4 ¿Se observan prácticas asociadas al Pensamiento Sistémico? Marque sí si en la clase los/las estudiantes logran identificar las partes de un todo que son cuantificables, si logran identificar las relaciones numéricas entre diferentes partes de un sistema, o si logran identificar cómo el incremento de un factor tiene impacto en el incremento o decremento de otro elemento del sistema.': 'pensamiento_sistemico',
        'Pensamiento sistémico ¿La/El docente realiza actividades que permiten a los/las estudiantes identificar datos numéricos? Ej. En una simulación sobre la cantidad de lluvia que cae en la ciudad, se invita a los/las estudiantes a considerar que las cifras se miden en milímetros cúbicos y corresponden a litros de agua por metro cuadrado': 'datos_numericos',
        '¿Los/las estudiantes identifican las relaciones numéricas dentro de un sistema? Ej. Los/las estudiantes analizan lo que sucede con los depredadores si se cambian los valores iniciales de las presas o del alimento disponible para estas, en una simulación presa-depredador.': 'relaciones_numericas',
        '¿Los/las estudiantes analizan cómo los cambios en las variables contribuyen a los resultados del sistema? Ej. Los estudiantes determinan qué pasa, repetición a repetición de una simulación, cuando se incrementa en 1 el número inicial de depredadores.': 'impacto_variables',
        'Por favor, mencione las actividades asociadas a pensamiento sistémico que se hayan desarrollado en la clase acompañada.': 'actividades_sistemico',
        'Sobre los conocimientos técnicos del docente ¿Se usa el vocabulario adecuado (terminología correcta) con relación al pensamiento computacional ? Diligencie esta parte durante la observación, y si es preciso, ajuste respuestas dadas previamente para responder mejor a la generalidad de lo observado': 'vocabulario_comp',
        '¿Se conectan los temas presentados con la vida diaria?': 'conexion_vida',
        '¿Sabe cómo resolver los problemas técnicos cuando fallan las herramientas computacionales en el aula?': 'resolucion_tecnica',
        'Si aplica, por favor, indique las dificultades técnicas que se presentaron durante la clase acompañada': 'dificultades_tecnicas',
        'Sobre las prácticas pedagógicas y de gestión de aula ¿Se preparó de forma previa el material requerido para la lección?': 'prep_material',
        '¿Se gestionan correctamente los materiales e instrumentos para el desarrollo de las actividades propuestas?': 'gestion_material',
        '¿Se valora el esfuerzo de los estudiantes para desarrollar las actividades propuestas?': 'valoracion_esfuerzo',
        '¿Se observa acompañamiento con estrategias de apoyo (aclaración de dudas, explicaciones, ejemplos adicionales, invitación a revisar notas de clases previas, etc) a los estudiantes durante el desarrollo de las actividades?': 'apoyo_estudiantes',
        'Prácticas en pro de la equidad de género Elija todas las opciones que representen lo que haya sucedido durante la clase acompañada. - Se corrigen comentarios y comportamientos sexistas': 'equidad_corrige_sexismo',
        'Prácticas en pro de la equidad de género Elija todas las opciones que representen lo que haya sucedido durante la clase acompañada. - Se estimula el liderazgo femenino': 'equidad_liderazgo_fem',
        'Prácticas en pro de la equidad de género Elija todas las opciones que representen lo que haya sucedido durante la clase acompañada. - Se realizan acciones afirmativas en términos de género': 'equidad_acciones_afirm',
        'Prácticas en pro de la equidad de género Elija todas las opciones que representen lo que haya sucedido durante la clase acompañada. - Se dedica tiempo de la clase a hacer reflexiones sobre equidad de género, por ejemplo, destacando los aportes de personajes masculinos y femeninos': 'equidad_reflexion',
        'Prácticas en pro de la equidad de género Elija todas las opciones que representen lo que haya sucedido durante la clase acompañada. - Se hace uso de lenguaje inclusivo, sin estereotipos de género, que promueva respeto por la diversidad': 'equidad_lenguaje_inc',
        'Prácticas en pro de la equidad de género Elija todas las opciones que representen lo que haya sucedido durante la clase acompañada. - No se observa ninguna práctica pedagógica en pro de la equidad de género': 'equidad_ninguna',
        'Prácticas en pro de la equidad de género Elija todas las opciones que representen lo que haya sucedido durante la clase acompañada. - Otra': 'equidad_otra',
        'Otra.2': 'equidad_otra_detalle',
        'Por favor, agregue cualquier otra información adicional que considere relevante para aclarar sus respuestas a la pregunta anterior': 'info_adicional_equidad',
        'Instantánea 1 - minuto 8 de la observación ¿Qué está haciendo el/la docente ahora? Indique cuál de las siguientes acciones es la principal que está realizando la/el docente en este instante.': 'accion_docente',
        'Indique con quiénes está interactuando el/la docente': 'interaccion',
        '¿Con quiénes está interactuando el/la docente?': 'interaccion_det',
        '¿Están los/las estudiantes respondiendo las preguntas y/o participando en las discusiones?': 'participacion',
        '¿Están los/las estudiantes escuchando atentamente al docente?': 'escucha',
        '¿Están los/las estudiantes tomando nota de las explicaciones o discusiones?': 'notas',
        '¿Están los/las estudiantes haciendo preguntas y/o pidiendo ayuda al docente?': 'preguntas',
        '¿Están los/las estudiantes socializando su trabajo?': 'socializacion',
        '¿Quiénes están socializando su trabajo?': 'socializacion_quien',
        '¿Están los/las estudiantes distraídos, haciendo indisciplina o mostrando de alguna otra manera que no están involucrados en las actividades que lidera el/la docente?': 'distraccion',
        '¿Quiénes no están involucrados en las actividades que lidera el/la docente?': 'no_involucrados',
        '¿Están haciendo uso de herramientas computacionales?': 'uso_tech',
        '¿Quiénes están haciendo uso de herramientas computacionales?': 'uso_tech_quien',
        '¿Están los/las estudiantes trabajando individualmente?': 'trabajo_ind',
        '¿Están los/las estudiantes trabajando en parejas o grupos?': 'trabajo_grupo',
        '¿Quiénes están ejerciendo roles de liderazgo en el trabajo en parejas o grupos?': 'liderazgo',
        '¿Están los/las estudiantes realizando las actividades por sí mismos, sin ayuda del docente?': 'autonomia',
        'Agregue cualquier comentario adicional, que sea relevante para entender lo que está sucediendo en el aula en este instante de la clase': 'comentarios',
        '¿Avanzar a la Instantánea 2?': 'avanzar',
        'Por favor, seleccione qué desea hacer.': 'accion_final',
        'Ciudadanía digital y comprensión y uso de la IA ¿Se observan prácticas que busquen fomentar habilidades de ciudadanía digital o promover la comprensión y el uso de la IA? Marque sí si en la clase los/las estudiantes aprenden conceptos básicos de Inteligencia Artificial (IA, aprendizaje automático, modelo, algoritmo de aprendizaje, datos de entrenamiento, predicción, sesgos, etc.), realizan actividades desconectadas o conectadas de IA, o analizan problemas de seguridad, éticos y de sesgos asociados al uso de la tecnología con o sin IA.': 'ia_practicas_presentes',
        'Ciudadanía digital y comprensión y uso de la IA Responda todas las preguntas y luego, si es posible, describa brevemente la actividad que se realizó durante la clase y que permitió evidenciar el acercamiento a la comprensión y uso de la Inteligencia Artificial por parte de los/las estudiantes. ¿Los/las estudiantes llevan a cabo alguna actividad desconectada para fortalecer su comprensión de conceptos de IA? Ejemplo: analizar aplicaciones u objetos y decidir si corresponden o no a ejemplos de IA, etiquetar imágenes y luego discutir sesgos en la interpretación de estas, determinar los datos de entrenamiento requeridos para alguna toma de decisión o predicción, etc).': 'ia_act_desconectada_desc',
        '¿Los/las estudiantes usan herramientas de IA generativa? Ejemplo: hacen una consulta a un modelo grande de lenguaje como ChatGPT, crean imágenes mediante un prompt en Copilot o Meta, generan un video con Canva, etc.': 'ia_herramientas_generativas',
        '¿Los/las estudiantes entrenan modelos de IA o hacen uso de uno de estos modelos? Ejemplo: crean un modelo de reconocimiento de imágenes con TeachableMachine, crean un modelo de reconocimiento de texto con https://machinelearningforkids.co.uk/, vinculan un modelo de IA creado a un programa de Scratch o vinculan un proyecto en MakeCode con un modelo de IA usando https://makeairobots.com/, etc.': 'ia_entrenamiento_modelos',
        '¿Se realizan discusiones críticas sobre perspectiva, sesgos algorítmicos, o la necesidad de que población diversa contribuya en proyectos computacionales? Ejemplo: se analizan las fallas de un modelo de IA para reconocer una imagen, se discute por qué un modelo de IA genera imágenes que representan un estereotipo, se comentan las ventajas de que varias personas distintas colaboren para entrenar un modelo de IA, etc': 'ia_discusiones_criticas',
        '¿Se discuten o promueven buenas prácticas de seguridad digital (ej. la protección de datos, contraseñas, y el uso seguro de internet)?': 'ia_seguridad_digital',
        '¿Se abordan aspectos éticos del uso de tecnologías digitales (ej. respeto a la privacidad, uso responsable de la información)?': 'ia_etica_tecnologia',
        'Por favor, mencione las actividades asociadas a ciudadanía digital (seguridad informática, uso ético de tecnologías, equidad ) y/o de IA que se hayan desarrollado en la clase acompañada.': 'ia_actividades_desc',
        'Ciudadanía digital y comprensión y uso de la IA ¿Se observan prácticas que busquen fomentar habilidades de ciudadanía digital o promover la comprensión y el uso de la IA? Marque sí si en la clase los/las estudiantes aprenden conceptos básicos de Inteligencia Artificial (IA, aprendizaje automático, modelo, algoritmo de aprendizaje, datos de entrenamiento, predicción, sesgos, etc.), realizan actividades desconectadas o conectadas de IA, o analizan problemas de seguridad, éticos y de sesgos asociados al uso de la tecnología con o sin IA.': 'ciudadania_ia_presentes',
    'Ciudadanía digital y comprensión y uso de la IA Responda todas las preguntas y luego, si es posible, describa brevemente la actividad que se realizó durante la clase y que permitió evidenciar el acercamiento a la comprensión y uso de la Inteligencia Artificial por parte de los/las estudiantes. ¿Los/las estudiantes llevan a cabo alguna actividad desconectada para fortalecer su comprensión de conceptos de IA? Ejemplo: analizar aplicaciones u objetos y decidir si corresponden o no a ejemplos de IA, etiquetar imágenes y luego discutir sesgos en la interpretación de estas, determinar los datos de entrenamiento requeridos para alguna toma de decisión o predicción, etc).': 'ciudadania_ia_desconectada',
    '¿Los/las estudiantes usan herramientas de IA generativa? Ejemplo: hacen una consulta a un modelo grande de lenguaje como ChatGPT, crean imágenes mediante un prompt en Copilot o Meta, generan un video con Canva, etc.': 'ciudadania_ia_herramientas',
    '¿Los/las estudiantes entrenan modelos de IA o hacen uso de uno de estos modelos? Ejemplo: crean un modelo de reconocimiento de imágenes con TeachableMachine, crean un modelo de reconocimiento de texto con https://machinelearningforkids.co.uk/, vinculan un modelo de IA creado a un programa de Scratch o vinculan un proyecto en MakeCode con un modelo de IA usando https://makeairobots.com/, etc.': 'ciudadania_ia_modelos',
    '¿Se realizan discusiones críticas sobre perspectiva, sesgos algorítmicos, o la necesidad de que población diversa contribuya en proyectos computacionales? Ejemplo: se analizan las fallas de un modelo de IA para reconocer una imagen, se discute por qué un modelo de IA genera imágenes que representan un estereotipo, se comentan las ventajas de que varias personas distintas colaboren para entrenar un modelo de IA, etc': 'ciudadania_ia_discusiones',
    '¿Se discuten o promueven buenas prácticas de seguridad digital (ej. la protección de datos, contraseñas, y el uso seguro de internet)?': 'ciudadania_ia_seguridad',
    '¿Se abordan aspectos éticos del uso de tecnologías digitales (ej. respeto a la privacidad, uso responsable de la información)?': 'ciudadania_ia_etica',
    'Por favor, mencione las actividades asociadas a ciudadanía digital (seguridad informática, uso ético de tecnologías, equidad ) y/o de IA que se hayan desarrollado en la clase acompañada.': 'ciudadania_ia_actividades',
    }
    return (rename_dict,)


@app.cell
def _(df_6, rename_dict):
    for kesy in rename_dict.keys():
        if kesy not in df_6.columns:
            print(kesy)
    print("*"*10)

    for col in df_6.columns:
        if col not in rename_dict:
            print(col)
    return


@app.function
def rename_columns(df, rename_dict):
    """
    Renombra las columnas de un DataFrame usando un diccionario.
    - Ignora claves en rename_dict que no coincidan con columnas existentes.
    - Mantiene los nombres originales si no hay nuevo nombre en rename_dict.

    Args:
        df (pandas.DataFrame): DataFrame cuyas columnas se van a renombrar.
        rename_dict (dict): Diccionario con {nombre_actual: nuevo_nombre}.

    Returns:
        pandas.DataFrame: DataFrame con las columnas renombradas.
    """
    df_renamed = df.copy()  # Crea una copia del DataFrame para evitar modificar el original
    current_columns = df_renamed.columns.tolist()
    safe_rename_dict = {_col: rename_dict[_col] for _col in current_columns if _col in rename_dict}
    df_renamed = df_renamed.rename(columns=safe_rename_dict)  # Obtiene las columnas actuales del DataFrame
    return df_renamed


@app.cell
def _(df_6):
    # Obtiene todas las columnas hasta la columna de interés
    columnas_hasta_instantanea = df_6.columns[:df_6.columns.get_loc('Instantánea 1 - minuto 8 de la observación ¿Qué está haciendo el/la docente ahora? Indique cuál de las siguientes acciones es la principal que está realizando la/el docente en este instante.') + 1]

     # Crea la lista final de columnas a seleccionar
    columnas_a_seleccionar = columnas_hasta_instantanea.tolist()
    columnas_a_seleccionar = columnas_a_seleccionar + ['Momento', '¿Se promueven los procesos de metacognición y reflexión?', 'Al cierre de la clase ¿Se hace uso de algún tipo de gráfico de anclaje o memoria colectiva?', 'Nombre de docente observado/a', 'Colegio']
    # Selecciona las columnas para crear Obs_generales
    obs_generales = df_6.loc[:, columnas_a_seleccionar].copy()
    return (obs_generales,)


@app.cell
def _(instantaneas_1, obs_generales, rename_dict):
    # Llama a la función
    instantaneas_2 = rename_columns(instantaneas_1, rename_dict)
    obs_generales_1 = rename_columns(obs_generales, rename_dict)
    return instantaneas_2, obs_generales_1


@app.cell
def _(obs_generales_1):
    [c for c in obs_generales_1.columns if 'colegio' in c.lower()]
    return


@app.cell
def _(instantaneas_2):
    instantaneas_2
    return


@app.cell
def _(instantaneas_2, obs_generales_1):
    instantaneas_3 = instantaneas_2.replace(['nan', 'NaN', 'N/A'], '', regex=False)
    obs_generales_2 = obs_generales_1.replace(['nan', 'NaN', 'N/A'], '', regex=False)
    return instantaneas_3, obs_generales_2


@app.cell
def _():
    nuevo_orden_1 = ['fecha_inicio', 'fecha_fin', 'visita', 'momento', 'fecha_acomp', 'fecha_registro', 'hora_inicio', 'duracion_clase', 'duracion_seg', 'doc_docente', 'nombre_docente', 'sexo_docente', 'colegio', 'tipo_respuesta', 'id_respuesta', 'ip', 'progreso', 'finalizado', 'latitud', 'longitud', 'canal_dist', 'idioma', 'asignatura', 'otra_asignatura', 'grado', 'guia_pedagogica', 'grado_guia', 'num_guia', 'sesion_guia', 'tema_clase', 'total_estudiantes', 'est_femenino', 'est_masculino', 'tech_portatiles', 'tech_escritorio', 'tech_tabletas', 'tech_celulares', 'tech_microprocesadores', 'tech_componentes_externos', 'tech_robots', 'tech_sin_uso', 'tech_otra', 'tech_otra_detalle', 'click_inicio', 'click_fin', 'envio_pagina', 'num_clics', 'min_inicio_gestion', 'objetivos_aprend', 'conoc_previos', 'conceptos_clave', 'act_desconectada_presente', 'act_desconectada_desc', 'act_desconectada_participantes', 'razon_dificultad_instrucciones', 'razon_dificultad_concepto', 'razon_dificultad_narrativa', 'razon_dificultad_otra', 'razon_dificultad_otra_detalle', 'act_desconectada_compartir', 'act_desconectada_cierre', 'act_desconectada_eficacia', 'act_desconectada_comentarios', 'act_conectada_presente', 'act_conectada_dispositivos', 'act_conectada_microprocesadores', 'act_conectada_distribucion', 'act_conectada_software', 'act_conectada_herramientas', 'act_conectada_conectividad', 'act_conectada_predecir', 'act_conectada_ejecutar_replicar', 'act_conectada_ejecutar_entregar', 'act_conectada_investigar_libre', 'act_conectada_investigar_guiada', 'act_conectada_investigar_compartir', 'act_conectada_explicacion', 'act_conectada_modificar_ind', 'act_conectada_modificar_docente', 'act_conectada_modificar_apoyo', 'act_conectada_hacer_ind', 'act_conectada_hacer_apoyo', 'act_conectada_hacer_replicar', 'act_conectada_proyecto_fisico', 'act_conectada_comentarios', 'estrategia_pares', 'estrategia_parsons', 'estrategia_vivo', 'estrategia_lectura', 'estrategia_evaluacion', 'estrategia_proyectos', 'estrategia_diseno', 'estrategia_tinkering', 'estrategia_ninguna', 'estrategia_otra', 'estrategia_otra_detalle', 'estudiantes_solucion', 'estudiantes_instrucciones', 'razon_inicio_atencion', 'razon_inicio_claras', 'razon_inicio_modelo_doc', 'razon_inicio_modelo_est', 'razon_inicio_otra', 'razon_inicio_otra_detalle', 'razon_no_inicio_confusas', 'razon_no_inicio_sin_instrucciones', 'razon_no_inicio_sin_modelo', 'razon_no_inicio_otra', 'razon_no_inicio_otra_detalle', 'promocion_comp', 'vocabulario_comp', 'conexion_vida', 'resolucion_tecnica', 'dificultades_tecnicas', 'prep_material', 'gestion_material', 'valoracion_esfuerzo', 'apoyo_estudiantes', 'equidad_corrige_sexismo', 'equidad_liderazgo_fem', 'equidad_acciones_afirm', 'equidad_reflexion', 'equidad_ninguna', 'equidad_otra', 'equidad_otra_detalle', 'info_adicional_equidad', 'metacognicion', 'uso_grafico_anclaje']  # Metadatos generales y fechas  # Identificación y datos del docente  # Respuesta y progreso  # Ubicación y distribución  # Detalles de la clase  # Tecnologías digitales  # Interacciones y timing  # Actividades desconectadas  # Actividades conectadas  # Estrategias pedagógicas  # Evaluación de estudiantes  # Promoción y competencias  # Gestión y equidad
    return (nuevo_orden_1,)


@app.cell
def _(nuevo_orden_1, obs_generales_2):
    obs_generales_3 = obs_generales_2.reindex(columns=nuevo_orden_1)
    return (obs_generales_3,)


@app.cell
def _():
    ['Está explicando conceptos de pensamiento computacional y/o programación',
           'Está haciendo preguntas a toda la clase',
           'Está dando instrucciones para el desarrollo de una actividad',
           'Está monitoreando o supervisando el trabajo de los/las estudiantes, sin intervenir',
           'Está copiando en el tablero sin hablar',
           'Está escuchando las intervenciones o presentaciones de los/las estudiantes',
           'Está retroalimentando el trabajo realizado por los/las estudiantes (en parejas o grupos)',
           'Está resolviendo problemas técnicos (uso del proyector, problemas con el computador, etc)',
           'Está haciendo actividades de gestión de aula (disciplina, atención de los/las estudiantes, etc)',
           'Está explicando conceptos relevantes para la lección, pero no asociados al pensamiento computacional o la programación',
           'Está presente físicamente, pero desconectado(a) de las actividades',
           'Está hablando de temas no relacionados con la clase',
           'Está ausente físicamente',
           'Está dando instrucciones para la próxima clase'],

    docente_actividades = {
        "Instrucción docente": [
            {"full_name": "Está explicando conceptos de pensamiento computacional y/o programación", "clean_name": "Conceptos de PC"},
            {"full_name": "Está explicando conceptos relevantes para la lección, pero no asociados al pensamiento computacional o la programación", "clean_name": "Conceptos relevantes, no de PC"},
            {"full_name": "Está dando instrucciones para el desarrollo de una actividad", "clean_name": "Dar instrucciones"},
            {"full_name": "Está dando una explicación temática", "clean_name": "Explicar temas"},
            {"full_name": "Está copiando en el tablero sin hablar", "clean_name": "Copiar en tablero"},
        ],
        "Interacción": [
            {"full_name": "Está escuchando las intervenciones o presentaciones de los/las estudiantes", "clean_name": "Escuchar intervenciones"},
            {"full_name": "Está monitoreando o supervisando el trabajo de los/las estudiantes, sin intervenir", "clean_name": "Supervisar trabajos"},
            {"full_name": "Está haciendo preguntas a toda la clase", "clean_name": "Hacer preguntas"},
            {"full_name": "Está retroalimentando el trabajo realizado por los/las estudiantes (en parejas o grupos)", "clean_name": "Retroalimentar trabajos"},
            {"full_name": "Está aclarando dudas no relacionadas con instrucciones de actividades", "clean_name": "Aclarar dudas"},
        ],
        "Gestión de aula": [
            {"full_name": "Está haciendo actividades de gestión de aula (disciplina, atención de los/las estudiantes, etc)", "clean_name": "Gestión de aula"},
            {"full_name": "Está resolviendo problemas técnicos (uso del proyector, problemas con el computador, etc)", "clean_name": "Resolver problemas técnicos"},
        ],
        "Tareas no docente": [
            {"full_name": "Está ausente físicamente", "clean_name": "Ausente físicamente"},
            {"full_name": "Está presente físicamente, pero desconectado(a) de las actividades", "clean_name": "Desconectado de actividades"},
            {"full_name": "Está hablando de temas no relacionados con la clase", "clean_name": "Temas no relacionados"},
            {"full_name": "Está dando instrucciones para la próxima clase", "clean_name": "Instrucciones próxima clase"},
        ],
    }

    actividad_map = {x["full_name"]: {"clean": x["clean_name"], "cat": categoria} for categoria, valores in docente_actividades.items() for x in valores}
    return actividad_map, docente_actividades


@app.cell
def _(docente_actividades):
    docente_actividades.items()
    return


@app.cell
def _(obs_generales_3):
    obs_generales_3
    return


@app.cell
def _(actividad_map, instantaneas_3, pd):
    # Mapeo instantáneas
    def map_actividad(actividad):
        if actividad in actividad_map:
            return (actividad_map[actividad]['clean'], actividad_map[actividad]['cat'])
        else:
            return (actividad, None)
    instantaneas_3[['accion_docente_clean', 'accion_docente_cat']] = instantaneas_3['¿Qué está haciendo el/la docente ahora?'].apply(lambda x: pd.Series(map_actividad(x)))
    return


@app.cell
def _(instantaneas_3):
    instantaneas_3
    return


@app.cell
def _(instantaneas_3):
    # Asignar 'momento' como 'Pre' para la primera visita y 'Post' para la segunda visita por cada docente
    # instantaneas_4 = instantaneas_3.sort_values(['doc_docente', 'visita'])
    # instantaneas_4['visita_order'] = instantaneas_4.groupby('doc_docente')['visita'].rank(method='dense').astype('Int64')
    # instantaneas_4['momento'] = instantaneas_4['visita_order'].map({1: 'Pre', 2: 'Post'})
    # instantaneas_4 = instantaneas_4.drop(columns=['visita_order'])
    # Mostrar los primeros registros para verificar
    instantaneas_4 = instantaneas_3.copy()
    instantaneas_4
    return (instantaneas_4,)


@app.cell
def _(obs_generales_3):
    obs_generales_3[obs_generales_3['id_respuesta'] == 'R_7fVs1D5VROLjBfd']
    return


@app.cell
def _():
    import plotly.express as px
    return (px,)


@app.cell
def _(instantaneas_4, px):
    df_7 = instantaneas_4.dropna(subset=['accion_docente_cat'])
    _df_counts = df_7.groupby(['momento', 'Número de instantánea', 'accion_docente_cat']).size().reset_index(name='count')
    _df_counts['percent'] = _df_counts.groupby(['momento', 'Número de instantánea'])['count'].apply(lambda x: 100 * x / x.sum()).reset_index(drop=True)
    for _momento in _df_counts['momento'].unique():
        df_momento = _df_counts[_df_counts['momento'] == _momento]
        _fig = px.line(df_momento, x='Número de instantánea', y='percent', color='accion_docente_cat', markers=True, title=f'Distribución porcentual de categorías - {_momento}', labels={'percent': 'Porcentaje (%)', 'Número de instantánea': 'Número de instantánea'})
        _fig.update_layout(yaxis=dict(range=[0, 100]), legend_title_text='Categoría', template='plotly_white')
        _fig.show()
    return


@app.cell
def _(instantaneas_4, pd, px):
    df_heat = instantaneas_4.copy()
    df_heat['Número de instantánea'] = pd.to_numeric(df_heat['Número de instantánea'], errors='coerce')
    df_heat = df_heat.dropna(subset=['Número de instantánea', 'accion_docente_clean'])
    _df_counts = df_heat.groupby(['momento', 'Número de instantánea', 'accion_docente_clean']).size().reset_index(name='count')
    _df_counts['percent'] = _df_counts.groupby(['momento', 'Número de instantánea'])['count'].apply(lambda x: 100 * x / x.sum()).reset_index(drop=True)
    ordered_actions = _df_counts['accion_docente_clean'].value_counts().index.tolist()
    _df_counts['accion_docente_clean'] = pd.Categorical(_df_counts['accion_docente_clean'], categories=ordered_actions, ordered=True)
    pivot_pre = _df_counts[_df_counts['momento'] == 'Pre'].pivot(index='accion_docente_clean', columns='Número de instantánea', values='percent')
    pivot_post = _df_counts[_df_counts['momento'] == 'Post'].pivot(index='accion_docente_clean', columns='Número de instantánea', values='percent')
    color_scale = 'Purples'
    pivot_pre = pivot_pre.fillna(0)
    pivot_post = pivot_post.fillna(0)
    for _momento in ['Pre', 'Post']:
        if _momento == 'Pre':
            data = pivot_pre
        else:
            data = pivot_post
        _fig = px.imshow(data, labels=dict(x='Número de instantánea', y='Acción del docente', color='Porcentaje'), x=data.columns, color_continuous_scale=color_scale, text_auto='.1f')
        _fig.update_layout(title=f'¿Qué está haciendo el docente? (Distribución porcentual por instantánea) - {_momento}', height=850, margin=dict(l=280, r=40, t=80, b=40), coloraxis_colorbar=dict(title='Porcentaje'), template='plotly_white')
        _fig.update_traces(texttemplate='%{z:0.1f}%', hovertemplate='Acción: %{y}<br>Momento/Inst: %{x}<br>%{z:.1f}%<extra></extra>', textfont=dict(size=8))
        _fig.update_yaxes(autorange='reversed')
        _fig.show()
    return


@app.cell
def _(instantaneas_4, obs_generales_3):
    obs_generales_3.to_csv('../data/limpieza/obs_generales_stem_limpio.csv', index=False)
    instantaneas_4.to_csv('../data/limpieza/instantaneas_stem_limpio.csv', index=False)
    return


@app.cell
def _(obs_generales_3, pd):
    import plotly.graph_objects as go
    objetivos_map = {'objetivos_aprend': {'positive_words': ['sí'], 'negative_words': ['no'], 'clean_name': 'Objetivos de Aprendizaje', 'category': 'Inicio de clase'}, 'conoc_previos': {'positive_words': ['sí'], 'negative_words': ['no'], 'clean_name': 'Conocimientos Previos', 'category': 'Inicio de clase'}, 'conceptos_clave': {'positive_words': ['sí'], 'negative_words': ['no'], 'clean_name': 'Conceptos Clave', 'category': 'Inicio de clase'}, 'vocabulario_comp': {'positive_words': ['sí'], 'negative_words': ['no'], 'clean_name': 'Vocabulario adecuado', 'category': 'Conocimientos técnicos'}, 'conexion_vida': {'positive_words': ['sí'], 'negative_words': ['no'], 'clean_name': 'Conexión con la vida diaria', 'category': 'Conocimientos técnicos'}, 'prep_material': {'positive_words': ['sí'], 'negative_words': ['no'], 'clean_name': 'Preparación de materiales', 'category': 'Prácticas pedagógicas y de gestión de aula'}, 'gestion_material': {'positive_words': ['sí'], 'negative_words': ['no'], 'clean_name': 'Gestión de materiales', 'category': 'Prácticas pedagógicas y de gestión de aula'}, 'valoracion_esfuerzo': {'positive_words': ['sí'], 'negative_words': ['no'], 'clean_name': 'Valoración del esfuerzo', 'category': 'Prácticas pedagógicas y de gestión de aula'}, 'apoyo_estudiantes': {'positive_words': ['sí'], 'negative_words': ['no'], 'clean_name': 'Apoyo a estudiantes', 'category': 'Prácticas pedagógicas y de gestión de aula'}, 'metacognicion': {'positive_words': ['sí'], 'negative_words': ['no'], 'clean_name': 'Metacognición y reflexión', 'category': 'Cierre de clase'}, 'uso_grafico_anclaje': {'positive_words': ['sí'], 'negative_words': ['no'], 'clean_name': 'Uso de gráfico de anclaje o memoria colectiva', 'category': 'Cierre de clase'}}
    clean_objetivos = obs_generales_3.copy()

    def _clean_column_values(value, positive_words, negative_words):
        if pd.isna(value):
            return 'No'
        value = value.lower().strip()
        if any((pos_word in value for pos_word in positive_words)):
            return 'Sí'
        if any((neg_word in value for neg_word in negative_words)):
            return 'No'
        return 'No'
    for _col, _mapping in objetivos_map.items():
        clean_objetivos[_col] = clean_objetivos[_col].str.lower().str.strip()
        clean_objetivos[_col] = clean_objetivos[_col].fillna('No')
        clean_objetivos[_col] = clean_objetivos[_col].apply(lambda x: _clean_column_values(x, _mapping['positive_words'], _mapping['negative_words']))
    return clean_objetivos, go, objetivos_map


@app.cell
def _(clean_objetivos, go, objetivos_map):
    for _col, _mapping in objetivos_map.items():
        for _momento in ['Pre', 'Post']:
            _mask = clean_objetivos['momento'] == _momento
            pos_count = (clean_objetivos.loc[_mask, _col] == 'Sí').sum()
            neg_count = (clean_objetivos.loc[_mask, _col] == 'No').sum()
            total = pos_count + neg_count
            percentage = pos_count / total * 100 if total > 0 else 0
            key = 'pre_percentage' if _momento == 'Pre' else 'post_percentage'
            objetivos_map[_col][key] = percentage
    categories = []
    # Data grouped by section
    # groups = {
    #     'Inicio de clase': [
    #         ('Objetivos de aprendizaje', 42, 89),
    #         ('Conocimientos previos', 62, 88),
    #         ('Conceptos clave', 70, 91)
    #     ],
    #     'Conocimientos técnicos': [
    #         ('Vocabulario adecuado', 73, 91),
    #         ('Conexión vida diaria', 42, 80)
    pretest = []
    #     'Prácticas pedagógicas y de gestión de aula': [
    #         ('Material preparado', 56, 86),
    #         ('Gestión de materiales', 58, 82),
    #         ('Valoración esfuerzo', 59, 80),
    #         ('Estrategias de apoyo', 59, 74)
    posttest = []
    #     'Cierre de la clase': [
    #         ('Gráficos de anclaje', 8, 36),
    #         ('Metacognición', 27, 74)
    #     ]
    # }
    section_starts = []
    # Flatten data for plotting and record section starts
    sections = []
    for _col, _mapping in objetivos_map.items():
        sections.append(_mapping['category'])
        categories.append(_mapping['clean_name'])
        pretest.append(_mapping['pre_percentage'])
        posttest.append(_mapping['post_percentage'])
    # for section, items in groups.items():
    #     section_starts.append(len(categories))
    #     for cat, pre, post in items:
    #         sections.append(section)
    #         categories.append(cat)
    #         pretest.append(pre)
    #         posttest.append(post)
        if _mapping['category'] not in section_starts:
            section_starts.append(len(categories) - 1)
    _fig = go.Figure()
    for _i in range(len(categories)):
        _fig.add_trace(go.Scatter(x=[pretest[_i], posttest[_i]], y=[[sections[_i], sections[_i]], [categories[_i], categories[_i]]], mode='markers+lines', line=dict(color='lightgray', width=2), showlegend=False))
    full_sections = []
    for section in sections:
        full_sections.append(section)
        full_sections.append(section)
    _fig.add_trace(go.Scatter(x=pretest, y=[sections, categories], mode='markers+text', name='Pretest', marker=dict(color='cornflowerblue', size=10), text=[f'{v:.1f}%' for v in pretest], textposition='middle left'))
    _fig.add_trace(go.Scatter(x=posttest, y=[sections, categories], mode='markers+text', name='Postest', marker=dict(color='orchid', size=10), text=[f'{v:.1f}%' for v in posttest], textposition='middle right'))
    _fig.update_layout(title='Porcentaje de docentes observados en cada práctica', xaxis_title='Docentes observados', xaxis=dict(range=[0, 100], ticksuffix='%'), template='simple_white', height=700, yaxis_title='', yaxis=dict(autorange='reversed'), margin=dict(l=300, r=20, t=60, b=50), legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
    # Create figure
    # Add connecting lines
    # Add pretest and posttest markers + labels
    # Layout: reverse y to keep provided order top->bottom, increase left margin
    _fig.show()  # keep categories in the order we defined
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
