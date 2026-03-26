"""
推理优化原理 — 大模型为什么需要优化
====================================
目标：理解大模型推理中的关键技术

核心概念：
- KV Cache：缓存已计算的 Key/Value，避免重复计算
- Flash Attention：优化注意力计算的内存访问模式
- 推测解码(Speculative Decoding)：小模型猜测 + 大模型验证
- PagedAttention：像操作系统分页一样管理 KV Cache
"""

import math
import time

# ============ KV Cache ============

class KVCacheDemo:
    """
    KV Cache 原理演示
    
    问题：自回归生成时，每生成一个 token 都要重新计算所有之前 token 的注意力
    解决：缓存已计算的 K 和 V，只需计算新 token 的 Q
    
    无 KV Cache:
      生成 token 1: 计算 Q1,K1,V1              → O(n)
      生成 token 2: 计算 Q2,K1,K2,V1,V2        → O(n)
      生成 token 3: 计算 Q3,K1,K2,K3,V1,V2,V3  → O(n)
      总计: O(n²) 每步都要重新算之前的 K,V
    
    有 KV Cache:
      生成 token 1: 计算 Q1,K1,V1, 缓存 K1,V1  → O(n)
      生成 token 2: 计算 Q2,K2,V2, 读缓存 K1,V1 → O(n)
      生成 token 3: 计算 Q3,K3,V3, 读缓存 K1,K2,V1,V2 → O(n)
      总计: O(n) 每步只算新 token
    """
    
    def __init__(self):
        self.k_cache = []  # 缓存的 Key
        self.v_cache = []  # 缓存的 Value
    
    def compute_attention(self, new_q, new_k, new_v):
        """
        带 KV Cache 的注意力计算
        
        new_q: 新 token 的 Query (1, d)
        new_k: 新 token 的 Key (1, d)
        new_v: 新 token 的 Value (1, d)
        """
        # 添加新的 K, V 到缓存
        self.k_cache.append(new_k)
        self.v_cache.append(new_v)
        
        # 拼接所有缓存的 K
        all_k = self.k_cache  # (seq_len, d)
        
        # 注意力分数: Q 只需要和所有 K 做点积
        scores = [sum(a*b for a,b in zip(new_q, k)) / math.sqrt(len(new_q)) for k in all_k]
        
        # Softmax
        max_s = max(scores)
        exp_scores = [math.exp(s - max_s) for s in scores]
        sum_exp = sum(exp_scores)
        weights = [e / sum_exp for e in exp_scores]
        
        # 加权求和 V
        output = [0.0] * len(new_v)
        for w, v in zip(weights, self.v_cache):
            for i in range(len(v)):
                output[i] += w * v[i]
        
        return output
    
    def clear(self):
        self.k_cache = []
        self.v_cache = []


def demo_kv_cache():
    """演示 KV Cache 的效果"""
    print("=" * 60)
    print("KV Cache 原理演示")
    print("=" * 60)
    
    d = 4  # 维度
    seq_len = 10  # 序列长度
    
    # 模拟 token
    import random
    random.seed(42)
    tokens = [[random.gauss(0, 1) for _ in range(d)] for _ in range(seq_len)]
    
    # 无 KV Cache：每次重新计算
    print(f"\n无 KV Cache (每步重新计算所有):")
    total_ops_no_cache = 0
    for step in range(1, seq_len + 1):
        ops = step * d  # 每步要计算 step 个 token 的 K,V
        total_ops_no_cache += ops
        print(f"  第{step}步: {ops}次乘法")
    print(f"  总计: {total_ops_no_cache}次乘法")
    
    # 有 KV Cache：只计算新 token
    print(f"\n有 KV Cache (每步只算新 token):")
    total_ops_with_cache = 0
    for step in range(1, seq_len + 1):
        ops = d  # 每步只算1个新 token
        total_ops_with_cache += ops
        print(f"  第{step}步: {ops}次乘法")
    print(f"  总计: {total_ops_with_cache}次乘法")
    
    print(f"\n加速比: {total_ops_no_cache / total_ops_with_cache:.1f}x")
    print(f"KV Cache 内存占用: {seq_len * d * 2 * 4} bytes (K+V, FP32)")


# ============ Flash Attention 原理 ============

def explain_flash_attention():
    """解释 Flash Attention 的核心思想"""
    print("\n" + "=" * 60)
    print("Flash Attention 原理")
    print("=" * 60)
    
    print("""
问题：标准注意力的内存访问模式很差

标准 Attention:
  1. 计算 S = Q @ K^T         → 需要把整个 (n,n) 矩阵放进 GPU SRAM
  2. 计算 P = softmax(S)      → 又要读写 (n,n) 矩阵
  3. 计算 O = P @ V           → 还要读 (n,n) 矩阵
  → 内存访问量 = O(n²)，远超计算量 O(n²)

Flash Attention 优化:
  1. 分块(Tiling)：把 Q,K,V 分成小块，每块放进 GPU SRAM（高速缓存）
  2. 在 SRAM 内完成计算：避免反复读写 HBM（显存，慢）
  3. 在线 Softmax：不需要存储完整的 (n,n) 注意力矩阵
  4. 反向传播时重算：用少量内存，需要时重新计算

效果:
  - 内存: O(n) 而不是 O(n²)
  - 速度: 快 2-4 倍（减少 HBM 访问）
  - 精度: 几乎无损（数值稳定处理）

关键洞察:
  GPU 的计算能力远超内存带宽。
  Flash Attention 的核心不是减少计算量，
  而是让计算更高效地利用高速缓存。
""")


