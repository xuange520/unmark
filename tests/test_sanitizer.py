"""
Unit tests for Layer A: Deterministic Unicode & Invisible Character Sanitizer.
"""

import unittest
from unmark.sanitizer import inspect_text_anomalies, sanitize_text


class TestSanitizer(unittest.TestCase):
    def test_clean_text_no_anomalies(self):
        text = "This is a clean sentence without any hidden characters."
        report = inspect_text_anomalies(text)
        self.assertFalse(report["has_invisible_marks"])
        self.assertEqual(report["total_invisible_chars"], 0)

        cleaned, clean_report = sanitize_text(text)
        self.assertEqual(cleaned, text)
        self.assertEqual(clean_report["total_invisible_chars"], 0)

    def test_zero_width_space_stripping(self):
        # Injected with zero-width space (\u200B), ZWNJ (\u200C), ZWJ (\u200D), BOM (\uFEFF)
        text = "人\u200B工\u200C智\u200D能\uFEFF技术"
        report = inspect_text_anomalies(text)
        self.assertTrue(report["has_invisible_marks"])
        self.assertEqual(report["total_invisible_chars"], 4)

        cleaned, clean_report = sanitize_text(text)
        self.assertEqual(cleaned, "人工智能技术")
        self.assertEqual(clean_report["total_invisible_chars"], 4)

    def test_bidi_controls_and_soft_hyphens(self):
        # Injected with LTR/RTL marks (\u200E, \u200F), bidi override (\u202E), soft hyphen (\u00AD)
        text = "Secret\u200EMark\u200FData\u202EText\u00ADEnd"
        cleaned, report = sanitize_text(text)
        self.assertEqual(cleaned, "SecretMarkDataTextEnd")
        self.assertEqual(report["total_invisible_chars"], 4)


if __name__ == "__main__":
    unittest.main()
