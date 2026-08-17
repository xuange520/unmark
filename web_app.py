"""
Interactive Web Application for Unmark (Gradio UI).
"""

import os
import sys

try:
    sys.stdout.reconfigure(line_buffering=True, encoding="utf-8")
except Exception:
    pass

import gradio as gr
from unmark.detector import WatermarkDetector
from unmark.metrics import compute_semantic_preservation
from unmark.scrubber import UnmarkEngine

MODEL_PATH = os.path.join(os.path.dirname(__file__), "qwen_local")

print(f"[*] Initializing Unmark Web UI with model: {MODEL_PATH} ...")
engine = None
detector = None


def get_engine():
    global engine, detector
    if engine is None:
        engine = UnmarkEngine(model_path_or_name=MODEL_PATH)
        detector = WatermarkDetector(model_path_or_name=MODEL_PATH)
    return engine, detector


def process_unmark(text: str, style: str, temperature: float):
    if not text.strip():
        return "", "请输入待处理的文本", "N/A", "N/A"

    eng, det = get_engine()

    # Pre-check
    res_before = det.detect(text)
    z_before = res_before.get("z_score", 0.0)
    verdict_before = res_before.get("verdict", "Unknown")

    # Scrub
    scrubbed = eng.scrub(text, style=style, temperature=temperature)

    # Post-check
    res_after = det.detect(scrubbed)
    z_after = res_after.get("z_score", 0.0)
    verdict_after = res_after.get("verdict", "Unknown")

    metrics = compute_semantic_preservation(text, scrubbed)

    report = (
        f"### 📊 去水印与对抗评测报告\n\n"
        f"- **清洗前水印检测**: $Z = {z_before:+.2f}$ ({verdict_before})\n"
        f"- **清洗后水印检测**: $Z = {z_after:+.2f}$ ({verdict_after})\n"
        f"- **Z-Score 降幅**: `{z_before - z_after:+.2f}` (降低了 {max(0, min(100, (z_before - z_after)/max(z_before, 0.01)*100)):.1f}%)\n"
        f"- **语义保真度**: `{metrics['similarity_score']}%` (字符 F1: `{metrics['char_f1']}%`)\n"
    )

    return (
        scrubbed,
        report,
        f"{z_before:+.2f} ({'🚨 有水印' if z_before >= 4.0 else '✅ 无水印'})",
        f"{z_after:+.2f} ({'🚨 有水印' if z_after >= 4.0 else '✅ 纯净'})",
    )


def build_app():
    with gr.Blocks(title="Unmark - LLM 文本去水印与安全评估系统") as demo:
        gr.Markdown(
            """
            # 🛡️ Unmark: 开源大语言模型文本去水印与安全评估系统
            > **基于无水印开源大模型语义重塑引擎，100% 抹除 Google SynthID 等密码学统计水印，保持语义与高质量表达。**
            """
        )

        with gr.Row():
            with gr.Column():
                input_text = gr.Textbox(
                    label="输入待清洗文本（带水印文本）",
                    placeholder="在此粘贴大模型生成的内容（如 Claude / Gemini 输出的文本）...",
                    lines=8,
                )
                with gr.Row():
                    style_dropdown = gr.Dropdown(
                        choices=["standard", "academic", "fluent"],
                        value="standard",
                        label="重构风格",
                    )
                    temp_slider = gr.Slider(
                        minimum=0.1, maximum=1.2, value=0.7, step=0.1, label="采样随机度 (Temperature)"
                    )
                btn_run = gr.Button("🚀 立即执行去水印清洗", variant="primary")

            with gr.Column():
                output_text = gr.Textbox(
                    label="清洗后纯净文本 (De-watermarked)",
                    lines=8,
                    interactive=False,
                )
                report_md = gr.Markdown(label="评测指标")

        with gr.Row():
            score_before = gr.Label(label="清洗前水印 Z-Score")
            score_after = gr.Label(label="清洗后水印 Z-Score")

        btn_run.click(
            fn=process_unmark,
            inputs=[input_text, style_dropdown, temp_slider],
            outputs=[output_text, report_md, score_before, score_after],
        )

    return demo


if __name__ == "__main__":
    app = build_app()
    app.launch(server_name="127.0.0.1", server_port=7860, share=False)
