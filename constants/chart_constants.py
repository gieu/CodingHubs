import plotly.express as px

COLOR_PALETTES = {
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
    "Vivid": px.colors.qualitative.Vivid,
}

AGGREGATION_METHODS = {
    "Cuenta": "count",
    "Suma": "sum",
    "Promedio": "mean",
    "Cuenta de únicos": "nunique",
}

BARMODE_DICT = {
    "grupo": "group",
    "apilado": "stack",
    "superpuesto": "overlay",
    "relativo": "relative",
}