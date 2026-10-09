# Limpieza de datos — Instrumento CHM 2026

Este documento explica, paso a paso, cómo se construyó el pipeline de
limpieza en `prueba.ipynb` para el instrumento **CHM (Coding Hub Masters)
2026**, replicando la metodología usada previamente en
`01_limpieza_datos_EC_2026.py` (instrumento "EC", Encuentros Colaborativos).

## 1. Punto de partida

- Archivo de entrada: `input/Instrumento+EC+CHM+2026_25+de+agosto+de+2026_10.40.xlsx`
  (export de Qualtrics, formato xlsx, 1 sola hoja, 13 respuestas al momento
  de este trabajo).
- Pipeline de referencia: `01_limpieza_datos_EC_2026.py`, un notebook
  **marimo** que procesaba dos CSV de Qualtrics (`EC1_2026.csv`,
  `EC2_2026.csv`, hoy inexistentes) y producía 3 CSV de salida (momentos,
  instantáneas, asistentes).
- Salida de referencia (forma esperada): `ejemplos_output/momentos_EC2_CHM.xlsx`.
- Notebook de trabajo: `prueba.ipynb` (Jupyter estándar, no marimo).

## 2. Investigación previa (antes de escribir código)

Antes de tocar el notebook se inspeccionó el archivo `.xlsx` nuevo con
`zipfile`/XML puro (sin `pandas`, porque `openpyxl` no estaba instalado
todavía) para verificar si la estructura calzaba con lo que
`01_limpieza_datos_EC_2026.py` esperaba. Hallazgos clave:

- El archivo mantiene el formato típico de exportación Qualtrics de 3 filas
  de cabecera: fila 0 = códigos de variable, fila 1 = texto de la pregunta
  (el header real), fila 2 = metadato `ImportId` (se descarta).
- El texto ancla (`ANCHOR`) que marca el inicio de cada bloque de "momento"
  aparece exactamente 5 veces, con bloques de **408 columnas** cada uno — la
  misma lógica de detección de bloques del script EC funciona sin cambios.
- Hay **486 columnas** con prefijo `I1.`…`I18.` (instantáneas), igual que en
  EC.
- Los 11 códigos de roster que usa `ROSTER_CODES` en el script EC
  (`Q411_1, Q445_1, Q412_1, Q413_1, Q417_1, Q422_1, Q437_1, Q438_1, Q439_1,
  Q440_1, Q265_1`) están presentes, en las mismas posiciones, con el mismo
  formato de celda `código\tNombre\tID` — con datos reales (no de prueba).

Diferencias estructurales encontradas frente a EC:

- **No hay separación EC1/EC2**: es un único archivo, sin columna de
  "Evento".
- **No existe `Q5_1`** (institución en texto libre, como en EC). En su
  lugar: `Q4` = "Nombre del Coding Hub" (equivalente al nodo), y
  `Q5_4…Q5_25` = casillas de selección múltiple, una por institución
  acompañada.
- El script EC filtraba las respuestas contra una lista de IDs válidos
  publicada en Google Sheets. Para CHM no existe (ni se buscó) una lista
  equivalente.

## 3. Decisiones tomadas con el usuario

Antes de escribir el pipeline se plantearon 3 preguntas de diseño (vía
`AskUserQuestion`) y se resolvieron así:

1. **Diccionario de renombrado**: usar
   `ejemplos_output/Momentos_EC_CP - diccionario de variables.csv`
   (columnas `Nombre, Nuevo Nombre, conducta`, 431 filas), en vez del
   Google Sheet `DIC_URL` que usa el script EC (ese diccionario es
   específico de EC y no aplica a CHM).
2. **Columna "Evento"**: se omite por completo — el archivo CHM es un único
   conjunto de datos, sin distinción EC1/EC2.
3. **Filtro de IDs válidos**: no se aplica ningún filtro externo — se
   procesan todas las filas del archivo tal cual.

## 4. Corrección de un bug en la celda de lectura existente

El notebook ya tenía una celda que hacía `pd.read_excel(file_path)` sin
`skiprows`. Eso toma la fila 0 (códigos de variable, p. ej. `Q411_1`) como
encabezado de columnas, en vez de la fila 1 (texto real de la pregunta).
Se corrigió para leer:

```python
codes = pd.read_excel(file_path, header=None, nrows=1).iloc[0].astype(str).tolist()
df_instrumentos = pd.read_excel(file_path, skiprows=[0, 2])
```

Esto replica exactamente lo que hacía `leer_qualtrics()` en el script EC,
adaptado de `pd.read_csv` a `pd.read_excel`.

