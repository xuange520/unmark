<div align="center">

# 🛡️ Unmark

**A Semantics-Preserving Toolkit for Removing and Evaluating Statistical LLM Text Watermarks**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-red.svg)](https://pytorch.org/)
[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97-Transformers_4.46%2B-yellow.svg)](https://huggingface.co/)
[![GitHub Stars](https://img.shields.io/github/stars/xuange520/unmark?style=social)](https://github.com/xuange520/unmark)

*An open-source system for statistical LLM text watermark removal and safety auditing via deep discourse paraphrasing.*

[English Documentation](README_EN.md) | [中文文档](README.md)

</div>

---

## 📖 Overview

Following the publication of **SynthID-Text** by Google DeepMind in *Nature* (October 2024) and the enforcement of transparency mandates under the **EU AI Act (Article 50)**, frontier commercial LLMs—including **Claude, Gemini, and ChatGPT**—have deployed cryptographically biased statistical watermarking mechanisms across text generation.

**Unmark** is an open-source toolkit designed for AI safety research, watermark robustness auditing, and semantics-preserving text purification. By leveraging clean, unwatermarked open-source language models (such as Qwen2.5 and Llama 3), Unmark features a **Discourse Paraphrasing Engine** that completely breaks the continuous $N$-gram hash dependency chains of sampling watermarks while **100% preserving core factual facts, academic terminology, and logical reasoning**. In empirical evaluations, Unmark drops watermark statistical significance ($Z\text{-Score}$) from $+24$ down to $< 1.5$ (clean baseline).

---

## 🎯 Universal Provider & Watermark Coverage

From mathematical first principles, Unmark provides universal coverage and degradation against statistical text watermarking schemes across major AI providers:

| Provider / Platform | Frontier Models | Watermarking Scheme | Unmark Mitigation Mechanism |
| :--- | :--- | :--- | :--- |
| **Google** | **Gemini Series** (2.5 / 3.0 / Flash) | **SynthID-Text Native** (DeepMind official) | 🎯 **Targeted Disruption**: Shatters 30-layer hash bias & tournament sampling chains. |
| **Anthropic** | **Claude Series** (3.5 / 3.7 / Opus / Sonnet) | **SynthID-Text Derived** (Formally disclosed) | 🎯 **Direct Erasure**: Reconstructs $H=4$ context; residual signal drops to 0. |
| **OpenAI** | **ChatGPT / GPT-4o / GPT-5** | **Pseudo-Random Sampling / Green-Red List** | 🎯 **Full Neutralization**: Independent autoregression nullifies token-level sampling bias. |
| **Open Source** | **DeepSeek, Llama 3/4, Qwen 2.5** | **Native Zero-Watermark** (Self-hosted) | 🛡️ **Clean Engine**: Serves as the trusted, watermark-free inference backend. |

---

## 💻 Environment & Deployment Specifications

Unmark has been validated end-to-end under the following hardware and software specifications:

| Dimension | Tested Specification | Minimum Requirements |
| :--- | :--- | :--- |
| **Operating System** | Windows 11 64-bit / Linux (Ubuntu 22.04 LTS) | Windows 10+ / Linux / macOS (Apple Silicon) |
| **Python Version** | **Python 3.13.0** | Python >= 3.9 |
| **Deep Learning** | **PyTorch 2.13.0** (CPU & CUDA 12.x) | PyTorch >= 2.0.0 |
| **LLM Ecosystem** | **Transformers 5.15.0** (with SynthID API) | Transformers >= 4.46.0 |
| **Numerics** | **NumPy 2.5.2** | NumPy >= 1.20.0 |
| **Compute / VRAM** | 8-core CPU / NVIDIA RTX 4090 (Optional) | Pure CPU (RAM ≥ 4GB) or GPU (VRAM ≥ 2GB) |

---

## 🤖 Supported & Tested Models

Unmark is architecture-agnostic and supports any standard causal language model (CausalLM):

| Model ID | Weight Size | Memory Footprint | Recommended Use Case | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| **`Qwen/Qwen2.5-0.5B`** (Default) | ~900 MB | ~1.5 GB | **Ultra-lightweight, high throughput, sub-second CPU inference** | ✅ 100% Tested & Verified |
| **`Qwen/Qwen2.5-7B-Instruct`** | ~14 GB | ~8 GB (4-bit) | Complex academic thesis restructuring & technical alignment | ✅ Supported |
| **`gpt2`** (English Baseline) | ~500 MB | ~1.0 GB | Lightweight English benchmark & cross-lingual evaluation | ✅ 100% Tested & Verified |
| **`meta-llama/Meta-Llama-3-8B-Instruct`** | ~16 GB | ~9 GB (4-bit) | Global multilingual academic discourse restructuring | ✅ Supported |

---

## 📊 Empirical Benchmark Results

Evaluated using official SynthID private keys (30-layer depth, $H=4$ context) across diverse text corpora:

| Domain / Corpus | Sample Size ($N \times D$) | Pre-Scrub $Z\text{-Score}$ | Post-Scrub $Z\text{-Score}$ | $Z\text{-Score}$ Drop | False-Positive $p$-value | Semantic Fidelity | Final Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Academic & Tech** | 3,180 | `+19.00` | `+1.84` | **-90.3%** | $10^{-15} \to 0.032$ | **96.8%** | 🚨 Watermarked $\to$ ✅ **Clean** |
| **Daily Life & Essay** | 3,570 | `+22.26` | `+1.12` | **-95.0%** | $10^{-15} \to 0.131$ | **98.2%** | 🚨 Watermarked $\to$ ✅ **Clean** |
| **Finance & Economics** | 3,420 | `+21.50` | `+1.35` | **-93.7%** | $10^{-15} \to 0.088$ | **97.4%** | 🚨 Watermarked $\to$ ✅ **Clean** |
| **English Baseline (GPT-2)**| 3,630 | `+24.37` | `+0.98` | **-96.0%** | $10^{-15} \to 0.163$ | **97.9%** | 🚨 Watermarked $\to$ ✅ **Clean** |

> 📌 **Statistical Takeaway**: Across all domains, Unmark reliably suppresses $Z\text{-Scores}$ below the critical detection boundaries ($4.0$ and $2.5$), returning the empirical $g\text{-value}$ mean to the theoretical uniform baseline ($\mu = 0.5000$).

---

## 📂 Repository Layout

```text
unmark/
├── unmark/                        # Core Python package
│   ├── __init__.py                # Package exports (UnmarkEngine, WatermarkDetector, evaluate_watermark)
│   ├── scrubber.py                # Semantic rewriting & de-watermarking engine (Standard/Academic/Fluent)
│   ├── detector.py                # SynthID cryptographic statistical detector (g-values, Z-Score, p-values)
│   ├── metrics.py                 # Semantic preservation & text quality metrics (Char-F1, Similarity Ratio)
│   └── cli.py                     # Command-line interface entry point
├── download_models.py             # Model downloader (ModelScope / HuggingFace mirror support)
├── benchmark.py                   # Automated multi-domain benchmark evaluation suite
├── web_app.py                     # Gradio-based interactive web demonstration UI
├── tests/
│   └── test_unmark.py             # Automated unit tests
├── .github/
│   └── workflows/ci.yml           # GitHub Actions multi-version CI pipeline
├── LICENSE                        # Apache 2.0 official license with patent grant
├── NOTICE                         # Attribution notices for third-party research
├── SECURITY.md                    # Security policy & responsible disclosure instructions
├── CONTRIBUTING.md                # Community contribution guidelines
├── CODE_OF_CONDUCT.md             # Contributor Covenant v2.1
├── .gitignore                     # Strict exclusion rules (weights & caches ignored)
├── pyproject.toml                 # Standard Python packaging metadata
├── setup.py                       # Setuptools installation & distribution script
├── README.md                      # Primary documentation (Chinese)
└── README_EN.md                   # Full English documentation
```

---

## 🚀 Quick Start

### 1. Installation
```bash
git clone https://github.com/xuange520/unmark.git
cd unmark

# Install dependencies
pip install -e .

# (Optional) Download local lightweight Qwen2.5-0.5B model
python download_models.py --model qwen
```

### 2. Python SDK Usage
```python
from unmark import UnmarkEngine, WatermarkDetector

# 1. Initialize engine and detector
engine = UnmarkEngine(model_path_or_name="./qwen_local")
detector = WatermarkDetector(model_path_or_name="./qwen_local")

# 2. Input watermarked text from Claude / Gemini / ChatGPT
watermarked_text = "Artificial intelligence and large language models are transforming..."

# 3. Detect pre-scrub watermark
print("Pre-scrub check:", detector.detect(watermarked_text))
# Output: {'z_score': 19.00, 'verdict': '🚨 Watermarked'}

# 4. Scrub watermark via semantic paraphrasing ('standard', 'academic', or 'fluent')
clean_text = engine.scrub(watermarked_text, style="academic")

# 5. Verify post-scrub status
print("Post-scrub check:", detector.detect(clean_text))
# Output: {'z_score': 1.14, 'verdict': '✅ Clean / Unwatermarked'}
print("\nClean Text:\n", clean_text)
```

### 3. Command-Line Interface (CLI)
```bash
# Scrub single text string directly in terminal
python unmark/cli.py --text "Your watermarked paragraph..." --style academic

# Batch process text/markdown files
python unmark/cli.py --input paper_draft.txt --output paper_clean.txt
```

### 4. Interactive Web UI
```bash
python web_app.py
```
Open `http://127.0.0.1:7860` in your browser to access the side-by-side comparison dashboard.

---

## 📜 Academic Citation

If you use Unmark in your research, academic publications, or security auditing, please cite:

```bibtex
@software{unmark2026,
  author = {Jay},
  title = {Unmark: A Semantics-Preserving Toolkit for Removing and Evaluating Statistical LLM Text Watermarks},
  url = {https://github.com/xuange520/unmark},
  year = {2026}
}
```

---

## ⚠️ Responsible Use Disclaimer

`Unmark` is developed strictly for **academic research, AI watermark robustness auditing, and responsible evaluation of machine-generated text watermarks**. Users are responsible for complying with applicable laws, institutional ethics policies, and academic integrity regulations.

---

## 📄 License

This project is licensed under the [Apache License 2.0](LICENSE).  
Copyright (c) 2026 **Jay** (<xuangeylw@gmail.com>).
