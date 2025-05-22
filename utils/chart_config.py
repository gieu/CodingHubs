def get_chart_config():
    chart_config = {
        'editable': True,
        'toImageButtonOptions': {
            'format': 'png',  # one of png, svg, jpeg, webp
            'filename': 'grafica',
            'scale': 3  # Multiply title/legend/axis/canvas sizes by this factor
        }
    }
    return chart_config