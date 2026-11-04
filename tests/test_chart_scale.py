from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from pipeline.chart_scale import compact_number, confirmed_dominance, nice_axis_scale


class ChartScaleTest(unittest.TestCase):
    def test_large_range_uses_round_two_hundred_thousand_steps(self):
        maximum, step = nice_axis_scale([1_035_000])
        self.assertEqual(1_200_000, maximum)
        self.assertEqual(200_000, step)

    def test_smaller_range_scales_down(self):
        maximum, step = nice_axis_scale([47_500])
        self.assertEqual(50_000, maximum)
        self.assertEqual(10_000, step)

    def test_empty_series_has_safe_scale(self):
        self.assertEqual((1.0, 0.2), nice_axis_scale([]))

    def test_compact_labels_use_dutch_decimal_separator(self):
        self.assertEqual("200k", compact_number(200_000))
        self.assertEqual("1,2M", compact_number(1_200_000))

    def test_dominance_requires_two_consecutive_observations(self):
        self.assertEqual(
            ["", "XFG", "XFG", "", "JN.1", "JN.1"],
            confirmed_dominance(["XFG", "XFG", "XFG", "JN.1", "JN.1", "JN.1"]),
        )


if __name__ == "__main__":
    unittest.main()
