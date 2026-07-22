import json
import tempfile
import unittest
from pathlib import Path

from src.lad.provenance import record_downloaded_file, record_local_snapshot


class ProvenanceTests(unittest.TestCase):
    def test_records_downloaded_dataset_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir, "source.json")
            source.write_text('{"examples": []}\n', encoding="utf-8")
            manifest = Path(temp_dir, "manifest.jsonl")

            record = record_downloaded_file(
                file_path=source,
                manifest_path=manifest,
                artifact_type="dataset-source",
                name="example/task",
                source_url="https://example.test/task.json",
                revision="abc123",
                license_name="Apache-2.0",
                terms_url="https://example.test/LICENSE",
                access_timestamp="2026-07-22T00:00:00Z",
                download_command="download command",
                privacy_or_consent="public articles; no private records",
                redistribution="scripts and hashes only pending package terms",
            )

            self.assertEqual(record["bytes"], source.stat().st_size)
            self.assertEqual(len(record["sha256"]), 64)
            self.assertEqual(
                record["privacy_or_consent"], "public articles; no private records"
            )
            self.assertEqual(
                record["redistribution"],
                "scripts and hashes only pending package terms",
            )
            self.assertEqual(json.loads(manifest.read_text()), record)

    def test_records_every_file_size_and_checksum(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir, "snapshot")
            root.mkdir()
            Path(root, "config.json").write_text("{}\n", encoding="utf-8")
            Path(root, "weights.bin").write_bytes(b"weights")
            manifest = Path(temp_dir, "manifest.jsonl")

            record = record_local_snapshot(
                snapshot_dir=root,
                manifest_path=manifest,
                name="fake/model",
                source_url="https://example.test/fake/model",
                revision="abc123",
                license_name="MIT",
                terms_url="https://example.test/license",
                access_timestamp="2026-07-22T00:00:00Z",
            )

            saved = json.loads(manifest.read_text().strip())
            self.assertEqual(saved, record)
            self.assertEqual(saved["artifact_type"], "huggingface-model-snapshot")
            self.assertEqual(saved["revision"], "abc123")
            self.assertEqual(len(saved["files"]), 2)
            self.assertTrue(all(item["sha256"] for item in saved["files"]))
            self.assertEqual(
                saved["total_bytes"], sum(item["bytes"] for item in saved["files"])
            )


if __name__ == "__main__":
    unittest.main()
