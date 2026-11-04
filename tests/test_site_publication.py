from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from buildSiteData import public_report, status_page


class SitePublicationTest(unittest.TestCase):
    def test_public_health_report_omits_machine_specific_fields(self):
        report = {
            "created_at": "changes every build",
            "status": "healthy",
            "sources": [{
                "id": "source", "name": "Source", "provider": "Provider",
                "lifecycle": "active", "required_for_publish": True,
                "record_count": 2, "publication_date": "2024-01-02",
                "newest_observation": "2024-01-01", "health": "healthy",
                "messages": [], "blocking": False, "cache_path": "/private/path",
                "cache_modified_at": "changes", "cache_size": 10,
            }],
        }
        public = public_report(report)
        self.assertNotIn("created_at", public)
        self.assertNotIn("cache_path", public["sources"][0])
        self.assertEqual("2024-01-02", public["newest_source_date"])

    def test_status_page_escapes_source_messages(self):
        report = {
            "status": "blocked",
            "sources": [{
                "id": "source", "name": "Source", "health": "invalid",
                "lifecycle": "active", "newest_observation": None,
                "publication_date": None, "messages": ["<script>bad()</script>"],
            }],
        }
        page = status_page(report)
        self.assertNotIn("<script>bad()", page)
        self.assertIn("&lt;script&gt;bad()&lt;/script&gt;", page)


if __name__ == "__main__":
    unittest.main()
