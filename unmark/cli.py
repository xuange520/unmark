"""
Command-Line Interface (CLI) for Unmark v0.2.0.
"""

import argparse
import os
import sys
import time

# Ensure project root is in sys.path for standalone script execution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    sys.stdout.reconfigure(line_buffering=True, encoding="utf-8")
except Exception:
    pass

from unmark.detector import WatermarkDetector
from unmark.metrics import compute_semantic_preservation
from unmark.sanitizer import inspect_text_anomalies, sanitize_text
from unmark.scrubber import UnmarkEngine


def main():
    parser = argparse.ArgumentParser(
        description="Unmark v0.2.0: Dual-Layer Semantics-Preserving LLM Watermark Removal & Safety Evaluation Toolkit."
    )
    parser.add_argument(
        "--model",
        type=str,
        default=os.path.join(project_root, "qwen_local"),
        help="Path or HuggingFace repo ID of the model to use for de-watermarking.",
    )
    parser.add_argument(
        "--text",
        type=str,
        default=None,
        help="Input text string to scrub.",
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Input file path (.txt / .md).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path to save scrubbed text.",
    )
    parser.add_argument(
        "--layer",
        type=str,
        choices=["all", "layer-a", "layer-b"],
        default="all",
        help="Cleaning layer to run: 'all' (Layer A + Layer B), 'layer-a' (invisible Unicode only), 'layer-b' (statistical LLM only).",
    )
    parser.add_argument(
        "--style",
        type=str,
        choices=["standard", "academic", "fluent"],
        default="standard",
        help="Paraphrasing style to apply for Layer B.",
    )
    parser.add_argument(
        "--eval",
        action="store_true",
        default=True,
        help="Evaluate watermark Z-score before and after scrubbing.",
    )

    args = parser.parse_args()

    # Read input text
    input_text = ""
    if args.text:
        input_text = args.text
    elif args.input:
        if not os.path.exists(args.input):
            print(f"[!] Input file not found: {args.input}")
            sys.exit(1)
        with open(args.input, "r", encoding="utf-8", errors="ignore") as f:
            input_text = f.read()
    else:
        print("Please provide --text or --input file. Type --help for usage.")
        sys.exit(0)

    print("=" * 75)
    print("      Unmark v0.2.0: Dual-Layer LLM Watermark & Provenance Scrubber")
    print("=" * 75)

    # 1. Inspect Layer A Anomaly
    anomalies = inspect_text_anomalies(input_text)
    print(f"[*] Layer A Status: Found {anomalies['total_invisible_chars']} invisible/tracking character(s).")
    if anomalies["has_invisible_marks"]:
        for k, v in anomalies["category_breakdown"].items():
            if v > 0:
                print(f"    - {k}: {v}")
    print()

    # Fast path: Layer A only
    if args.layer == "layer-a":
        print("[*] Running Layer A (Deterministic Unicode Sanitization) only...")
        clean_text, report = sanitize_text(input_text)
        print(f"[+] Purged {report['total_invisible_chars']} hidden mark(s).\n")
        print("--- [Sanitized Text] ---")
        print(clean_text)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(clean_text)
            print(f"\n[+] Saved to {args.output}")
        return

    # Load models for Layer B or Full Dual-Layer
    print(f"[*] Loading model backend from: {args.model} ...")
    t0 = time.time()
    engine = UnmarkEngine(model_path_or_name=args.model)
    detector = WatermarkDetector(model_path_or_name=args.model) if args.eval else None
    print(f"[+] Model loaded in {time.time() - t0:.2f}s.\n")

    # Pre-evaluation
    res_before = None
    if args.eval and detector:
        res_before = detector.detect(input_text)
        print(f"[*] Statistical Watermark Check (Before Scrubbing):")
        print(f"    - g-value Mean : {res_before['mean_g']:.4f}")
        print(f"    - Z-Score      : {res_before['z_score']:+.2f}")
        print(f"    - Status       : {res_before['verdict']}\n")

    # Scrubbing
    sanitize_first = args.layer == "all"
    print(f"[*] Executing {'Dual-Layer (A+B)' if sanitize_first else 'Layer B'} Scrubbing [{args.style}] ...")
    t_start = time.time()
    scrubbed = engine.scrub(
        input_text,
        style=args.style,
        sanitize_first=sanitize_first,
    )
    duration = time.time() - t_start
    print(f"[+] Completed in {duration:.2f}s.\n")

    print("--- [Purified Final Text] ---")
    print(scrubbed)
    print()

    # Post-evaluation
    if args.eval and detector and res_before:
        res_after = detector.detect(scrubbed)
        metrics = compute_semantic_preservation(input_text, scrubbed)

        print("=" * 75)
        print("                         Evaluation Summary")
        print("=" * 75)
        print(f"{'Stage':<20} | {'g-value Mean':<12} | {'Z-Score':<10} | {'Verdict'}")
        print("-" * 75)
        print(f"{'1. Original Input':<20} | {res_before['mean_g']:<12.4f} | {res_before['z_score']:<+10.2f} | {res_before['verdict']}")
        print(f"{'2. After Unmark':<20} | {res_after['mean_g']:<12.4f} | {res_after['z_score']:<+10.2f} | {res_after['verdict']}")
        print("=" * 75)
        print(f"📊 Semantic Preservation : {metrics['similarity_score']}% (Char F1: {metrics['char_f1']}%)")
        print(f"📉 Z-Score Drop          : {res_before['z_score'] - res_after['z_score']:+.2f}")
        print(f"🧹 Layer A Purged        : {anomalies['total_invisible_chars']} invisible character(s)")
        print("=" * 75)

    # Save to output file if requested
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(scrubbed)
        print(f"\n[+] Saved purified text to: {args.output}")


if __name__ == "__main__":
    main()
