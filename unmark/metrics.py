"""
Semantic Preservation & Text Quality Evaluation Metrics.
"""

from collections import Counter
import difflib
from typing import Any, Dict


def compute_char_f1(reference: str, candidate: str) -> float:
    """Computes character-level F1 score between reference and candidate texts."""
    ref_chars = Counter(reference.strip())
    cand_chars = Counter(candidate.strip())

    overlap = sum((ref_chars & cand_chars).values())
    total_ref = sum(ref_chars.values())
    total_cand = sum(cand_chars.values())

    if total_ref == 0 or total_cand == 0:
        return 0.0

    precision = overlap / total_cand
    recall = overlap / total_ref

    if precision + recall == 0:
        return 0.0
    return 2.0 * (precision * recall) / (precision + recall)


def compute_semantic_preservation(original: str, scrubbed: str) -> Dict[str, Any]:
    """
    Evaluates semantic similarity and structural preservation between original and scrubbed texts.

    Returns:
        Dictionary with similarity ratio, length ratio, and character overlap.
    """
    orig_clean = original.strip()
    scrub_clean = scrubbed.strip()

    if not orig_clean or not scrub_clean:
        return {
            "similarity_score": 0.0,
            "char_f1": 0.0,
            "length_ratio": 0.0,
            "status": "Empty text",
        }

    matcher = difflib.SequenceMatcher(None, orig_clean, scrub_clean)
    sim_ratio = matcher.ratio()
    char_f1 = compute_char_f1(orig_clean, scrub_clean)
    len_ratio = len(scrub_clean) / max(len(orig_clean), 1)

    return {
        "similarity_score": round(sim_ratio * 100, 2),
        "char_f1": round(char_f1 * 100, 2),
        "length_ratio": round(len_ratio, 3),
        "orig_char_count": len(orig_clean),
        "scrubbed_char_count": len(scrub_clean),
    }