# ============ 推测解码 ============

class SpeculativeDecodingDemo:
    """
    推测解码 (Speculative Decoding) 原理
    
    思路：用小模型快速猜测多个 token，大模型一次性验证
    效果：生成速度提升 2-3 倍，输出质量完全不变
    """
    
    def explain(self):
        print("\n" + "=" * 60)
        print("推测解码 (Speculative Decoding) 原理")
        print("=" * 60)
        
        print("""
标准自回归生成 (大模型):
  token1 → token2 → token3 → token4 → token5
  每步都要大模型前向传播一次，共 5 步，慢！

推测解码:
  Step 1: 小模型快速猜测 5 个 token
    小模型: token1 → token2 → token3 → token4 → token5
    (很快，因为小模型计算量小)
  
  Step 2: 大模型一次性验证这 5 个 token
    大模型: 输入 [prefix, token1, token2, token3, token4, token5]
    输出: 每个位置的条件概率 P(token_i | prefix, token_1..token_{i-1})
  
  Step 3: 逐个验证
    - token1: 大模型也认为对 ✓ → 接受
    - token2: 大模型也认为对 ✓ → 接受
    - token3: 大模型认为错 ✗ → 从这里开始用大模型的分布重新采样
    - token4,5: 丢弃
  
  结果: 一次大模型前向传播就得到 2-3 个 token
        比标准生成快 2-3 倍！

关键洞察:
  - 大模型只需"验证"不需要"生成"，速度快很多
  - 小模型猜测错误时，大模型纠正，质量完全不变
  - 典型加速比: 2-3x
""")


# ============ PagedAttention ============

def explain_paged_attention():
    """解释 PagedAttention"""
    print("\n" + "=" * 60)
    print("PagedAttention 原理")
    print("=" * 60)
    
    print("""
问题：KV Cache 内存管理浪费严重

无 PagedAttention (vLLM 之前):
  - 每个请求预分配最大长度的 KV Cache
  - 实际只用了 20%，剩下 80% 浪费
  - 128K 上下文 → 每个请求预分配巨大内存
  - GPU 内存利用率低

PagedAttention (vLLM):
  - 像操作系统的虚拟内存分页一样管理 KV Cache
  - KV Cache 分成固定大小的"页"(blocks)
  - 按需分配，用多少分多少
  - 不同请求可以共享公共前缀的 KV Cache

效果:
  - 内存利用率: 从 ~20% 提升到 ~95%
  - 吞吐量: 提升 2-4x
  - 支持更长的上下文
  - 支持并行采样（多个候选共享前缀）

示例:
  传统: 100 个请求 × 128K 预分配 = 12.8M tokens 的 KV Cache
  PagedAttention: 100 个请求 × 实际使用 ≈ 2.5M tokens
  
  → 同样的 GPU 能服务 4 倍的请求！
""")


# ============ 综合对比 ============

def summary():
    """推理优化技术总结"""
    print("\n" + "=" * 60)
    print("推理优化技术总结")
    print("=" * 60)
    
    techniques = [
        ("KV Cache",       "缓存已计算的K,V",    "O(n²) → O(n) 每步",   "必须开启", "几乎所有LLM"),
        ("Flash Attention", "优化内存访问模式",    "内存 O(n²) → O(n)",   "推荐", "GPU推理"),
        ("推测解码",        "小模型猜+大模型验证",  "速度 2-3x",          "可选", "低延迟场景"),
        ("PagedAttention",  "分页管理KV Cache",    "内存利用率 +4x",      "推荐", "高并发服务"),
        ("量化",            "降低权重精度",        "显存 4-8x 压缩",      "推荐", "资源受限"),
        ("连续批处理",      "动态插入新请求",      "吞吐量 +3x",         "必须", "在线服务"),
    ]
    
    print(f"\n{'技术':<16} {'原理':<22} {'效果':<22} {'推荐':<8} {'适用场景'}")
    print("-" * 80)
    for name, principle, effect, rec, scene in techniques:
        print(f"{name:<16} {principle:<22} {effect:<22} {rec:<8} {scene}")
    
    print("\n生产环境推荐组合:")
    print("  KV Cache + Flash Attention + PagedAttention + INT4量化 + 连续批处理")


# ============ 主函数 ============

if __name__ == '__main__':
    demo_kv_cache()
    explain_flash_attention()
    SpeculativeDecodingDemo().explain()
    explain_paged_attention()
    summary()
