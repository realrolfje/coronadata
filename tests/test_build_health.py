import sys
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from checkBuildHealth import classify


class BuildHealthTest(unittest.TestCase):
    def test_active_source_failure_blocks_publication(self):
        blocking, warnings = classify(
            ["Problem opening 'https://data.rivm.nl/example.json': http error 500"]
        )
        self.assertEqual(1, len(blocking))
        self.assertEqual([], warnings)

    def test_retired_nice_failure_is_a_warning(self):
        error = (
            "Problem opening "
            "'https://www.stichting-nice.nl/covid-19/public/intake-count/': "
            "http error 404"
        )
        blocking, warnings = classify([error])
        self.assertEqual([], blocking)
        self.assertEqual([error], warnings)

    def test_historical_data_warning_does_not_block(self):
        warning = "Percentages niet compleet voor 2020-12-14"
        blocking, warnings = classify([warning])
        self.assertEqual([], blocking)
        self.assertEqual([warning], warnings)


if __name__ == "__main__":
    unittest.main()
