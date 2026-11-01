import io
from email.message import Message
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from pipeline.download import fetch_json_source
from pipeline.infectieradar_ari import parse


FIXTURE = PROJECT_ROOT / "tests" / "fixtures" / "infectieradar-ari.json"


class FakeResponse(io.BytesIO):
    def __init__(self, content, content_type="application/json", status=200):
        super().__init__(content)
        self.status = status
        self.headers = Message()
        self.headers["Content-Type"] = content_type

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class SourceDownloadTest(unittest.TestCase):
    def test_valid_download_is_atomic_snapshotted_and_idempotent(self):
        content = FIXTURE.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "cache" / "ari.json"
            snapshots = root / "raw"

            with patch(
                "pipeline.download.urllib.request.urlopen",
                side_effect=lambda *_args, **_kwargs: FakeResponse(content),
            ):
                first = self._fetch(target, snapshots)
                second = self._fetch(target, snapshots)

            self.assertTrue(first.changed)
            self.assertFalse(second.changed)
            self.assertEqual(content, target.read_bytes())
            self.assertEqual(first.snapshot, second.snapshot)
            self.assertEqual(0o444, first.snapshot.stat().st_mode & 0o777)

    def test_wrong_content_type_does_not_replace_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "ari.json"
            target.write_text("preserved")
            with patch(
                "pipeline.download.urllib.request.urlopen",
                return_value=FakeResponse(b"<html>error</html>", "text/html"),
            ):
                with self.assertRaisesRegex(ValueError, "expected JSON content type"):
                    self._fetch(target, root / "raw")
            self.assertEqual("preserved", target.read_text())

    @staticmethod
    def _fetch(target, snapshots):
        return fetch_json_source(
            source_id="rivm_infectieradar_ari",
            url="https://example.invalid/ari.json",
            target=target,
            snapshot_root=snapshots,
            parser=parse,
            minimum_bytes=10,
        )


if __name__ == "__main__":
    unittest.main()
