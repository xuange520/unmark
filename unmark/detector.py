"""
=============================================================================
                       Unmark - 密码学水印统计检测模块
=============================================================================
文件说明:
    本模块实现了基于 Google DeepMind (Nature 2024) 论文标准的 SynthID-Text 密码学
    水印检测分析算法。通过计算 N-gram 上下文与私钥调制下的 g-value 均值、Z-Score
    正态偏置统计量与假阳性 p-value，精准判断文本是否携带大模型统计水印。

核心数学公式:
    1. 理论无偏基准: g ~ Uniform[0, 1), μ₀ = 0.5, σ₀² = 1/12
    2. 统计标准误:   SE = sqrt(σ₀² / N)
    3. 偏置统计量:   Z = (mean(g) - μ₀) / SE
    4. 显著性检验:   p = 1 - Φ(Z)  (Z ≥ 4.0 判定为极高置信度带水印)
=============================================================================
"""

import math
from typing import Any, Dict, List, Optional
import numpy as np
import torch
from transformers import AutoTokenizer, SynthIDTextWatermarkLogitsProcessor

# 官方 SynthID-Text 30 层深度推荐密钥配置
DEFAULT_SYNTHID_CONFIG = {
    "ngram_len": 5,  # 对应前序上下文 H = 4 个 Token
    "keys": [
        654, 400, 836, 123, 340, 443, 597, 160, 57, 29,
        590, 639, 13, 715, 468, 990, 966, 226, 324, 585,
        118, 504, 421, 521, 129, 669, 732, 225, 90, 960,
    ],
    "sampling_table_size": 2**16,
    "sampling_table_seed": 0,
    "context_history_size": 1024,
}


def _norm_cdf(x: float) -> float:
    """标准正态分布累积分布函数 (CDF)"""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def evaluate_watermark(
    text: str,
    tokenizer: Any,
    logits_processor: SynthIDTextWatermarkLogitsProcessor,
    device: str = "cpu",
    z_threshold: float = 4.0,
) -> Dict[str, Any]:
    """
    评测一段文本中是否包含 SynthID-Text 统计学水印。

    参数:
        text (str): 待检测的文本字符串
        tokenizer: Hugging Face 分词器
        logits_processor: 已初始化的 SynthIDTextWatermarkLogitsProcessor
        device (str): 计算设备 ('cpu' 或 'cuda')
        z_threshold (float): 水印判定 Z-Score 临界阈值 (默认 4.0)

    返回:
        Dict[str, Any]: 包含 g-value 均值、Z-Score、p-value 与判定结论的字典
    """
    tokens = tokenizer(text, return_tensors="pt").input_ids.to(device)
    total_tokens = tokens.shape[1]

    # 若文本长度短于 N-gram 上下文窗口，无法提取统计量
    if total_tokens < logits_processor.ngram_len:
        return {
            "valid": False,
            "reason": f"文本过短 ({total_tokens} tokens < {logits_processor.ngram_len} 窗口)",
            "mean_g": 0.5,
            "z_score": 0.0,
            "p_value": 1.0,
            "verdict": "无法判定 (文本过短)",
            "num_scored": 0,
        }

    with torch.no_grad():
        # 计算 30 层私钥对应的 g-values 矩阵
        g_values = logits_processor.compute_g_values(input_ids=tokens)
        eos_mask = logits_processor.compute_eos_token_mask(
            input_ids=tokens, eos_token_id=tokenizer.eos_token_id
        )[:, logits_processor.ngram_len - 1 :]
        context_mask = logits_processor.compute_context_repetition_mask(input_ids=tokens)
        combined_mask = (context_mask * eos_mask).bool()

        valid_g = g_values[combined_mask]
        if valid_g.numel() == 0:
            return {
                "valid": False,
                "reason": "无有效未重复的 Token",
                "mean_g": 0.5,
                "z_score": 0.0,
                "p_value": 1.0,
                "verdict": "无法判定 (全重复文本)",
                "num_scored": 0,
            }

        valid_g_np = valid_g.cpu().numpy()
        mean_g = float(np.mean(valid_g_np))
        num_scored = int(valid_g_np.size)

        # 统计学假设检验：无水印均匀分布假设
        mu_0 = 0.5
        var_0 = 1.0 / 12.0
        se = math.sqrt(var_0 / num_scored)
        z_score = (mean_g - mu_0) / se
        p_value = max(1.0 - _norm_cdf(z_score), 1e-15)

        # 依据统计学显著性给出结论
        if z_score >= z_threshold:
            verdict = "🚨 极高置信度带水印 (Watermarked)"
            is_watermarked = True
        elif z_score >= 2.5:
            verdict = "⚠️ 疑似带有水印 (Likely Watermarked)"
            is_watermarked = True
        else:
            verdict = "✅ 纯净无水印 (Clean / Unwatermarked)"
            is_watermarked = False

        return {
            "valid": True,
            "mean_g": mean_g,
            "z_score": z_score,
            "p_value": p_value,
            "verdict": verdict,
            "is_watermarked": is_watermarked,
            "num_scored": num_scored,
        }


class WatermarkDetector:
    """
    高层封装的 SynthID 水印检测器 API。
    """

    def __init__(
        self,
        model_path_or_name: str,
        config: Optional[Dict[str, Any]] = None,
        device: Optional[str] = None,
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.config = config or DEFAULT_SYNTHID_CONFIG
        self.tokenizer = AutoTokenizer.from_pretrained(model_path_or_name)
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        self.processor = SynthIDTextWatermarkLogitsProcessor(
            **self.config, device=self.device
        )

    def detect(self, text: str) -> Dict[str, Any]:
        """
        对传入文本执行水印检测并返回指标字典。
        """
        return evaluate_watermark(
            text=text,
            tokenizer=self.tokenizer,
            logits_processor=self.processor,
            device=self.device,
        )
