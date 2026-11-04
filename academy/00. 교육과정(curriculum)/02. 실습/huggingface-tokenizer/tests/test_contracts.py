"""Input/error/artifact tests only. These do not simulate a real tokenizer run."""
import copy
import importlib.util
import json
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("inspect_tokenizer", ROOT / "inspect_tokenizer.py")
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class Contracts(unittest.TestCase):
    def altered(self, source, edit, loader):
        content = lab.read_json(ROOT / source)
        edit(content)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.json"
            path.write_text(json.dumps(content), encoding="utf-8")
            return loader(path)

    def test_default_inputs_and_immutable_profiles(self):
        self.assertEqual(len(lab.load_inputs(ROOT / "inputs.json")["samples"]), 3)
        for name in ["qwen", "smol"]:
            self.assertEqual(len(lab.load_profile(ROOT / "models.json", name)["revision"]), 40)

    def test_branch_revision_rejected(self):
        with self.assertRaisesRegex(ValueError, "immutable"):
            self.altered("models.json", lambda d: d["profiles"][0].update(revision="main"), lambda p: lab.load_profile(p, "qwen"))

    def test_profile_duplicates_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self.altered("models.json", lambda d: d["profiles"].append(copy.deepcopy(d["profiles"][0])), lambda p: lab.load_profile(p, "qwen"))

    def test_unknown_profile_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown"):
            lab.load_profile(ROOT / "models.json", "missing")

    def test_sample_duplicate_rejected(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            self.altered("inputs.json", lambda d: d["samples"].append(copy.deepcopy(d["samples"][0])), lab.load_inputs)

    def test_empty_sample_rejected(self):
        with self.assertRaisesRegex(ValueError, "characters"):
            self.altered("inputs.json", lambda d: d["samples"][0].update(text=""), lab.load_inputs)

    def test_unknown_role_rejected(self):
        with self.assertRaisesRegex(ValueError, "roles"):
            self.altered("inputs.json", lambda d: d["messages"][0].update(role="tool"), lab.load_inputs)

    def test_last_role_must_be_user(self):
        with self.assertRaisesRegex(ValueError, "user message"):
            self.altered("inputs.json", lambda d: d["messages"][-1].update(role="assistant"), lab.load_inputs)

    def test_preflight_never_imports_or_loads_tokenizer(self):
        output = StringIO()
        with patch.object(lab, "load_real_tokenizer", side_effect=AssertionError("must not load")), redirect_stdout(output):
            code = lab.main(["--preflight"])
        result = json.loads(output.getvalue())
        self.assertIn(code, (0, 2))
        self.assertFalse(result["tokenizer_executed"])
        self.assertFalse(result["network_used"])

    def test_missing_template_dependency_is_detected(self):
        def version(package):
            if package == "jinja2":
                raise lab.importlib.metadata.PackageNotFoundError(package)
            return lab.DEPENDENCIES[package]
        with patch.object(lab.importlib.metadata, "version", side_effect=version):
            status = lab.dependency_status()
        self.assertFalse(status["jinja2"]["matches"])
        self.assertIsNone(status["jinja2"]["installed"])

    def test_missing_setup_never_writes_success(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(lab, "load_real_tokenizer", side_effect=lab.SetupRequired("dependency missing")), redirect_stderr(StringIO()):
            out = Path(tmp) / "run"
            self.assertEqual(lab.main(["--output", str(out)]), 2)
            self.assertFalse(out.exists())

    def test_existing_evidence_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(lab, "load_real_tokenizer", side_effect=AssertionError("must not load")), redirect_stderr(StringIO()):
            out = Path(tmp)
            (out / "observations.md").write_text("original", encoding="utf-8")
            self.assertEqual(lab.main(["--output", str(out)]), 2)
            self.assertEqual((out / "observations.md").read_text(), "original")

    def test_invalid_max_length_stops_before_loading(self):
        with patch.object(lab, "load_real_tokenizer", side_effect=AssertionError("must not load")), redirect_stderr(StringIO()):
            self.assertEqual(lab.main(["--max-length", "0", "--output", "unused"]), 2)

    def test_missing_output_stops_before_loading(self):
        with patch.object(lab, "load_real_tokenizer", side_effect=AssertionError("must not load")), redirect_stderr(StringIO()):
            self.assertEqual(lab.main([]), 2)

    def observed_qwen(self, max_length):
        # Real recorded observation from this verification run, not a tokenizer stub.
        import os
        base = os.environ.get("KEDU_OBSERVATIONS", str(ROOT.parents[1] / "reports/KEDU-PRODUCTION-001/runtime"))
        if not Path(base).is_dir():
            self.skipTest("Set KEDU_OBSERVATIONS to the real Qwen observation directory")
        return lab.read_json(Path(base) / ("qwen-01" if max_length == 8 else "qwen-length16-fixed") / "observations.json")

    def test_real_observation_with_truncation(self):
        self.assertEqual(lab.check_observation(self.observed_qwen(8)), [])

    def test_real_observation_fitting_limit_is_valid(self):
        self.assertEqual(lab.check_observation(self.observed_qwen(16)), [])

    def test_corrupted_truncation_flag_is_rejected(self):
        data = self.observed_qwen(16)
        data["samples"][0]["was_truncated"] = True
        self.assertTrue(any("Truncation behavior" in error for error in lab.check_observation(data)))


if __name__ == "__main__":
    unittest.main()
