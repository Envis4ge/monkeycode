"""
量化对比实验 — 理解模型压缩
===========================
目标：理解量化如何压缩模型，对比不同精度

核心概念：
- 浮点精度：FP32 → FP16 → INT8 → INT4
- 量化原理：用更少的位数表示权重，牺牲少量精度换取大幅压缩
- 量化影响：模型大小、推理速度、输出质量的权衡
"""

import struct
import time
import os

# ============ 浮点精度基础 ============

def explain_precision():
    """解释不同浮点格式"""
    print("=" * 60)
    print("浮点精度详解")
    print("=" * 60)
    
    formats = [
        ("FP32", 32, 8, 23, "单精度", "~7位有效数字", "训练标准"),
        ("FP16", 16, 5, 10, "半精度", "~3位有效数字", "训练/推理"),
        ("BF16", 16, 8, 7, "Brain Float", "~2位有效数字", "训练(大模型常用)"),
        ("INT8", 8, 0, 0, "8位整数", "离散值", "推理量化"),
        ("INT4", 4, 0, 0, "4位整数", "离散值", "极致压缩"),
    ]
    
    print(f"\n{'格式':<8} {'位数':<8} {'指数':<8} {'尾数':<8} {'精度':<16} {'用途'}")
    print("-" * 65)
    for name, bits, exp, mant, desc, prec, use in formats:
        print(f"{name:<8} {bits:<8} {exp:<8} {mant:<8} {desc:<12} {prec:<14} {use}")
    
    print("\n关键洞察:")
    print("  - FP32 精度最高但占用最大（每个参数4字节）")
    print("  - FP16/BF16 减半存储，精度损失很小")
    print("  - INT8 再减半，适合推理")
    print("  - INT4 极致压缩，质量有所下降但可接受")


# ============ 量化实现 ============

def quantize_fp32_to_int8(weights):
    """
    将 FP32 权重量化为 INT8
    
    原理：
    1. 找到权重的最大绝对值 max_val
    2. 计算缩放因子 scale = max_val / 127
    3. 量化: q = round(w / scale)
    4. 反量化: w' = q * scale
    
    这是"对称量化"的简化实现
    """
    max_val = max(abs(w) for w in weights)
    if max_val == 0:
        return [0] * len(weights), 1.0
    
    scale = max_val / 127.0
    
    # 量化：浮点 → 整数
    quantized = [round(w / scale) for w in weights]
    # 限制在 [-127, 127]
    quantized = [max(-127, min(127, q)) for q in quantized]
    
    return quantized, scale


def dequantize_int8(quantized, scale):
    """INT8 反量化回浮点"""
    return [q * scale for q in quantized]


def quantize_fp32_to_int4(weights):
    """
    将 FP32 权重量化为 INT4 (范围 [-8, 7])
    
    精度更低但压缩更激进
    """
    max_val = max(abs(w) for w in weights)
    if max_val == 0:
        return [0] * len(weights), 1.0
    
    scale = max_val / 7.0  # INT4 范围更小
    
    quantized = [round(w / scale) for w in weights]
    quantized = [max(-8, min(7, q)) for q in quantized]
    
    return quantized, scale


def dequantize_int4(quantized, scale):
    """INT4 反量化回浮点"""
    return [q * scale for q in quantized]


# ============ 量化误差分析 ============

def calculate_error(original, reconstructed):
    """计算量化误差"""
    n = len(original)
    
    # 均方误差
    mse = sum((o - r) ** 2 for o, r in zip(original, reconstructed)) / n
    
    # 信噪比 (SNR)
    signal_power = sum(o ** 2 for o in original) / n
    noise_power = mse
    snr = 10 * (signal_power / noise_power) if noise_power > 0 else float('inf')
    snr_db = 10 * __import__('math').log10(snr) if snr > 0 else 0
    
    # 最大绝对误差
    max_error = max(abs(o - r) for o, r in zip(original, reconstructed))
    
    return mse, snr_db, max_error


# ============ 实验 ============