También se detectó que `openpyxl` (requerido por `pd.read_excel`/
`to_excel`) no estaba instalado en el entorno virtual del proyecto
(`./codinghubs`). Se instaló (`pip install openpyxl`) y se agregó a
`requirements.txt`.

## 5. Construcción del pipeline en `prueba.ipynb`

Se portaron (no se ejecutaron literalmente) las funciones y constantes del
script EC que seguían aplicando sin cambios, y se adaptaron las que
dependían de la estructura EC1/EC2. Celdas, en orden:

1. **Imports**: `re`, `pathlib.Path`, `pandas`.
2. **Lectura del archivo** (corregida, ver punto 4).
3. **Constantes y funciones auxiliares**, portadas tal cual del script EC:
   `ANCHOR`, `CF_STEMS`, `quitar_emoji`, `quitar_sufijo`, `normalizar`,
   `canon`, `extraer_nombre`.
   - `ROSTER_CODES` se portó con un cambio de nomenclatura: los 5 códigos
     que en EC se llamaban `PE1..PE5` (Pares Expertos) en CHM se llaman
     `CHM1..CHM5` (Coding Hub Master) — mismos códigos Qualtrics, mismas
     posiciones, solo cambia la etiqueta de rol. Los 6 códigos `DA1..DA6`
     se mantuvieron igual.
4. **Carga del diccionario de renombrado** (`Momentos_EC_CP - diccionario
   de variables.csv`) — ver punto 6 para el detalle de por qué esto se
   volvió más complejo de lo previsto.
5. **Asistentes (roster)**: `construir_asistentes()`, igual que en EC pero
   sin columna `Evento` (solo hay un archivo/evento).
6. **Momentos**: `construir_momentos()`, sin cambios de lógica — detecta
   las 5 anclas, corta 5 bloques de 408 columnas, los apila en formato
   largo con `Número de momento` (1–5), descarta momentos vacíos.
7. **Reemplazo de IDs de roster por nombres**: melt de las columnas
   "ID del/los docentes" → merge contra la tabla de asistentes por
   `(ID de respuesta, rol)` → pivot → merge de vuelta a `momentos`. Misma
   lógica que EC, sin columna `Evento` en las claves de merge.
8. **Instantáneas**: `construir_instantaneas()`, sin cambios de lógica —
   parsea semánticamente los bloques `I1.`…`I18.` y concatena acciones
   multiselección.
9. **Metadatos del encuentro** (`meta`), adaptado para CHM:
   - `Nombre del nodo` viene de `Q4` ("Nombre del Coding Hub"), no de la
     columna que buscaba EC (que no existe en este instrumento).
   - `Institución` se arma concatenando (unidas con `"; "`) todas las
     casillas marcadas de `Q5_4`…`Q5_25` (en EC era un solo campo de texto
     libre `Q5_1`).
   - No se construye `IDEncuentro` porque en el script EC viene de un
     lookup contra el Google Sheet de IDs válidos, que decidimos no usar.
10. **Ensamblado final**: `meta` se mergea con los momentos ya resueltos
    (por `ID de respuesta`), se renombra con el diccionario, se rellenan
    nulos con `""`. Igual para instantáneas.
11. **Guardado**: se escriben 3 archivos `.xlsx` en `output/`:
    `momentos_CHM_2026.xlsx`, `instantaneas_CHM_2026.xlsx`,
    `asistentes_CHM_2026.xlsx` (en el script EC original se guardaba en
    CSV; aquí se usa Excel para calzar con la forma del archivo de
    referencia `momentos_EC2_CHM.xlsx`).

## 6. Verificación y hallazgo de discrepancias en el diccionario

Al correr el pipeline por primera vez de punta a punta (ejecutando las
celdas del notebook fuera de Jupyter, como script, para poder inspeccionar
resultados con `pandas`), **el 71% de las columnas de momento (290 de
408) no se estaban renombrando correctamente** ni resolviendo bien los
nombres de roster. Se investigó columna por columna y se encontraron dos
problemas reales, no solo de decisión de diseño:

### 6.1 Desfase de sufijos de roster

El diccionario CSV fue construido esperando sufijos `PE1..PE6` / `DA1..DA6`
en las columnas de tipo "ID del/los docentes" y "Tipo de docente
implicado". Pero el archivo real usa una numeración distinta:

- `CHM1..CHM5` (5 casillas) en vez de `PE1..PE6` (6 casillas).
- `DA1..DA10` (10 casillas) en vez de `DA1..DA6` (6 casillas).

