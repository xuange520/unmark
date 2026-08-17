"""
Layer A: Deterministic Unicode & Invisible Character Sanitizer for Unmark.

This module detects and purges hidden tracking characters, zero-width spaces,
bidirectional (bidi) control overrides, invisible Unicode tags, and soft hyphens
commonly used for covert physical watermarking and origin tracking.
"""

from typing import Any, Dict, List, Tuple
import re

# Precise Unicode character sets for covert provenance tracking
INVISIBLE_CHAR_PATTERNS: Dict[str, str] = {
    "zero_width_spaces": r"[\u200B\u200C\u200D\uFEFF]",
    "bidi_controls": r"[\u200E\u200F\u202A-\u202E\u2066-\u2069]",
    "soft_hyphens": r"[\u00AD]",
    "unicode_tag_chars": r"[\U000E0001-\U000E007F]",
    "invisible_separators": r"[\u2060-\u2064\u206A-\u206F]",
}

COMBINED_INVISIBLE_REGEX = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in INVISIBLE_CHAR_PATTERNS.items())
)


def inspect_text_anomalies(text: str) -> Dict[str, Any]:
    """Scans text for covert invisible characters and anomaly indicators.

    Args:
        text: Input string to inspect.

    Returns:
        Dict containing anomaly flags, character counts, and locations.
    """
    counts: Dict[str, int] = {k: 0 for k in INVISIBLE_CHAR_PATTERNS}
    total_invisible = 0
    positions: List[Dict[str, Any]] = []

    for match in COMBINED_INVISIBLE_REGEX.finditer(text):
        for name, pattern in INVISIBLE_CHAR_PATTERNS.items():
            if match.group(name) is not None:
                counts[name] += 1
                total_invisible += 1
                positions.append(
                    {
                        "category": name,
                        "char_repr": repr(match.group(name)),
                        "index": match.start(),
                    }
                )
                break

    return {
        "has_invisible_marks": total_invisible > 0,
        "total_invisible_chars": total_invisible,
        "category_breakdown": counts,
        "sample_locations": positions[:20],  # Return up to 20 for preview
    }


def sanitize_text(text: str, normalize_whitespace: bool = False) -> Tuple[str, Dict[str, Any]]:
    """Deterministically strips all hidden tracking marks and zero-width characters.

    Args:
        text: Input text containing possible covert characters.
        normalize_whitespace: If True, normalizes exotic whitespace (e.g. non-breaking spaces)
            to standard ASCII spaces.

    Returns:
        Tuple of (clean_text, anomaly_report)
    """
    report = inspect_text_anomalies(text)

    # Fast path if no invisible characters are present
    if not report["has_invisible_marks"]:
        clean_text = text
    else:
        clean_text = COMBINED_INVISIBLE_REGEX.sub("", text)

    if normalize_whitespace:
        # Normalize non-breaking spaces (\u00A0), en/em spaces (\u2000-\u200A), ideographic spaces (\u3000)
        clean_text = re.sub(r"[\u00A0\u2000-\u200A\u202F\u205F\u3000]", " ", clean_text)

    return clean_text, report
