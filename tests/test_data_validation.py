import unittest
from pathlib import Path

from data_validation import validate_cases, validate_diagnostic_responses, validate_review_log

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class DataValidationTests(unittest.TestCase):
    def test_canonical_project_data_is_valid(self):
        self.assertEqual(validate_cases(PROJECT_ROOT / "cases.csv"), [])
        self.assertEqual(validate_diagnostic_responses(PROJECT_ROOT / "ai_responses.csv"), [])
        self.assertEqual(validate_review_log(PROJECT_ROOT / "responsible_ai_log.csv"), [])

    def test_rejects_cases_with_invalid_severity(self):
        errors = validate_cases(PROJECT_ROOT / "tests/fixtures/cases_invalid_severity.csv")
        self.assertTrue(any("invalid severity" in error for error in errors))

    def test_rejects_review_log_with_unknown_decision(self):
        errors = validate_review_log(PROJECT_ROOT / "tests/fixtures/review_invalid_decision.csv")
        self.assertTrue(any("invalid human_decision" in error for error in errors))

    def test_rejects_response_missing_required_field(self):
        errors = validate_diagnostic_responses(PROJECT_ROOT / "tests/fixtures/response_missing_evidence.csv")
        self.assertTrue(any("evidence must not be empty" in error for error in errors))
