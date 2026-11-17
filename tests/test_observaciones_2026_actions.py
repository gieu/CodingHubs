import unittest
from unittest.mock import patch

import pandas as pd

from actions import observaciones_2026_actions as charts


class TeacherActionAliasesTest(unittest.TestCase):
    def test_action_colors_stay_the_same_when_filtering_categories(self):
        source = pd.DataFrame({
            "momento": ["2026_1", "2026_1"],
            charts.INSTANT: [1, 1],
            "accion_docente_clean": ["Gestión de aula", "Supervisar trabajos"],
            "accion_docente_cat": ["Gestión de aula", "Interacción"],
        })
        for subset in [source, source.iloc[[1]]]:
            figures = []
            with patch.object(charts, "_show", side_effect=lambda fig, **kwargs: figures.append(fig)), patch.object(charts, "st"):
                charts.instantaneas(subset, source[["momento"]])
            for trace in figures[0].data:
                self.assertEqual(trace.line.color, charts.ACTION_COLORS[trace.name])
            scale = figures[-1].data[0].colorscale
            self.assertEqual([color for _, color in scale], charts.GREEN_SCALE)

    def test_heatmap_prioritizes_requested_actions_then_sorts_the_rest(self):
        source = pd.DataFrame({
            "momento": ["2025_1"] * 5,
            charts.INSTANT: [1] * 5,
            "accion_docente_clean": ["Supervisar trabajos", "Retroalimentar trabajos",
                                     "Aclarar dudas", "Explicar temas", "Dar instrucciones"],
        })
        figures = []
        with patch.object(charts, "_show", side_effect=lambda fig, **kwargs: figures.append(fig)), patch.object(charts, "st"):
            charts.instantaneas(source, pd.DataFrame({"momento": ["2025_1"] * 5}))
        self.assertEqual(list(figures[-1].data[0].y), [
            "Dar instrucciones", "Explicar temas", "Retroalimentar trabajos",
            "Aclarar dudas", "Supervisar trabajos",
        ])

    def test_aliases_merge_in_both_charts_without_changing_totals_or_source(self):
        actions = [
            "Hacer preguntas",
            "Está haciendo preguntas a los/las estudiantes",
            " Está haciendo preguntas a toda la clase ",
            "Retroalimentar trabajos",
            "Está retroalimentando el trabajo realizado por los/las estudiantes",
            "Está retroalimentando el trabajo realizado por los/las estudiantes (en parejas o grupos)",
            "Explicar temas",
            None,
        ]
        source = pd.DataFrame({
            "momento": ["2025_1"] * 8,
            charts.INSTANT: [1] * 8,
            "accion_docente_clean": actions,
            "accion_docente_cat": ["Interacción", None, None, "Interacción", None, None,
                                   "Instrucción docente", None],
            "comentarios": ["Respuesta"] * 8,
        })
        original = source.copy(deep=True)
        figures = []
        with patch.object(charts, "_show", side_effect=lambda fig, **kwargs: figures.append(fig)), patch.object(charts, "st"):
            charts.instantaneas(source, pd.DataFrame({"momento": ["2025_1"] * 8}))
        pd.testing.assert_frame_equal(source, original)
        lines = {trace.name: trace for trace in figures[0].data}
        self.assertEqual(lines["Interacción"].customdata, ([6, 8],))
        self.assertEqual(lines["Sin dato"].customdata, ([1, 8],))
        heatmap = figures[1].data[0]
        values = dict(zip(heatmap.y, heatmap.z))
        self.assertEqual(set(values), {"Hacer preguntas", "Retroalimentar trabajos",
                                       "Explicar temas", "Sin dato"})
        self.assertEqual(values["Hacer preguntas"], [37.5])
        self.assertEqual(values["Retroalimentar trabajos"], [37.5])
        self.assertEqual(sum(row[0] for row in heatmap.z), 100)


if __name__ == "__main__":
    unittest.main()
