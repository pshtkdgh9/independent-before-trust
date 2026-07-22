import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "extract_fever_source_pack.py"
)
_SPEC = importlib.util.spec_from_file_location("extract_fever_source_pack", _SCRIPT_PATH)
_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)

FeverSourcePackError = _MODULE.FeverSourcePackError
extract_fever_source_pack_result = _MODULE.extract_fever_source_pack_result
extract_fever_source_pack = _MODULE.extract_fever_source_pack


class ExtractFeverSourcePackTests(unittest.TestCase):
    def test_extracts_only_single_resolvable_evidence_rows_with_hashes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            claims = root / "paper_dev.jsonl"
            wiki_dir = root / "wiki-pages"
            wiki_dir.mkdir()
            _write_jsonl(
                wiki_dir / "wiki-001.jsonl",
                [
                    {
                        "id": "Ada_Lovelace",
                        "text": "Ada page.",
                        "lines": (
                            "0\tAda Lovelace was a mathematician.\tAda\tLovelace\n"
                            "1\tAda Lovelace wrote notes on the Analytical Engine.\tAnalytical Engine"
                        ),
                    },
                    {
                        "id": "Grace_Hopper",
                        "text": "Grace page.",
                        "lines": "0\tGrace Hopper worked on compilers.\tGrace",
                    },
                ],
            )
            _write_jsonl(
                wiki_dir / "wiki-002.jsonl",
                [{"id": "Unused_Page", "text": "Unused.", "lines": "0\tUnused sentence."}],
            )
            claim_rows = [
                {
                    "id": 11,
                    "verifiable": "VERIFIABLE",
                    "label": "SUPPORTS",
                    "claim": "Ada Lovelace wrote notes.",
                    "evidence": [[["ann", "e1", "Ada_Lovelace", 1]]],
                },
                {
                    "id": 12,
                    "label": "REFUTES",
                    "claim": "Grace Hopper avoided compilers.",
                    "evidence": [[["ann", "e2", "Grace_Hopper", 0]]],
                },
                {
                    "id": 13,
                    "label": "SUPPORTS",
                    "claim": "This has two evidence sets.",
                    "evidence": [
                        [["ann", "e3", "Ada_Lovelace", 0]],
                        [["ann", "e4", "Grace_Hopper", 0]],
                    ],
                },
                {
                    "id": 14,
                    "label": "NOT ENOUGH INFO",
                    "claim": "This has null evidence.",
                    "evidence": [[["ann", "e5", None, None]]],
                },
                {
                    "id": 15,
                    "label": "SUPPORTS",
                    "claim": "Missing page.",
                    "evidence": [[["ann", "e6", "Missing_Page", 0]]],
                },
            ]
            _write_jsonl(claims, claim_rows)

            rows = extract_fever_source_pack(claims, wiki_dir, limit=None, seed=123)

            self.assertEqual([row["source_row_id"] for row in rows], [11, 12])
            first = rows[0]
            self.assertEqual(first["source_pack_id"], "fever-paper-dev-11-Ada_Lovelace-1")
            self.assertEqual(first["label"], "SUPPORTS")
            self.assertEqual(first["claim"], "Ada Lovelace wrote notes.")
            self.assertEqual(
                first["evidence_sentence"],
                "Ada Lovelace wrote notes on the Analytical Engine.",
            )
            self.assertEqual(first["wiki_page_id"], "Ada_Lovelace")
            self.assertEqual(first["sentence_id"], 1)
            self.assertEqual(first["claim_hash"], _sha("Ada Lovelace wrote notes."))
            self.assertEqual(
                first["evidence_sentence_hash"],
                _sha("Ada Lovelace wrote notes on the Analytical Engine."),
            )
            self.assertIn("candidate_hash", first)
            self.assertNotIn("expected_action", first)
            self.assertNotIn("conflict_replacement_sentence", first)

    def test_retains_first_duplicate_claim_and_reports_skipped_duplicates(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            wiki_dir = root / "wiki-pages"
            wiki_dir.mkdir()
            _write_jsonl(
                wiki_dir / "wiki.jsonl",
                [
                    {"id": "First_Page", "text": "First.", "lines": "0\tFirst sentence."},
                    {"id": "Second_Page", "text": "Second.", "lines": "0\tSecond sentence."},
                ],
            )
            claims = root / "claims.jsonl"
            _write_jsonl(
                claims,
                [
                    {
                        "id": 1,
                        "label": "SUPPORTS",
                        "claim": "Duplicate claim.",
                        "evidence": [[["ann", "e1", "First_Page", 0]]],
                    },
                    {
                        "id": 2,
                        "label": "SUPPORTS",
                        "claim": "Duplicate claim.",
                        "evidence": [[["ann", "e2", "First_Page", 0]]],
                    },
                    _claim(3, "Unique claim.", "Second_Page"),
                ],
            )

            result = extract_fever_source_pack_result(claims, wiki_dir, limit=None, seed=0)

            self.assertEqual(result.summary["duplicates_skipped"], 1)
            self.assertEqual(result.summary["candidate_rows_written"], 2)
            self.assertEqual([row["source_row_id"] for row in result.rows], [1, 3])
            self.assertEqual(
                len({row["claim"] for row in result.rows}),
                len(result.rows),
            )

    def test_rejects_duplicate_source_row_ids_conflicting_duplicates_and_empty_evidence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            wiki_dir = root / "wiki-pages"
            wiki_dir.mkdir()
            _write_jsonl(
                wiki_dir / "wiki.jsonl",
                [
                    {"id": "Ada_Lovelace", "text": "Ada.", "lines": "0\t\t"},
                    {"id": "First_Page", "text": "First.", "lines": "0\tFirst sentence."},
                    {"id": "Second_Page", "text": "Second.", "lines": "0\tSecond sentence."},
                ],
            )
            claims = root / "claims.jsonl"
            _write_jsonl(
                claims,
                [
                    _claim(1, "Duplicate ID A.", "First_Page"),
                    _claim(1, "Duplicate ID B.", "First_Page"),
                ],
            )
            with self.assertRaisesRegex(FeverSourcePackError, "duplicate source row id"):
                extract_fever_source_pack(claims, wiki_dir, limit=None, seed=0)

            _write_jsonl(
                claims,
                [
                    _claim(2, "Conflicting duplicate.", "First_Page"),
                    _claim(3, "Conflicting duplicate.", "Second_Page"),
                ],
            )
            with self.assertRaisesRegex(
                FeverSourcePackError, "conflicting duplicate evidence mapping"
            ):
                extract_fever_source_pack(claims, wiki_dir, limit=None, seed=0)

            _write_jsonl(
                claims,
                [
                    {
                        "id": 3,
                        "label": "SUPPORTS",
                        "claim": "Empty evidence.",
                        "evidence": [[["ann", "e3", "Ada_Lovelace", 0]]],
                    }
                ],
            )
            with self.assertRaisesRegex(FeverSourcePackError, "empty evidence sentence"):
                extract_fever_source_pack(claims, wiki_dir, limit=None, seed=0)

    def test_cli_is_deterministic_limited_lf_and_atomic_on_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            wiki_dir = root / "wiki-pages"
            wiki_dir.mkdir()
            _write_jsonl(
                wiki_dir / "wiki.jsonl",
                [
                    {"id": "Page_A", "text": "A.", "lines": "0\tSentence A."},
                    {"id": "Page_B", "text": "B.", "lines": "0\tSentence B."},
                    {"id": "Page_C", "text": "C.", "lines": "0\tSentence C."},
                ],
            )
            claims = root / "claims.jsonl"
            _write_jsonl(
                claims,
                [
                    _claim(1, "Claim A.", "Page_A"),
                    _claim(2, "Claim B.", "Page_B"),
                    _claim(3, "Claim C.", "Page_C"),
                ],
            )
            output = root / "source-pack.jsonl"

            command = [
                sys.executable,
                "scripts/extract_fever_source_pack.py",
                "--claims",
                str(claims),
                "--wiki-dir",
                str(wiki_dir),
                "--output",
                str(output),
                "--limit",
                "2",
                "--seed",
                "7",
            ]
            first = subprocess.run(command, text=True, capture_output=True, check=False)
            first_bytes = output.read_bytes()
            second = subprocess.run(command, text=True, capture_output=True, check=False)

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(json.loads(first.stdout)["duplicates_skipped"], 0)
            self.assertEqual(json.loads(first.stdout)["candidate_rows_written"], 2)
            self.assertEqual(output.read_bytes(), first_bytes)
            self.assertEqual(first_bytes.count(b"\n"), 2)
            self.assertNotIn(b"\r\n", first_bytes)

            bad_claims = root / "bad-claims.jsonl"
            _write_jsonl(bad_claims, [_claim(4, "Missing.", "Missing_Page")])
            with output.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write("keep me\n")
            bad = subprocess.run(
                command[:3]
                + [str(bad_claims)]
                + command[4:],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("no extractable candidate rows", bad.stderr)
            self.assertEqual(output.read_text(encoding="utf-8"), "keep me\n")


def _write_jsonl(path, rows):
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def _claim(row_id, claim, page_id):
    return {
        "id": row_id,
        "label": "SUPPORTS",
        "claim": claim,
        "evidence": [[["ann", f"e{row_id}", page_id, 0]]],
    }


def _sha(text):
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    unittest.main()
