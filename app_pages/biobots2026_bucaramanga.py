"""Encuesta de docentes BioBots de Bucaramanga."""
import streamlit as st

from app_pages.biobots_bucaramanga_section import render as render_bucaramanga
from app_pages.biobots_tracking_section import render as render_tracking
from constants.footer_constants import FOOTER_HTML, IMAGENES_BASE64
from constants.header_constants import header
from utils.chart_config import get_chart_config

CHART_CONFIG = get_chart_config()
COLORS = {"orange": "#F39C12", "text_dark": "#2C3E50"}


def style_figure(fig, height=430):
    fig.update_layout(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial", color=COLORS["text_dark"]),
        title=dict(font=dict(size=20, color=COLORS["text_dark"]),
                   x=0, y=0.98, yanchor="top", yref="container"),
        margin=dict(l=50, r=30, t=160 if fig.layout.barmode == "stack" else 85, b=55),
        hoverlabel=dict(bgcolor="white"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="#E9EFF5", zeroline=False)
    return fig


def plot(fig, key):
    st.plotly_chart(fig, width="stretch", config=CHART_CONFIG, key=key)


def analysis_callout(hallazgo, implicacion, accion):
    st.markdown(
        f"""
        <div style="background:#F3F8FC;border-left:5px solid {COLORS['orange']};
                    padding:14px 18px;margin:-4px 0 28px;border-radius:0 8px 8px 0;color:#2C3E50">
            <strong>Lectura para la acción</strong><br>
            <span><strong>Hallazgo:</strong> {hallazgo}</span><br>
            <span><strong>Implicación:</strong> {implicacion}</span><br>
            <span><strong>Acción:</strong> {accion}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


header("#2C3E50")
st.title("Biobots 2026 Bucaramanga")
render_tracking(style_figure, plot)
st.markdown("---")
render_bucaramanga(style_figure, plot, analysis_callout)
st.markdown("---")
st.markdown(FOOTER_HTML.format(imagenes_base64=IMAGENES_BASE64), unsafe_allow_html=True)