Además, el `pivot_table` que resuelve los códigos de roster a nombres
reales tiene `dropna=True` por defecto (heredado del script EC), lo que
**descartaba silenciosamente** cualquier columna de roster cuyo código no
apareciera en la tabla de asistentes construida con `ROSTER_CODES` — es
decir, todas las columnas `CHM1..CHM5` desaparecían del resultado en vez de
quedar vacías.

**Se confirmó con el usuario** que este instrumento solo usa nomenclatura
"CHM" (no "PE"), y se corrigió cambiando `ROSTER_CODES` para que los 5
códigos que antes mapeaban a `PE1..PE5` ahora mapeen a `CHM1..CHM5` (los
códigos de Qualtrics y las personas detrás son los mismos, solo cambió el
nombre del rol). Los slots `DA7..DA10` quedan sin resolver a propósito: no
existe ningún código de selección de roster en el archivo que cubra esos 4
slots adicionales.

### 6.2 Desfase de texto en las preguntas

Se detectaron dos tipos de diferencia de redacción entre el diccionario y
el archivo real:

- Sistemática: el diccionario dice `"Tipo de docente implicado"`, el
  archivo real dice `"Tipo de docente"` (sin la palabra "implicado").
- No sistemática: algunas preguntas están redactadas de forma distinta de
  fondo (p. ej. la pregunta de "humor" en la conducta "Construcción de
  ambiente colaborativo" tiene una formulación distinta en el diccionario
  que en el archivo real), y otras son preguntas nuevas que no existen en
  el diccionario en absoluto (escucha activa, turnos de conversación,
  columnas de `Timing`).

**Se confirmó con el usuario** normalizar en código solo las variantes
conocidas y sistemáticas, dejando sin renombrar las columnas con
diferencias de contenido real (no hay forma segura de adivinarlas
automáticamente).

### 6.3 Solución implementada

Se construyó un segundo nivel de "match por raíz" en la celda del
diccionario, además del match exacto original:

1. `canon_dic()`: como `canon()`, pero además reemplaza `"Tipo de docente
   implicado"` por `"Tipo de docente"`.
2. Para cada fila del diccionario cuyo `Nombre` termine en un sufijo de
   roster (`- PE\d*`, `- DA\d*`), se guarda también la versión sin sufijo
   ("raíz") apuntando al `Nuevo Nombre` sin su propio sufijo.
3. Al renombrar una columna real: si no hay match exacto, se le quita el
   sufijo de roster (`CHM\d*`/`DA\d*`/`PE\d*`), se busca la raíz resultante
   en el diccionario, y si hay match se reconstruye el nombre final
   pegando **el sufijo real del archivo** (no el del diccionario) al
   nombre nuevo encontrado. Así, por ejemplo, una columna terminada en
   `- CHM3` en el archivo puede resolverse contra una entrada del
   diccionario que originalmente decía `- PE3`, y el resultado final
   conserva `- CHM3`.

Con este cambio, las columnas resueltas correctamente subieron de 118/408
a 279/408 solo por el manejo de sufijos, y a **244 de 323 columnas finales
(75%)** una vez sumada la normalización de "implicado". Las columnas
restantes corresponden a diferencias de contenido genuinas (no de forma) y
quedaron, a propósito, con su texto original largo.

## 7. Resultado final

- `output/momentos_CHM_2026.xlsx` — 43 filas × 323 columnas (tabla larga,
  una fila por momento observado, `Número de momento` 1–5).
- `output/instantaneas_CHM_2026.xlsx` — 128 filas × 17 columnas.
- `output/asistentes_CHM_2026.xlsx` — 88 filas × 3 columnas (roster
  resuelto: `ID de respuesta`, `rol`, `Nombre`).

Los tres archivos se generan **exclusivamente** a partir de
`input/Instrumento+EC+CHM+2026_25+de+agosto+de+2026_10.40.xlsx` (no se
mezclan datos de `ejemplos_output/` ni de ninguna otra fuente; ese archivo
solo se usa como diccionario de renombrado y como referencia de forma
esperada).

## 8. Pendiente / fuera de alcance

- No se agregaron las hojas `sexo_docentes` ni `diccionario` dentro del
  Excel de momentos (esas hojas son insumos de `02_exploracion_ec_2026.py`,
  un script posterior de análisis, no de `01_limpieza_datos_EC_2026.py`).
- Las ~79 columnas de momento que quedaron sin renombrar por diferencias
  de contenido real entre el diccionario y el archivo requieren revisión
  manual del diccionario si se quiere cubrirlas.
- El archivo de entrada tenía solo 13 respuestas al momento de este
  trabajo; si se reprocesa con un export más grande, conviene volver a
  correr la verificación de la sección 6 para confirmar que no aparecen
  nuevas variantes de redacción no cubiertas.
