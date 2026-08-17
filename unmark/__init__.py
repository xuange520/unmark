"""
Unmark: Semantics-preserving statistical LLM watermark removal & evaluation toolkit.
"""

from unmark.detector import WatermarkDetector, evaluate_watermark
from unmark.metrics import compute_char_f1, compute_semantic_preservation
from unmark.sanitizer import inspect_text_anomalies, sanitize_text
from unmark.scrubber import UnmarkEngine

__version__ = "0.2.0"
__author__ = "Jay"
__license__ = "Apache-2.0"

__all__ = [
    "UnmarkEngine",
    "WatermarkDetector",
    "evaluate_watermark",
    "sanitize_text",
    "inspect_text_anomalies",
    "compute_semantic_preservation",
    "compute_char_f1",
]
