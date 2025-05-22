import streamlit as st

import geopandas as gpd # type: ignore
import plotly.graph_objects as go # type: ignore
import plotly.express as px # type: ignore

LIGHT_LAVANDER ="#f7e2ff"
LAVANDER = "#BD78D9"
DARK_VIOLET = "#402F6E"
def dibujar_mapa(gdf: gpd.geodataframe.GeoDataFrame) -> None:
    """Given a GeoDataFrame Object, this function plots a map of Colombia.
    The data should be grouped by 'departamento' (dpto_cnmbr) and should have a 
    value 'Count' that represents the number of nodos in this 'departamento'.
    For more information, check the 'get_nodo_map_data' function on actions folder.


    Args:
        gdf (gpd.geodataframe.GeoDataFrame)
    """
    
    # Plot the map using Plotly
    fig = px.choropleth(gdf, 
        geojson=gdf.geometry, 
        locations=gdf.index,
        color='Nodos',
        color_continuous_scale=[[0, "#fcf3ff"], [.01, LIGHT_LAVANDER], [.2, LAVANDER], [1, DARK_VIOLET]],
        projection="mercator",
        hover_data={"dpto_cnmbr": True, "dpto_codigo": True},  # Include department code and name in hover data
        labels={"dpto_codigo": "Code", "dpto_cnmbr": "Name"},  # Label customization
        custom_data=["dpto_codigo", "dpto_cnmbr"],  # Additional data for hover
    )

    fig.update_geos(
        fitbounds="locations",
        showframe=False,  # Hide frame
        visible=False,
        showland=True,
        landcolor='#F5F5F5',
        showocean=True,
        oceancolor='#c4dfe8',  # Set sea color to light blue
        coastlinecolor=DARK_VIOLET
    )

    # Add text over cities
    cities_with_nodos = gdf[gdf['Nodos'] > 0]

    fig.add_trace(
        go.Scattergeo(
            lon = cities_with_nodos.geometry.apply(lambda geom: geom.centroid.x),
            lat = cities_with_nodos.geometry.apply(lambda geom: geom.centroid.y),
            text = cities_with_nodos['Nodos'],  # Text to display
            mode = 'markers+text',
            marker = dict(size=12, color='white', symbol='square'),  # Transparent marker
            textfont = dict(size=8, color='black', family='Arial'),
            showlegend = False,
            hoverinfo = 'skip',
        )
    )

    fig.update_layout(
        autosize=False,
        margin=dict(l=0, r=0, b=0, t=0, pad=0),
        height=450,
    )
    # fig.update_traces(marker_line_width=0)
    fig.update_coloraxes(showscale=False)
    # fig.show() # Plot the figure 
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("Los datos geográficos fueron creados apartir del datos del [Dane]('https://geoportal.dane.gov.co/servicios/descarga-y-metadatos/datos-geoestadisticos/?cod=111') y datos abiertos disponibles en el [Github]('https://github.com/jacasta2/colombian_map/blob/main/from_shapefiles/departamentos/mapa_departamentos.json')")