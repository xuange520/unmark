"""
Command-Line Interface (CLI) for Unmark.
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
from unmark.scrubber import UnmarkEngine


def main():
    parser = argparse.ArgumentParser(
        description="Unmark: Semantics-preserving statistical LLM watermark removal & evaluation tool."
    )
    parser.add_argument(
        "--model",
        type=str,
        default="d:\\源码\\Python\\SynthID-Text\\qwen_local",
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
        "--style",
        type=str,
        choices=["standard", "academic", "fluent"],
        default="standard",
        help="Paraphrasing style to apply.",
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
        with open(args.input, "r", encoding="utf-8") as f:
            input_text = f.read()
    else:
        print("Please provide --text or --input file. Type --help for usage.")
        sys.exit(0)

    print("=" * 70)
    print("        Unmark: LLM Text Watermark Scrubber & Evaluator")
    print("=" * 70)
    print(f"[*] Loading model from: {args.model} ...")
    
    t0 = time.time()
    engine = UnmarkEngine(model_path_or_name=args.model)
    detector = WatermarkDetector(model_path_or_name=args.model)
    print(f"[+] Model loaded successfully in {time.time() - t0:.2f}s.\n")

    print("--- [Original Input Text] ---")
    print(input_text.strip()[:300] + ("..." if len(input_text) > 300 else ""))
    print()

    # Pre-evaluation
    res_before = None
    if args.eval:
        res_before = detector.detect(input_text)
        print(f"[*] Watermark Check (Before Scrubbing):")
        print(f"    - g-value Mean : {res_before['mean_g']:.4f}")
        print(f"    - Z-Score      : {res_before['z_score']:+.2f}")
        print(f"    - Status       : {res_before['verdict']}\n")

    # Scrubbing
    print(f"[*] Scrubbing watermarks using [{args.style}] style ...")
    t_start = time.time()
    scrubbed = engine.scrub(input_text, style=args.style)
    duration = time.time() - t_start
    print(f"[+] Scrubbed in {duration:.2f}s.\n")

    print("--- [De-watermarked Text] ---")
    print(scrubbed)
    print()

    # Post-evaluation
    if args.eval:
        res_after = detector.detect(scrubbed)
        metrics = compute_semantic_preservation(input_text, scrubbed)

        print("=" * 70)
        print("                      Evaluation Summary")
        print("=" * 70)
        print(f"{'Stage':<18} | {'g-value Mean':<12} | {'Z-Score':<10} | {'Verdict'}")
        print("-" * 70)
        print(f"{'1. Before Scrub':<18} | {res_before['mean_g']:<12.4f} | {res_before['z_score']:<+10.2f} | {res_before['verdict']}")
        print(f"{'2. After Scrub':<18} | {res_after['mean_g']:<12.4f} | {res_after['z_score']:<+10.2f} | {res_after['verdict']}")
        print("=" * 70)
        print(f"📊 Semantic Preservation : {metrics['similarity_score']}% (Char F1: {metrics['char_f1']}%)")
        print(f"📉 Z-Score Drop          : {res_before['z_score'] - res_after['z_score']:+.2f}")
        print("=" * 70)

    # Save to output file if requested
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(scrubbed)
        print(f"[+] Saved de-watermarked text to: {args.output}")


if __name__ == "__main__":
    main()
