"""
Unmark: A semantics-preserving toolkit for removing and evaluating statistical LLM text watermarks.
"""

__version__ = "0.1.0"
__author__ = "Jay <xuangeylw@gmail.com>"
__license__ = "Apache-2.0"

from unmark.detector import WatermarkDetector, evaluate_watermark
from unmark.metrics import compute_semantic_preservation
from unmark.scrubber import UnmarkEngine

__all__ = [
    "UnmarkEngine",
    "WatermarkDetector",
    "evaluate_watermark",
    "compute_semantic_preservation",
]
