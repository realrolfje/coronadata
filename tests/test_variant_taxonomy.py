import json
from pathlib import Path
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from pipeline.variant_taxonomy import (
    ExclusiveVariantWeek,
    load_taxonomy,
    make_exclusive_week,
    pool_exclusive_weeks,
)
from validateVariantTaxonomy import validate


class VariantTaxonomyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.taxonomy = load_taxonomy(PROJECT_ROOT / "data/variant-taxonomy-v1.json")
        cls.fixture = json.loads(
            (PROJECT_ROOT / "tests/fixtures/variants-taxonomy.json").read_text()
        )

    def test_problematic_week_becomes_mutually_exclusive(self):
        records = [
            record for record in self.fixture
            if record["Date_of_statistics_week_start"] == "2025-03-10"
        ]
        result = make_exclusive_week(records, self.taxonomy)
        self.assertEqual(15, result.sample_size)
        self.assertEqual(15, result.total)
        self.assertEqual(6, result.counts["LP.8.1"])
        self.assertEqual(3, result.counts["JN.1"])
        self.assertEqual(1, result.counts["Recombinants"])
        self.assertNotIn("BA.2+S:L452X", result.counts)
        self.assertEqual((), result.unresolved_parents)

    def test_second_problematic_week_becomes_mutually_exclusive(self):
        records = [
            record for record in self.fixture
            if record["Date_of_statistics_week_start"] == "2025-02-17"
        ]
        result = make_exclusive_week(records, self.taxonomy)
        self.assertEqual(19, result.total)
        self.assertEqual(4, result.counts["LP.8.1"])
        self.assertEqual(4, result.counts["JN.1"])

    def test_recombinant_alias_is_attached_to_recombinant_aggregate(self):
        fixture = [
            {"Date_of_statistics_week_start":"2025-01-01","Variant_code":"Recombinants","Variant_cases":2,"Sample_size":2,"Is_subvariant_of":"","May_include_samples_listed_before":False},
            {"Date_of_statistics_week_start":"2025-01-01","Variant_code":"NB.1.8.1","Variant_cases":1,"Sample_size":2,"Is_subvariant_of":"","May_include_samples_listed_before":False},
        ]
        result = make_exclusive_week(fixture, self.taxonomy)
        self.assertEqual(1, result.counts["Recombinants"])
        self.assertEqual(1, result.counts["NB.1.8.1"])

    def test_missing_parent_is_explicitly_unresolved(self):
        fixture = [
            {"Date_of_statistics_week_start":"2025-01-01","Variant_code":"X.1","Variant_cases":1,"Sample_size":1,"Is_subvariant_of":"missing","May_include_samples_listed_before":False},
        ]
        result = make_exclusive_week(fixture, self.taxonomy)
        self.assertEqual(("X.1->missing",), result.unresolved_parents)

    def test_more_children_than_parent_is_rejected(self):
        fixture = [
            {"Date_of_statistics_week_start":"2025-01-01","Variant_code":"BA.2","Variant_cases":1,"Sample_size":2,"Is_subvariant_of":"","May_include_samples_listed_before":False},
            {"Date_of_statistics_week_start":"2025-01-01","Variant_code":"BA.2.86","Variant_cases":2,"Sample_size":2,"Is_subvariant_of":"BA.2","May_include_samples_listed_before":False},
        ]
        with self.assertRaisesRegex(ValueError, "more than parent count"):
            make_exclusive_week(fixture, self.taxonomy)

    def test_total_above_sample_size_is_rejected(self):
        fixture = [
            {"Date_of_statistics_week_start":"2025-01-01","Variant_code":"B.1.1.529","Variant_cases":2,"Sample_size":2,"Is_subvariant_of":"","May_include_samples_listed_before":False},
            {"Date_of_statistics_week_start":"2025-01-01","Variant_code":"Recombinants","Variant_cases":1,"Sample_size":2,"Is_subvariant_of":"","May_include_samples_listed_before":False},
        ]
        with self.assertRaisesRegex(ValueError, "exceeds sample size"):
            make_exclusive_week(fixture, self.taxonomy)

    def test_feed_validation_reports_invalid_week_without_raising(self):
        fixture = [
            {"Date_of_statistics_week_start":"2025-01-01","Variant_code":"B.1.1.529","Variant_cases":2,"Sample_size":2,"Is_subvariant_of":"","May_include_samples_listed_before":False},
            {"Date_of_statistics_week_start":"2025-01-01","Variant_code":"Recombinants","Variant_cases":1,"Sample_size":2,"Is_subvariant_of":"","May_include_samples_listed_before":False},
        ]
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "variants.json"
            source.write_text(json.dumps(fixture))
            report = validate(
                source, PROJECT_ROOT / "data/variant-taxonomy-v1.json"
            )
        self.assertEqual(1, report["week_count"])
        self.assertEqual(0, report["valid_week_count"])
        self.assertEqual("2025-01-01", report["invalid_weeks"][0]["date"])
        self.assertIn("exceeds sample size", report["invalid_weeks"][0]["error"])

    def test_four_week_pool_is_sample_weighted_and_filters_small_windows(self):
        weeks = [
            ExclusiveVariantWeek("2026-01-05", 2, {"XFG": 2}),
            ExclusiveVariantWeek("2026-01-12", 8, {"XFG": 4, "JN.1": 4}),
            ExclusiveVariantWeek("2026-01-19", 10, {"XFG": 2, "JN.1": 8}),
        ]
        pooled = pool_exclusive_weeks(weeks, minimum_samples=20)
        self.assertEqual(1, len(pooled))
        self.assertEqual(20, pooled[0].sample_size)
        self.assertEqual(8, pooled[0].counts["XFG"])
        self.assertEqual(12, pooled[0].counts["JN.1"])


if __name__ == "__main__":
    unittest.main()
