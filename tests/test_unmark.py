"""
Unit Tests for Unmark.
"""

import os
import unittest
from unmark.metrics import compute_char_f1, compute_semantic_preservation


class TestUnmarkMetrics(unittest.TestCase):
    def test_char_f1_exact_match(self):
        text = "人工智能正在深刻改变世界"
        f1 = compute_char_f1(text, text)
        self.assertAlmostEqual(f1, 1.0, places=2)

    def test_semantic_preservation(self):
        orig = "今天周末阳光明媚，我在阳台上喝咖啡看风景。"
        scrubbed = "在明媚的周末，我坐在阳台品尝咖啡，欣赏外面的景致。"
        metrics = compute_semantic_preservation(orig, scrubbed)
        self.assertGreater(metrics["char_f1"], 50.0)
        self.assertGreater(metrics["similarity_score"], 30.0)


if __name__ == "__main__":
    unittest.main()
