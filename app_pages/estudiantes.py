import streamlit as st
import pandas as pd
import plotly.express as px
from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import LOGO_NAVBAR_BASE64, HIDE_STREAMLIT_STYLE, NAVBAR_TEMPLATE, generar_css_personalizado
from utils.chart_config import get_chart_config
chart_config = get_chart_config()
# Configuración de la página
st.set_page_config(layout="wide")

# Ocultar elementos de Streamlit
st.markdown(HIDE_STREAMLIT_STYLE, unsafe_allow_html=True)

# Generar el CSS personalizado con el color deseado
color_fondo_navbar = "#4A90E2"  # Cambia este valor según lo necesites
custom_css = generar_css_personalizado(color_fondo_navbar)

# Aplicar el CSS en Streamlit
st.markdown(custom_css, unsafe_allow_html=True)

# Navbar personalizado con logo
navbar = NAVBAR_TEMPLATE.format(LOGO_NAVBAR_BASE64=LOGO_NAVBAR_BASE64)
st.markdown(navbar, unsafe_allow_html=True)

# URL del CSV
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTKYc2cyhi-1O4wGvtMh9P0kIVylAkMGS0ZCqTkxdHqW3ksfflMFJ7FbzUm_RKHtsrOZNPyeYYSfRHj/pub?output=csv"
CSV_AUX_PRE="https://docs.google.com/spreadsheets/d/e/2PACX-1vR-3xl1aiDrL1Y-ckN9ljdVTdut7S2C4H_1VtAUuJ7Q5w9eRV1zDq3QlFtVSF45QKXQ5uQOXnJCje0v/pub?output=csv"
CSV_AUX_GRADO="https://docs.google.com/spreadsheets/d/e/2PACX-1vRBBjImOz7qgk_1-3UpJ4qqSPSMoNGxQxMVSvd50XtZ7AntQLdnB2YM8E1Cgo7DqPixUz0phGoSkw9_/pub?output=csv"
CSV_AUX_ESTEREOTIPOS="https://docs.google.com/spreadsheets/d/e/2PACX-1vSAeQMy5-YOKAVIhsV_xaZ3P7wfU5caHp7o0TNg4_6NlCdSOtIlhxxUpnhOaOpfFZrZ4D0jtZY1WgtO/pub?output=csv"
# --- Cargar Datos con Cache ---
@st.cache_data(ttl=600)
def load_data(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    return df

df = load_data(CSV_URL)

# Cargar el archivo auxiliar para "Tipo de Preferencia"
@st.cache_data(ttl=600)
def load_aux_data(file):
    aux_df = pd.read_csv(file)
    aux_df.columns = aux_df.columns.str.strip()
    return aux_df



Preferencias = [
    'Preferencia 1', 'Preferencia 2', 'Preferencia 3', 'Preferencia 4', 'Preferencia 5', 
    'Preferencia 6', 'Preferencia 7', 'Preferencia 8', 'Preferencia 9', 'Preferencia 10', 
    'Preferencia 11', 'Preferencia 12', 'Preferencia 13', 'Preferencia 14', 'Preferencia 15'
]

Profesiones = [
    '2. Psicólogo/a', '2. Policía', '2. Bailarín/a', '2. Medico/a', '2. Ingeniero/a', 
    '2. Programador/a', '2. Biólogo/a', '2. Matemático/a', '2. Docente'
]
Actividades = [
    'Llevar al pollito', 'Botella blanca', 'Error en Pac-Man', 'Instrucciones para Pac-Man', 
    'Pulsera mágica', 'Espacios libres en parqueo', 'Ingredientes en hamburguesas', 
    'Preferencias de pasatiempos', 'Salida pedagógica', 'Ventas de helados por semana', 
    'Medidas de calidad del aire', 'Programación de MicroBit', 'Expresiones lógicas', 
    'Error en secuencia Pac-Man', 'Bloque faltante Pac-Man', 'Proceso de mensaje de texto', 
    'Serie de figuras', 'Lonchera Óscar', 'Preguntas ventas de helados', 'Distancia a instituto', 
    'Costos de Aerolíneas'
]


dict_aux = { "Preferencias": CSV_AUX_PRE,
    "Actividades": CSV_AUX_GRADO,
    "Profesiones": CSV_AUX_ESTEREOTIPOS,
}

st.title("Graficador de datos de estudiantes")


# Selección del tipo de gráfico
chart_type = st.radio("Tipo de Gráfico", ["Barras", "Dispersión", "Cajas", "Línea", "Histograma"])

# Seleccionar preguntas directamente con un multiselect
preguntas_actualizadas = st.multiselect(
    "Selecciona las preguntas",
    options=df.columns,
    default=[]
)

# Validar si se seleccionaron preguntas
if not preguntas_actualizadas:
    st.warning("Por favor, selecciona al menos una pregunta.")

categoria_x = None
if any(pregunta in Preferencias for pregunta in preguntas_actualizadas):
    categoria_x = "Preferencias"
elif any(pregunta in Profesiones for pregunta in preguntas_actualizadas):
    categoria_x = "Profesiones"
elif any(pregunta in Actividades for pregunta in preguntas_actualizadas):
    categoria_x = "Actividades"

col_x = st.selectbox("Selecciona el eje X", ['Pregunta', 'Respuesta'])


# Selección de categoría y columna para el eje Y
col_y = st.selectbox("Variable para el eje Y", df.columns)

if col_y in preguntas_actualizadas:
    st.warning("El eje X y el eje Y no pueden ser la misma columna. Por favor, selecciona columnas diferentes.")

# Selección de facetas

# Agrupar los selectboxes en una sola fila
col1, col2, col3 = st.columns(3)
with col1:
    facet_col = st.selectbox("Dividir en columnas por (opcional)", ["Ninguna", "Categoria", "Pregunta", "Respuesta"] + (["Categoria Conocimiento"] if any(pregunta in Actividades for pregunta in preguntas_actualizadas) else []) + list(df.columns))

with col2:
    facet_row = st.selectbox("Dividir en filas por (opcional)", ["Ninguna", "Categoria", "Pregunta", "Respuesta"] + (["Categoria Conocimiento"] if any(pregunta in Actividades for pregunta in preguntas_actualizadas) else []) + list(df.columns))

with col3:
    col_color = st.selectbox("Agrupar por color (opcional)", ["Ninguna", "Categoria", "Pregunta", "Respuesta"] + (["Categoria Conocimiento"] if any(pregunta in Actividades for pregunta in preguntas_actualizadas) else []) + list(df.columns))

col_generales = [facet_col, facet_row, col_color, col_y]#contiene todos los datos de los filtros que no sea ninguna ni eje y
col_id = set(col_generales).difference(set(["Ninguna", "Categoria", "Pregunta", "Respuesta","Categoria Conocimiento"]))#elimina los valores de ninguna
col_id = list(col_id)
st.write("Columnas de interés:",col_id)
df_filtrado = df.copy()  # Inicializar df_filtrado como una copia de df

# Combinar columnas generales y de preferencias
datos_interes = df_filtrado.loc[:, preguntas_actualizadas + col_id]
# Transformar datos con melt
datos_interes_m = datos_interes.melt(
    id_vars=col_id,
    value_vars=preguntas_actualizadas,
    value_name='Respuesta',
    var_name='Pregunta'
)
st.write("Datos de interés transformados:",col_generales)
if "Categoria" in col_generales or "Categoria Conocimiento" in col_generales:
    st.write("Se ha seleccionado la columna 'Categoria' o 'Categoria Conocimiento'. Se aplicará un merge con el archivo auxiliar.")
    aux_file = dict_aux[categoria_x]
    aux_data = load_aux_data(aux_file)
    # Realizar el merge con el archivo auxiliar
    datos_interes_m = datos_interes_m.merge(
        aux_data,
        left_on=['Pregunta','Respuesta'],
        right_on=['Preguntas','Opcion'],
        how='left'
    ).drop(columns=['Preguntas','Opcion'])  
    df_filtrado = datos_interes_m.copy()
    st.dataframe(df_filtrado.dropna().head(1000))
else:
    df_filtrado = datos_interes_m.copy()

def es_numerica(col, df):
    try:
        return pd.api.types.is_numeric_dtype(df[col])
    except KeyError:
        return False

# Validación extra de variable Y para gráficos numéricos
if chart_type in ["Dispersión", "Línea", "Cajas"]:
    if not es_numerica(col_y, df):
        st.warning() ## mejor un warning


# --- Filtros dinámicos ---

with st.expander("Filtros de Datos (Opcional)", expanded=False):
    columnas_filtro = st.multiselect("Selecciona columnas para filtrar", df.columns)
    for col in columnas_filtro:
        if es_numerica(col, df):
            rango = st.slider(f"Rango para {col}", float(df[col].min()), float(df[col].max()), (float(df[col].min()), float(df[col].max())))
            df_filtrado = df_filtrado[(df_filtrado[col] >= rango[0]) & (df_filtrado[col] <= rango[1])]
        else:
            valores = df[col].dropna().unique().tolist()
            seleccionados = st.multiselect(f"Valores para {col}", valores, default=valores)
            df_filtrado = df_filtrado[df_filtrado[col].isin(seleccionados)]

df_plot = df_filtrado.copy()
#Configuración de agregación para gráficos de barras
if chart_type == "Barras":
    opciones_agregacion = ["Cuenta", "Cuenta de únicos"]
    if es_numerica(col_y, df):
        opciones_agregacion.insert(1, "Promedio" )  
        opciones_agregacion.insert(2, "Suma" ) 
    metodo_agregacion = st.selectbox("Método de agregación", opciones_agregacion)
    aggfunc = {"Cuenta": "count","Suma": "sum", "Promedio": "mean",  "Cuenta de únicos": "nunique"}[metodo_agregacion]
    indices=[facet_col,facet_row, col_color, col_x]#contiene todos los datos de los filtros que no sea ninguna ni eje y
    if 'Categoria Conocimiento' in df_filtrado.columns:
        indices.append('Categoria Conocimiento')
    indices=set(indices).difference(set(["Ninguna"]))#elimina los valores de ninguna
    indices=list(indices)
    df_plot = pd.pivot_table(df_filtrado, values=col_y, index=indices, aggfunc=aggfunc).reset_index()


    # Verificar que las columnas seleccionadas existen en el DataFrame después de pivot_table
    if col_y not in df_plot.columns:
        st.warning(f"La columna '{col_y}' no se encuentra en los datos después de aplicar pivot_table. Por favor, selecciona otra columna.")

    # Selección del tipo de barra (barmode)
    barmode = st.selectbox("Tipo de barra", ["grupo", "apilado", "superpuesto", "relativo"])
    barmode_dict = {"grupo": "group", "apilado": "stack", "superpuesto": "overlay", "relativo": "relative"}
    if st.checkbox("Ver barras horizontales"):
        orientation = 'h'
        invertir = True
    else:
        orientation = 'v'
        invertir = False
    if st.checkbox("Visualizar frecuencia relativa"):
        columna_total = st.multiselect("Relativo respecto a:", ["Total"] + indices)
        if len(columna_total) == 0:
            st.warning("Por favor, selecciona una columna para calcular la frecuencia relativa.")
            st.stop()
        if len(columna_total) > 1 and "Total" in columna_total:
            st.warning("Selección errónea. Si desea ver el porcentaje respecto al Total, elimine los demás valores seleccionados, de lo contrario, elimine 'Total' para elegir una combinación personalizada")
            st.stop()
        if columna_total[0] == "Total":
            total = df_plot[col_y].sum()
            df_plot["Frecuencia"] = df_plot[col_y] / total
        elif columna_total == "Preguntas":
            arreglo_indices = [columna_total]
            if facet_row is not None:
                arreglo_indices.append(facet_row)
            if facet_col is not None:
                arreglo_indices.append(facet_col)
            total = df_plot.pivot_table(index=list(set(arreglo_indices)),
                                        values=col_y,
                                        aggfunc='sum').rename(columns={col_y: "TOTAL"}).reset_index()
            df_plot = df_plot.merge(total, on=list(set(arreglo_indices)))
            df_plot["Frecuencia"] = df_plot[col_y] / df_plot["TOTAL"]
        else:
            total = df_plot.pivot_table(index=columna_total,
                                        values=col_y,
                                        aggfunc='sum').rename(columns={col_y: "TOTAL"}).reset_index()
            df_plot = df_plot.merge(total, on=columna_total)
            df_plot["Frecuencia"] = df_plot[col_y] / df_plot["TOTAL"]
        visualizarFrecuencia=True
    else:
        visualizarFrecuencia=False

# Selección de colores
color_palettes = {
    "Plotly": px.colors.qualitative.Plotly,
    "Viridis": px.colors.sequential.Viridis,
    "Cividis": px.colors.sequential.Cividis,
    "Inferno": px.colors.sequential.Inferno,
    "Magma": px.colors.sequential.Magma,
    "Plasma": px.colors.sequential.Plasma,
    "Turbo": px.colors.sequential.Turbo,
    "G10": px.colors.qualitative.G10,
    "T10": px.colors.qualitative.T10,
    "Alphabet": px.colors.qualitative.Alphabet,
    "Dark24": px.colors.qualitative.Dark24,
    "Light24": px.colors.qualitative.Light24,
    "Set1": px.colors.qualitative.Set1,
    "Pastel1": px.colors.qualitative.Pastel1,
    "Set2": px.colors.qualitative.Set2,
    "Pastel2": px.colors.qualitative.Pastel2,
    "Set3": px.colors.qualitative.Set3,
    "Antique": px.colors.qualitative.Antique,
    "Bold": px.colors.qualitative.Bold,
    "D3": px.colors.qualitative.D3,
    "Prism": px.colors.qualitative.Prism,
    "Safe": px.colors.qualitative.Safe,
    "Vivid": px.colors.qualitative.Vivid
}


color_palette = st.selectbox("Paleta de colores", list(color_palettes.keys()))
color_sequence = color_palettes[color_palette]

category_order={
    "Momento_cono":["Pretest","Posttest"],
    "Sexo":["Mujer","Hombre"],
    "Grado":["Tercero","Cuarto","Quinto","Sexto","Septimo","Séptimo","Octavo","Noveno","Décimo","Undécimo"],
}

if chart_type in ["Barras", "Cajas", "Histograma"]:
    valores_unicos = df_plot[col_x].unique().tolist() 
    with st.expander("Orden de categorías (Opcional)", expanded=False):
        category_order[col_x] = st.multiselect("Ordena las categorías", options=valores_unicos, default=valores_unicos)
custom_title = st.text_input("Título personalizado del gráfico (opcional)")

          

if df_plot.empty:
    st.warning("No hay datos disponibles después de aplicar los filtros.")

st.markdown("### Vista previa de datos filtrados")
st.dataframe(df_plot.dropna().head(1000))



# Verificar que las columnas seleccionadas existen en el DataFrame
if col_y not in df_plot.columns:
    st.warning(f"La columna '{col_y}' no se encuentra en los datos filtrados. Por favor, selecciona otra columna.")
    st.stop()
title = custom_title if custom_title else f"{chart_type}: {'Pregunta'} vs {col_y}"
color_param = None if col_color == "Ninguna" else col_color
if col_color == "Ninguna":
    col_color = None

# Configuración de facetas
facet_col_param = None if facet_col == "Ninguna" else facet_col
facet_row_param = None if facet_row == "Ninguna" else facet_row


columnas_grafico = [col_x, col_y, col_color, facet_col_param, facet_row_param]
columnas_grafico = [col for col in columnas_grafico if col]  # Eliminar valores None


if chart_type == "Barras":
    if visualizarFrecuencia:
        fig = px.bar(
            df_plot,
            x=col_x if orientation == 'v' else "Frecuencia",
            y="Frecuencia" if orientation == 'v' else col_x,
            color=col_color,
            title=title,
            barmode=barmode_dict[barmode],
            color_discrete_sequence=color_sequence,
            facet_col=facet_col_param,
            facet_row=facet_row_param,
            category_orders=category_order,
            orientation=orientation,
            text="Frecuencia"
        )
        fig.update_traces(texttemplate='%{text:.2%}', textposition='outside')
        fig.update_layout(yaxis_tickformat=',.0%' if orientation == 'v' else None,
                          xaxis_tickformat=',.0%' if orientation == 'h' else None)
    else:
        # Crear gráfico de barras absoluto
        fig = px.bar(
            df_plot,
            x=col_x if orientation == 'v' else col_y,
            y=col_y if orientation == 'v' else col_x,
            color=col_color,
            title=title,
            barmode=barmode_dict[barmode],
            color_discrete_sequence=color_sequence,
            facet_col=facet_col_param,
            facet_row=facet_row_param,
            category_orders=category_order,
            orientation=orientation
        )

elif chart_type == "Dispersión":
    fig = px.scatter(df_plot, x=col_x, y=col_y, color=color_param, title=title, color_discrete_sequence=color_sequence, facet_col=facet_col_param, facet_row=facet_row_param)
elif chart_type == "Cajas":
    fig = px.box(df_plot, x=col_x, y=col_y, color=color_param, title=title, color_discrete_sequence=color_sequence, facet_col=facet_col_param, facet_row=facet_row_param,category_orders=category_order)
elif chart_type == "Línea":
    fig = px.line(df_plot, x=col_x, y=col_y, color=color_param, title=title, color_discrete_sequence=color_sequence, facet_col=facet_col_param, facet_row=facet_row_param)
elif chart_type == "Histograma":
    # Selección del tipo de barra (barmode) para histograma
    barmode = st.selectbox("Tipo de barra", ["grupo", "superpuesto", "relativo"])
    barmode_dict = {"grupo": "group", "superpuesto": "overlay", "relativo": "relative"}
    fig = px.histogram(df_plot, x=col_x, color=color_param, title=title, barmode=barmode_dict[barmode], color_discrete_sequence=color_sequence, facet_col=facet_col_param, facet_row=facet_row_param,category_orders=category_order)

st.plotly_chart(fig, use_container_width=True, config=chart_config)

def convertir_csv(dataframe):
    return dataframe.to_csv(index=False).encode('utf-8')

#st.download_button("Descargar datos filtrados", convertir_csv(df_filtrado), "datos_filtrados.csv", "text/csv")
#st.download_button("Descargar datos completos", convertir_csv(df), "datos_completos.csv", "text/csv")

# Pie de página
st.markdown("---")
st.write("© 2025 Colombia Programa - Ministerio de Tecnologías de la Información y las Comunicaciones (MinTIC)")

# Formatear el HTML con las imágenes convertidas a base64
formatted_footer = FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64)

# Mostrar el footer en Streamlit
st.markdown(formatted_footer, unsafe_allow_html=True)