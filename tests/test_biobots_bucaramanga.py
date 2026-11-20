import unittest

import pandas as pd

from utils.biobots_bucaramanga import barrier_counts, distribution, stacked_figure, AGREEMENT


class SurveyAggregationTest(unittest.TestCase):
    def test_missing_answers_are_not_disagreement(self):
        table = distribution(pd.DataFrame({'Pregunta [Indicador]': ['De acuerdo', None, ' ', 'Neutro']}), 'Pregunta')
        self.assertEqual(table['Base'].tolist(), [2, 2])
        self.assertEqual(table['Porcentaje'].sum(), 100)

    def test_not_applicable_remains_in_denominator(self):
        table = distribution(pd.DataFrame({'Pregunta [Transición]': ['Difícil', 'No aplica']}), 'Pregunta')
        self.assertEqual(table.loc[table['Respuesta'] == 'Difícil', 'Porcentaje'].iloc[0], 50)

    def test_multiselect_counts_each_person_once_and_groups_free_text(self):
        table = barrier_counts(pd.Series(['Manejo del tiempo durante las sesiones, Falta de tiempo disponible en el horario escolar',
                                         'Otro motivo, con comas', None, 'Ninguna']))
        counts = table.set_index('Factor')
        self.assertEqual(counts.loc['Otras dificultades', 'n'], 1)
        self.assertEqual(counts.loc['Manejo del tiempo durante las sesiones', 'n'], 1)
        self.assertEqual(set(table['Base']), {3})
        self.assertGreater(table['Porcentaje'].sum(), 100)

    def test_all_segments_have_readable_labels_including_tiny_values(self):
        table = pd.DataFrame({
            'Indicador': ['Ejemplo'] * 3,
            'Respuesta': ['En desacuerdo', 'Neutro', 'De acuerdo'],
            'n': [1, 1, 9998], 'Base': [10000] * 3,
            'Porcentaje': [0.01, 0.01, 99.98],
        })
        figure = stacked_figure(table, 'Prueba', AGREEMENT)
        labels = figure.layout.annotations
        self.assertEqual(len(labels), 3)
        self.assertFalse(figure.layout.legend.itemclick)
        self.assertFalse(figure.layout.legend.itemdoubleclick)
        self.assertEqual([label.text for label in labels[:2]], ['0.01%', '0.01%'])
        self.assertNotEqual(labels[0].yshift, labels[1].yshift)
        self.assertAlmostEqual(labels[2].x, 50.01)
        self.assertTrue(all(label.bgcolor and label.font.color == '#203447' for label in labels))

    def test_unknown_categories_are_preserved(self):
        table = distribution(pd.DataFrame({'Pregunta [Indicador]': ['Nueva categoría', 'De acuerdo']}), 'Pregunta')
        figure = stacked_figure(table, 'Prueba', AGREEMENT)
        self.assertIn('Nueva categoría', [trace.name for trace in figure.data])


if __name__ == '__main__':
    unittest.main()
