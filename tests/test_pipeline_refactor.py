import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from modules.brondata import dateCache
from modules.buildtime import reference_datetime
from pipeline.calculations import calculate_cumulative_totals
from pipeline.legacy_transform import transform_prevalence, transform_rivm_tests
from pipeline.site_export import build_surveillance_export
from createZiekGraph import select_date_range
from createRtGraph import select_rt_date_range
from createCovidTestsGraph import select_test_date_range
from createHeatmap import select_age_date_range


def record():
    return {
        "positief": 0, "nu_opgenomen": 0, "overleden": 0,
        "rivm_schatting_besmettelijk": {"min": None, "max": None, "value": None},
    }


class PipelineRefactorTest(unittest.TestCase):
    def test_date_parser_sanitizes_and_reuses_dates(self):
        first = dateCache.parse("2020-03-01T10:30:00Z")
        second = dateCache.parse("2020-03-01")
        self.assertEqual("2020-03-01", dateCache.sanitizeDate("2020-03-01T10:30:00Z"))
        self.assertEqual(first.date(), second.date())

    def test_fixture_transform_merges_without_discarding_existing_fields(self):
        daily = {"2020-03-01": record() | {"preserved": 42}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "prevalence.json"
            path.write_text(json.dumps([{"Date": "2020-03-01", "prev_low": "10", "prev_up": "30", "prev_avg": "20"}]))
            report = transform_prevalence(path, daily)
        self.assertEqual(3, report.observations_written)
        self.assertEqual(42, daily["2020-03-01"]["preserved"])
        self.assertEqual(20, daily["2020-03-01"]["rivm_schatting_besmettelijk"]["value"])

    def test_source_transform_aggregates_rows_by_date(self):
        daily = {}
        def ensure(date):
            return daily.setdefault(date, record())
        fixture = [
            {"Date_of_statistics": "2020-03-01", "Tested_with_result": 10, "Tested_positive": 2},
            {"Date_of_statistics": "2020-03-01", "Tested_with_result": 5, "Tested_positive": 1},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tests.json"
            path.write_text(json.dumps(fixture))
            transform_rivm_tests(path, daily, ensure)
        self.assertEqual(15, daily["2020-03-01"]["rivm_totaal_tests"])
        self.assertEqual(3, daily["2020-03-01"]["rivm_totaal_tests_positief"])

    def test_cumulative_calculation_is_deterministic(self):
        daily = {"2020-03-01": record(), "2020-03-02": record()}
        daily["2020-03-01"].update(positief=2, nu_opgenomen=1)
        daily["2020-03-02"].update(positief=3, overleden=1)
        first, second = copy.deepcopy(daily), copy.deepcopy(daily)
        calculate_cumulative_totals(first)
        calculate_cumulative_totals(second)
        self.assertEqual(first, second)
        self.assertEqual(5, first["2020-03-02"]["totaal_positief"])

    def test_project_paths_do_not_depend_on_current_directory(self):
        from modules.defaults import DAILY_STATS
        self.assertEqual(PROJECT_ROOT / "data/daily-stats.json", DAILY_STATS)

    def test_site_export_labels_reported_and_calculated_series(self):
        daily = {
            "2024-01-01": {
                "RNA": {"RNA_per_100k_avg": 120, "besmettelijk": 4500}
            },
            "2024-01-02": {
                "RNA": {"RNA_per_100k_avg": 0, "besmettelijk": None}
            },
        }
        export = build_surveillance_export(daily)
        self.assertEqual("2024-01-01", export["newest_observation"])
        self.assertEqual(["reported", "calculated"], [item["status"] for item in export["series"]])
        self.assertEqual(1, len(export["observations"]))

    def test_render_time_is_based_on_newest_observation(self):
        daily = {"2020-01-01": {}, "2024-05-06": {}}
        self.assertEqual("2024-05-06T12:00:00", reference_datetime(daily).isoformat())

    def test_short_hospital_chart_ends_at_last_hospital_observation(self):
        daily = {
            "2024-01-01": {"nu_opgenomen": 10, "nu_op_ic": 2},
            "2024-01-02": {"nu_opgenomen": 0, "nu_op_ic": 0},
            "2025-01-01": {"nu_opgenomen": 0, "nu_op_ic": 0},
        }
        selected = select_date_range(daily, 365)
        self.assertEqual("2024-01-01", selected[-1].strftime("%Y-%m-%d"))

    def test_short_rt_chart_ends_at_last_rt_observation(self):
        daily = {
            "2023-07-09": {"Rt_avg": None, "Rt_low": 0.1, "Rt_up": 0.3},
            "2023-07-10": {"Rt_avg": None, "Rt_low": None, "Rt_up": None},
            "2025-01-01": {"Rt_avg": None, "Rt_low": None, "Rt_up": None},
        }
        selected = select_rt_date_range(daily, 365)
        self.assertEqual("2023-07-09", selected[-1].strftime("%Y-%m-%d"))

    def test_short_test_chart_ends_at_last_test_observation(self):
        daily = {
            "2023-03-17": {"rivm_totaal_tests": 100},
            "2023-03-18": {"rivm_totaal_tests": None},
            "2025-01-01": {"rivm_totaal_tests": None},
        }
        selected = select_test_date_range(daily, 365)
        self.assertEqual("2023-03-17", selected[-1].strftime("%Y-%m-%d"))

    def test_full_test_chart_ends_at_last_test_observation(self):
        daily = {
            "2023-03-17": {"rivm_totaal_tests": 100},
            "2025-01-01": {"rivm_totaal_tests": None},
        }
        selected = select_test_date_range(daily, 0)
        self.assertEqual("2023-03-17", selected[-1].strftime("%Y-%m-%d"))

    def test_short_age_chart_ends_at_last_age_observation(self):
        daily = {
            "2023-04-04": {"besmettingleeftijd": {"65": 3}},
            "2023-04-05": {"besmettingleeftijd": {"65": 0}},
            "2025-01-01": {"besmettingleeftijd": {}},
        }
        selected = select_age_date_range(daily, 365)
        self.assertEqual("2023-04-04", selected[-1].strftime("%Y-%m-%d"))

    def test_full_age_chart_ends_at_last_age_observation(self):
        daily = {
            "2023-04-04": {"besmettingleeftijd": {"65": 3}},
            "2025-01-01": {"besmettingleeftijd": {}},
        }
        selected = select_age_date_range(daily, 0)
        self.assertEqual("2023-04-04", selected[-1].strftime("%Y-%m-%d"))


if __name__ == "__main__":
    unittest.main()