def experiment():
    """量化对比实验"""
    print("\n" + "=" * 60)
    print("量化对比实验")
    print("=" * 60)
    
    import random
    random.seed(42)
    
    # 模拟一组神经网络权重（近似正态分布）
    num_weights = 1000
    weights = [random.gauss(0, 1) for _ in range(num_weights)]
    
    print(f"\n权重数量: {num_weights}")
    print(f"权重范围: [{min(weights):.4f}, {max(weights):.4f}]")
    print(f"权重均值: {sum(weights)/num_weights:.4f}")
    
    # ---- 不同精度对比 ----
    print(f"\n{'精度':<10} {'字节/权重':<12} {'模型大小(MB)':<15} {'MSE':<15} {'SNR(dB)':<12} {'最大误差'}")
    print("-" * 80)
    
    # FP32（原始）
    fp32_size = num_weights * 4
    print(f"{'FP32':<10} {'4':<12} {fp32_size/1024/1024:<15.6f} {'0 (原始)':<15} {'∞':<12} {'0'}")
    
    # INT8
    q8, scale8 = quantize_fp32_to_int8(weights)
    r8 = dequantize_int8(q8, scale8)
    mse8, snr8, maxe8 = calculate_error(weights, r8)
    int8_size = num_weights * 1  # 每个权重1字节
    print(f"{'INT8':<10} {'1':<12} {int8_size/1024/1024:<15.6f} {mse8:<15.6f} {snr8:<12.2f} {maxe8:<.6f}")
    
    # INT4
    q4, scale4 = quantize_fp32_to_int4(weights)
    r4 = dequantize_int4(q4, scale4)
    mse4, snr4, maxe4 = calculate_error(weights, r4)
    int4_size = num_weights * 0.5  # 每个权重0.5字节
    print(f"{'INT4':<10} {'0.5':<12} {int4_size/1024/1024:<15.6f} {mse4:<15.6f} {snr4:<12.2f} {maxe4:<.6f}")
    
    # ---- 压缩率 ----
    print(f"\n压缩率:")
    print(f"  FP32 → INT8: {fp32_size/int8_size:.1f}x 压缩")
    print(f"  FP32 → INT4: {fp32_size/int4_size:.1f}x 压缩")
    
    # ---- 模拟不同规模模型 ----
    print(f"\n{'模型规模':<20} {'FP32 大小':<15} {'INT4 大小':<15} {'需要显存(INT4)'}")
    print("-" * 65)
    
    models = [
        ("1B 参数", 1e9),
        ("7B 参数", 7e9),
        ("13B 参数", 13e9),
        ("70B 参数", 70e9),
    ]
    
    for name, params in models:
        fp32_mb = params * 4 / 1024 / 1024
        int4_mb = params * 0.5 / 1024 / 1024
        print(f"{name:<20} {fp32_mb/1024:<13.1f} GB {int4_mb/1024:<13.1f} GB {int4_mb/1024*1.2:.1f} GB")


def quantization_schemes():
    """对比不同量化方案"""
    print("\n" + "=" * 60)
    print("Ollama 常用量化方案对比")
    print("=" * 60)
    
    schemes = [
        ("q4_0",  "4-bit", "基础4位量化", "最小体积，质量一般"),
        ("q4_1",  "4-bit", "4位 + 缩放因子", "稍大，质量略好"),
        ("q5_0",  "5-bit", "基础5位量化", "体积适中，质量较好"),
        ("q5_1",  "5-bit", "5位 + 缩放因子", "质量很好"),
        ("q8_0",  "8-bit", "基础8位量化", "体积较大，质量接近FP16"),
        ("q2_K",  "2-4 bit", "K-quant 混合", "极致压缩，质量有限"),
        ("q4_K_M","4-bit", "K-quant 中等", "⭐ 推荐：体积和质量平衡"),
        ("q5_K_M","5-bit", "K-quant 中等", "⭐ 推荐：质量优先"),
        ("q6_K",  "6-bit", "K-quant", "接近原始质量"),
    ]
    
    print(f"\n{'方案':<10} {'位数':<12} {'说明':<22} {'评价'}")
    print("-" * 65)
    for name, bits, desc, note in schemes:
        print(f"{name:<10} {bits:<12} {desc:<22} {note}")
    
    print("\n⭐ 推荐选择:")
    print("  - 显存紧张 → q4_K_M (7B 模型约 4GB)")
    print("  - 质量优先 → q5_K_M 或 q6_K")
    print("  - 不确定   → q4_K_M (最平衡)")


# ============ 演示 ============

if __name__ == '__main__':
    explain_precision()
    experiment()
    quantization_schemes()
