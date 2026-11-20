import unittest

import pandas as pd

from utils import biobots_tracking as tracking


class TrackingTest(unittest.TestCase):
    def data(self):
        data = pd.DataFrame({'Grupo': ['Priorizados', 'No priorizados', 'No priorizados'],
                             'Total': [6, 5, 0], 'Acompañamiento': [2, 1, float('nan')]})
        for scenario in tracking.SCENARIOS:
            data[scenario] = [1, 1, float('nan')]
        return data

    def test_group_denominators_and_missing_records(self):
        table = tracking.coverage(self.data(), grouped=True)
        a = table[table['Grupo'].eq('Priorizados')]
        b = table[table['Grupo'].eq('No priorizados')]
        self.assertTrue(a['Porcentaje'].eq(100).all())
        self.assertTrue(b['Porcentaje'].eq(50).all())
        self.assertTrue(b['Base'].eq(2).all())
        self.assertTrue(b['Sin_registro'].eq(1).all())

    def test_missing_accompaniment_is_not_zero_sessions(self):
        fig = tracking.accompaniment_figure(self.data())
        self.assertEqual(list(fig.data[1].y), [0, 50, 0])

    def test_heatmap_preserves_missing_and_labels_all_cells(self):
        fig = tracking.heatmap_figure(self.data())
        self.assertEqual(len(fig.layout.annotations), 18)
        self.assertEqual(sum(a.text == 'Sin registro' for a in fig.layout.annotations), 6)

    def test_all_figures_serialize(self):
        data = self.data()
        for fig in [tracking.distribution_figure(data), tracking.accompaniment_figure(data),
                    tracking.goals_figure(data), tracking.heatmap_figure(data),
                    tracking.coverage_figure(data), tracking.coverage_figure(data, grouped=True)]:
            self.assertTrue(fig.to_json())

    def test_goals_require_all_three_sequence_stages(self):
        data = self.data()
        data.loc[0, 'E3'] = float('nan')
        fig = tracking.goals_figure(data)
        self.assertAlmostEqual(fig.data[0].y[0], 200 / 3)
        self.assertAlmostEqual(fig.data[1].y[0], 100 / 3)

    def test_annotation_legend_cannot_leave_orphan_labels(self):
        fig = tracking.accompaniment_figure(self.data())
        self.assertFalse(fig.layout.legend.itemclick)
        self.assertFalse(fig.layout.legend.itemdoubleclick)
        self.assertTrue(all(v >= 0 for v in fig.layout.yaxis.tickvals))

    def test_prepare_rejects_duplicate_teachers(self):
        raw = pd.DataFrame({'Nombres completos': ['A', 'B'], 'Número de identificación': [1, 1]})
        with self.assertRaisesRegex(ValueError, 'única'):
            tracking.prepare(raw)


if __name__ == '__main__':
    unittest.main()
