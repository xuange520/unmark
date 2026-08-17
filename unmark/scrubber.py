"""
=============================================================================
                          Unmark - 语义重塑去水印引擎
=============================================================================
文件说明:
    本模块实现了基于无水印开源大模型 (LLM) 的深度语义重塑 (Discourse Paraphrasing) 算法。
    通过未加偏置的独立自回归采样，100% 破坏原文本中嵌入的 SynthID-Text 等连续 N-gram 哈希
    概率偏置链，使水印检测统计量 (Z-Score) 回归到白噪声基线，同时保持核心语义与事实完整度。

核心特性:
    1. 多风格重构模板 (Standard 标准 / Academic 学术 / Fluent 流畅)
    2. 自适应采样控制 (Temperature, Top-p, Repetition Penalty)
    3. 支持 CPU / CUDA 多硬件环境与单精度/半精度推理
=============================================================================
"""

from typing import Any, Dict, List, Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# 专为大模型语义重塑设计的 Prompt 模板库
STYLE_PROMPTS = {
    # 标准通用风格：适用于日常对话、自媒体文章、通用问答
    "standard": (
        "你是一个专业的文本重构与语言重塑专家。你的任务是将用户提供的文本进行深度同义改写，"
        "彻底更换所有句子的用词搭配与句式结构，严禁原样复制长句短语。"
        "同时必须100%保留原文全部核心事实、逻辑和论点。直接输出改写后的文本，不要输出任何前缀或解释。"
    ),
    # 严谨学术风格：适用于论文、综述、技术报告、学术公文
    "academic": (
        "你是一个严谨的学术论文重塑与润色专家。请在完整保留全部学术专有名词、实验数据与逻辑推导的前提下，"
        "以极其规范、严密的学术句式对以下文本进行深度重构，打破原有句式依赖，直接输出学术段落，无需额外说明。"
    ),
    # 流畅文学风格：适用于散文、小说、故事、新闻报道
    "fluent": (
        "请将以下内容用极其自然流畅、富有文学表现力的语言重述一遍，改变原有的句式模式，保持全部信息点完整，直接输出重写结果。"
    ),
}


class UnmarkEngine:
    """
    Unmark 语义重塑去水印清洗引擎。

    参数:
        model_path_or_name (str): 本地模型路径或 HuggingFace 模型标识 (如 ./qwen_local 或 Qwen/Qwen2.5-0.5B)
        device (str, optional): 运行设备 ('cuda' 或 'cpu'，默认自动检测)
        torch_dtype (torch.dtype, optional): 模型权重精度 (GPU 推荐 bfloat16/float16，CPU 推荐 float32)
    """

    def __init__(
        self,
        model_path_or_name: str,
        device: Optional[str] = None,
        torch_dtype: Optional[torch.dtype] = None,
    ):
        # 1. 自动选择最佳算力硬件
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        # 2. 加载分词器
        self.tokenizer = AutoTokenizer.from_pretrained(model_path_or_name)
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

        # 3. 加载因果语言模型
        selected_dtype = torch_dtype or (
            torch.bfloat16 if torch.cuda.is_available() else torch.float32
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path_or_name,
            torch_dtype=selected_dtype,
        ).to(self.device)
        self.model.eval()

    def scrub(
        self,
        text: str,
        style: str = "standard",
        temperature: float = 0.8,
        top_p: float = 0.92,
        top_k: int = 50,
        repetition_penalty: float = 1.15,
        max_new_tokens: Optional[int] = None,
    ) -> str:
        """
        对输入文本执行去水印重塑清洗。

        参数:
            text (str): 待清洗的带水印文本
            style (str): 重构风格 ('standard', 'academic', 'fluent')
            temperature (float): 采样随机度 (默认 0.8，避免原样复读)
            top_p (float): Nucleus 采样截断阈值 (默认 0.92)
            top_k (int): 候选词 Top-K 限制 (默认 50)
            repetition_penalty (float): 重复词惩罚系数 (默认 1.15，抑制 N-gram 重复)
            max_new_tokens (int, optional): 最大生成 Token 数量

        返回:
            str: 清洗后的纯净无水印文本
        """
        if not text or not text.strip():
            return ""

        system_instruction = STYLE_PROMPTS.get(style, STYLE_PROMPTS["standard"])
        prompt = (
            f"<|im_start|>system\n{system_instruction}<|im_end|>\n"
            f"<|im_start|>user\n请将以下文本用不同的词语搭配和句式结构进行深度改写，保持原意，严禁原样复制：\n{text.strip()}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        prompt_len = inputs.input_ids.shape[1]

        if max_new_tokens is None:
            input_text_tokens = len(self.tokenizer.encode(text))
            max_new_tokens = max(int(input_text_tokens * 1.4), 100)

        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                do_sample=True,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repetition_penalty=repetition_penalty,
            )

        generated_tokens = output_ids[0][prompt_len:]
        scrubbed_text = self.tokenizer.decode(
            generated_tokens, skip_special_tokens=True
        ).strip()

        # 过滤模型可能产生的多余前缀符号
        for prefix in ["改写结果：", "改写如下：", "重写如下：", "【改写】", "答："]:
            if scrubbed_text.startswith(prefix):
                scrubbed_text = scrubbed_text[len(prefix) :].strip()

        return scrubbed_text
