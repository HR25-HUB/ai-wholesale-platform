"""Run without third-party packages: python -m unittest discover -s tests/architecture."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).resolve().parents[2] / "scripts" / "check_architecture.py"
spec = importlib.util.spec_from_file_location("apd_arch_checker", CHECKER)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
POLICY = json.loads((Path(__file__).resolve().parents[2] / "architecture/policies/dependency-rules.json").read_text())


class ArchitectureRuleTests(unittest.TestCase):
    def check_source(self, source: str):
        with tempfile.TemporaryDirectory() as tmp:
            domain = Path(tmp) / "app" / "domain"
            domain.mkdir(parents=True)
            (domain / "rfq.py").write_text(source, encoding="utf-8")
            return checker.check(Path(tmp), POLICY)

    def test_allowed_pydantic_import(self):
        self.assertEqual(self.check_source("from pydantic import BaseModel\n"), [])

    def test_forbidden_prefect_import(self):
        findings = self.check_source("from prefect import flow\n")
        self.assertEqual(len(findings), 1)
        self.assertIn("prefect", findings[0]["reason"])

    def test_forbidden_app_delivery_import(self):
        self.assertEqual(len(self.check_source("from app.main import app\n")), 1)

    def test_forbidden_relative_import(self):
        self.assertEqual(len(self.check_source("from ..main import app\n")), 1)

    def test_syntax_error_fails_closed(self):
        self.assertEqual(len(self.check_source("def broken(:\n")), 1)


if __name__ == "__main__":
    unittest.main()
