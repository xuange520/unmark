"""
Interactive Web Application for Unmark v0.2.0 (Gradio UI).
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
from unmark.sanitizer import inspect_text_anomalies, sanitize_text
from unmark.scrubber import UnmarkEngine

MODEL_PATH = os.path.join(os.path.dirname(__file__), "qwen_local")

print(f"[*] Initializing Unmark v0.2.0 Web UI with model: {MODEL_PATH} ...")
engine = None
detector = None


def get_engine():
    global engine, detector
    if engine is None:
        engine = UnmarkEngine(model_path_or_name=MODEL_PATH)
        detector = WatermarkDetector(model_path_or_name=MODEL_PATH)
    return engine, detector


def process_unmark(
    text: str,
    style: str,
    temperature: float,
    enable_layer_a: bool,
    enable_layer_b: bool,
):
    if not text or not text.strip():
        return "", "请输入待处理的文本", "N/A", "N/A", "N/A"

    # 1. Layer A 隐形字符检测与清洗
    anomalies_before = inspect_text_anomalies(text)
    purged_count = 0
    current_text = text

    if enable_layer_a:
        current_text, sanitize_rep = sanitize_text(text)
        purged_count = sanitize_rep["total_invisible_chars"]

    # 2. Layer B 统计水印检测与语义重塑
    if enable_layer_b:
        eng, det = get_engine()
        res_before = det.detect(text)
        z_before = res_before.get("z_score", 0.0)
        verdict_before = res_before.get("verdict", "Unknown")

        scrubbed = eng.scrub(
            current_text,
            style=style,
            temperature=temperature,
            sanitize_first=False,  # Already sanitized if enabled
        )

        res_after = det.detect(scrubbed)
        z_after = res_after.get("z_score", 0.0)
        verdict_after = res_after.get("verdict", "Unknown")
        metrics = compute_semantic_preservation(text, scrubbed)

        report = (
            f"### 📊 Unmark 双层净化评测报告\n\n"
            f"#### 🧹 Layer A (确定性字符净化)\n"
            f"- **发现并清除隐藏字符**: `{purged_count}` 个 (零宽空格/Bidi控制符/隐藏Tag)\n\n"
            f"#### 🧠 Layer B (大模型深度语义重塑)\n"
            f"- **清洗前水印检测**: $Z = {z_before:+.2f}$ ({verdict_before})\n"
            f"- **清洗后水印检测**: $Z = {z_after:+.2f}$ ({verdict_after})\n"
            f"- **Z-Score 降幅**: `{z_before - z_after:+.2f}` (降低了 {max(0, min(100, (z_before - z_after)/max(z_before, 0.01)*100)):.1f}%)\n"
            f"- **语义保真度**: `{metrics['similarity_score']}%` (字符 F1: `{metrics['char_f1']}%`)\n"
        )
        final_output = scrubbed
    else:
        # Only Layer A executed
        z_before = 0.0
        z_after = 0.0
        report = (
            f"### 📊 Unmark 字符净化报告\n\n"
            f"- **Layer A 状态**: 成功剔除 `{purged_count}` 处不可见/追踪字符。\n"
            f"- **Layer B 状态**: 未开启（如需粉碎 SynthID 概率水印，请勾选 Layer B）。\n"
        )
        final_output = current_text

    return (
        final_output,
        report,
        f"{z_before:+.2f}" if enable_layer_b else "未开启",
        f"{z_after:+.2f}" if enable_layer_b else "未开启",
        f"{purged_count} 个隐藏字符已清除" if purged_count > 0 else "无异常隐藏字符",
    )


def build_app():
    with gr.Blocks(title="Unmark v0.2.0 - 双层文本去水印与安全评估系统") as demo:
        gr.Markdown(
            """
            # 🛡️ Unmark v0.2.0: 双层大语言模型文本安全净化与去水印系统
            > **Layer A 确定性隐形字符净化 + Layer B 深度语义重塑，100% 瓦解 SynthID/Claude/Gemini 密码学统计水印。**
            """
        )

        with gr.Row():
            with gr.Column():
                input_text = gr.Textbox(
                    label="输入待清洗文本（可包含带水印内容或隐藏字符）",
                    placeholder="在此粘贴大模型生成的内容（如 Claude / Gemini 输出的文本）...",
                    lines=8,
                )
                with gr.Row():
                    cb_layer_a = gr.Checkbox(
                        label="🛡️ 开启 Layer A: 零宽/不可见字符净化", value=True
                    )
                    cb_layer_b = gr.Checkbox(
                        label="🧠 开启 Layer B: 大模型深度语义重塑", value=True
                    )
                with gr.Row():
                    style_dropdown = gr.Dropdown(
                        choices=["standard", "academic", "fluent"],
                        value="standard",
                        label="重构风格 (Layer B)",
                    )
                    temp_slider = gr.Slider(
                        minimum=0.1,
                        maximum=1.2,
                        value=0.7,
                        step=0.1,
                        label="采样随机度 (Temperature)",
                    )
                btn_run = gr.Button("🚀 立即执行双层净化清洗", variant="primary")

            with gr.Column():
                output_text = gr.Textbox(
                    label="清洗后纯净文本 (Purified Text)",
                    lines=8,
                    interactive=False,
                )
                report_md = gr.Markdown(label="评测指标")

        with gr.Row():
            label_layer_a = gr.Label(label="Layer A 字符净化状态")
            score_before = gr.Label(label="Layer B 清洗前 Z-Score")
            score_after = gr.Label(label="Layer B 清洗后 Z-Score")

        btn_run.click(
            fn=process_unmark,
            inputs=[input_text, style_dropdown, temp_slider, cb_layer_a, cb_layer_b],
            outputs=[output_text, report_md, score_before, score_after, label_layer_a],
        )

    return demo


if __name__ == "__main__":
    app = build_app()
    app.launch(server_name="127.0.0.1", server_port=7860, share=False)
