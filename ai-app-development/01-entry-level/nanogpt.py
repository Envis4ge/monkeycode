"""
nanoGPT — 简化版 GPT
====================
目标：理解 Transformer 架构每一层的作用

核心概念：
- 自注意力(Self-Attention)：让每个位置关注其他位置的信息
- 多头注意力(Multi-Head Attention)：并行多个注意力头，捕获不同模式
- 位置编码(Position Encoding)：告诉模型每个 token 的位置
- 层归一化(Layer Normalization)：稳定训练
- 残差连接(Residual Connection)：缓解梯度消失

来源：Andrej Karpathy 的 nanoGPT 项目简化版
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

# ============ 超参数 ============

class GPTConfig:
    """GPT 模型配置"""
    vocab_size = 65       # 词汇表大小（字符级）
    block_size = 128      # 最大上下文长度
    n_embd = 384          # 嵌入维度
    n_head = 6            # 注意力头数
    n_layer = 6           # Transformer 层数
    dropout = 0.2         # Dropout 比例
    
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


# ============ 核心模块 ============

class Head(nn.Module):
    """
    单个注意力头 (Scaled Dot-Product Attention)
    
    注意力机制的核心思想：
    - Query(Q): "我在找什么信息？"
    - Key(K):   "我包含什么信息？"
    - Value(V): "我的实际内容是什么？"
    
    注意力分数 = softmax(Q @ K.T / sqrt(d_k))
    输出 = 注意力分数 @ V
    """
    
    def __init__(self, head_size, n_embd, block_size, dropout):
        super().__init__()
        self.key = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)
        
        # 因果注意力掩码：不允许看到未来的 token
        # 下三角矩阵，位置 i 只能看到位置 0..i
        self.register_buffer('tril', torch.tril(torch.ones(block_size, block_size)))
        
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        B, T, C = x.shape  # batch, time, channels
        
        # 计算 Q, K, V
        k = self.key(x)    # (B, T, head_size)
        q = self.query(x)  # (B, T, head_size)
        v = self.value(x)  # (B, T, head_size)
        
        # 计算注意力分数
        # q @ k.transpose(-2, -1) = (B, T, head_size) @ (B, head_size, T) = (B, T, T)
        wei = q @ k.transpose(-2, 1) * C**-0.5  # 缩放，防止梯度过小
        
        # 应用因果掩码（让未来的 token 权重为 -inf）
        wei = wei.masked_fill(self.tril[:T, :T] == 0, float('-inf'))
        wei = F.softmax(wei, dim=-1)
        wei = self.dropout(wei)
        
        # 加权求和
        out = wei @ v  # (B, T, T) @ (B, T, head_size) = (B, T, head_size)
        return out


class MultiHeadAttention(nn.Module):
    """
    多头注意力：并行多个注意力头，然后拼接
    
    为什么用多头？
    - 不同的头可以关注不同类型的关系
    - 头1可能关注语法关系，头2关注语义关系...
    - 最终拼接起来，信息更丰富
    """
    
    def __init__(self, num_heads, head_size, n_embd, dropout):
        super().__init__()
        self.heads = nn.ModuleList([
            Head(head_size, n_embd, n_embd, dropout) for _ in range(num_heads)
        ])
        # 投影层：将多头输出合并回原始维度
        self.proj = nn.Linear(n_embd, n_embd)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        # 每个头独立计算注意力，然后拼接
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        out = self.proj(out)  # 线性投影
        out = self.dropout(out)
        return out


class FeedForward(nn.Module):
    """
    前馈网络 (Position-wise Feed-Forward Network)
    
    作用：给每个位置独立地做一个非线性变换
    结构：Linear → ReLU → Linear
    
    注意力层负责"收集信息"，前馈层负责"处理信息"
    """
    
    def __init__(self, n_embd, dropout):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),  # 扩展4倍（标准做法）
            nn.ReLU(),
            nn.Linear(4 * n_embd, n_embd),   # 压缩回原始维度
            nn.Dropout(dropout),
        )
    
    def forward(self, x):
        return self.net(x)


class Block(nn.Module):
    """
    Transformer Block：注意力 + 前馈 + 残差 + 归一化
    
    结构:
    x → LayerNorm → MultiHeadAttention → + (残差)
    x → LayerNorm → FeedForward → + (残差)
    
    残差连接的作用：
    - 让梯度直接流回浅层，缓解梯度消失
    - 让网络更容易学习"在原基础上微调"，而不是"从头学"
    
    Pre-Norm vs Post-Norm：
    这里用的是 Pre-Norm（先归一化再计算），训练更稳定
    """
    
    def __init__(self, n_embd, n_head, block_size, dropout):
        super().__init__()
        head_size = n_embd // n_head
        self.sa = MultiHeadAttention(n_head, head_size, n_embd, dropout)
        self.ffwd = FeedForward(n_embd, dropout)
        self.ln1 = nn.LayerNorm(n_embd)
        self.ln2 = nn.LayerNorm(n_embd)
    
    def forward(self, x):
        # 残差连接 + 注意力
        x = x + self.sa(self.ln1(x))
        # 残差连接 + 前馈
        x = x + self.ffwd(self.ln2(x))
        return x


# ============ GPT 模型 ============

class GPT(nn.Module):
    """
    简化版 GPT 模型
    
    完整结构:
    Token Embedding + Position Embedding
          ↓
    N × Transformer Block (注意力+前馈)
          ↓
    LayerNorm
          ↓
    Linear (映射到词汇表大小)
          ↓
    Softmax (概率分布)
    """
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        # 嵌入层
        self.token_embedding_table = nn.Embedding(config.vocab_size, config.n_embd)
        self.position_embedding_table = nn.Embedding(config.block_size, config.n_embd)
        
        # Transformer 块
        self.blocks = nn.Sequential(*[
            Block(config.n_embd, config.n_head, config.block_size, config.dropout)
            for _ in range(config.n_layer)
        ])
        
        # 最终归一化和输出层
        self.ln_f = nn.LayerNorm(config.n_embd)
        self.lm_head = nn.Linear(config.n_embd, config.vocab_size)
    
    def forward(self, idx, targets=None):
        """
        前向传播
        
        idx: (B, T) 输入 token 序列
        targets: (B, T) 目标 token 序列（可选，用于计算损失）
        """
        B, T = idx.shape
        
        # 1. 获取嵌入
        tok_emb = self.token_embedding_table(idx)  # (B, T, n_embd)
        pos_emb = self.position_embedding_table(torch.arange(T, device=idx.device))  # (T, n_embd)
        x = tok_emb + pos_emb  # 广播相加，token信息 + 位置信息
        
        # 2. 通过 Transformer 块
        x = self.blocks(x)
        
        # 3. 最终归一化和输出
        x = self.ln_f(x)
        logits = self.lm_head(x)  # (B, T, vocab_size)
        
        # 4. 计算损失（如果提供了目标）
        loss = None
        if targets is not None:
            B, T, C = logits.shape
            logits = logits.view(B * T, C)
            targets = targets.view(B * T)
            loss = F.cross_entropy(logits, targets)
        
        return logits, loss
    
    @torch.no_grad()
    def generate(self, idx, max_new_tokens, block_size=None):
        """
        自回归生成：每次预测下一个 token，然后加入序列
        
        idx: (B, T) 起始序列
        max_new_tokens: 要生成的最大新 token 数
        """
        if block_size is None:
            block_size = self.config.block_size
        
        for _ in range(max_new_tokens):
            # 裁剪上下文到 block_size（防止超出训练时的长度）
            idx_cond = idx[:, -block_size:]
            
            # 前向传播
            logits, _ = self(idx_cond)
            
            # 只关注最后一个时间步的预测
            logits = logits[:, -1, :]  # (B, vocab_size)
            
            # 转为概率并采样
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)  # (B, 1)
            
            # 追加到序列
            idx = torch.cat((idx, idx_next), dim=1)
        
        return idx


# ============ 演示 ============

def demo():
    """演示：创建 GPT 模型并生成文本"""
    print("=" * 60)
    print("nanoGPT 演示：Transformer 架构详解")
    print("=" * 60)
    
    # 使用小配置方便演示
    config = GPTConfig(
        vocab_size=65,
        block_size=32,
        n_embd=64,
        n_head=4,
        n_layer=2,
        dropout=0.1,
    )
    
    print(f"\n模型配置:")
    print(f"  词汇表大小: {config.vocab_size}")
    print(f"  上下文长度: {config.block_size}")
    print(f"  嵌入维度:   {config.n_embd}")
    print(f"  注意力头数: {config.n_head}")
    print(f"  每头维度:   {config.n_embd // config.n_head}")
    print(f"  Transformer层数: {config.n_layer}")
    
    # 创建模型
    model = GPT(config)
    
    # 统计参数
    num_params = sum(p.numel() for p in model.parameters())
    print(f"  总参数量:   {num_params:,}")
    
    # 测试前向传播
    print("\n--- 前向传播测试 ---")
    x = torch.randint(0, config.vocab_size, (2, 16))  # batch=2, seq_len=16
    logits, loss = model(x, targets=x)
    print(f"  输入形状:   {x.shape}")
    print(f"  输出形状:   {logits.shape}")
    print(f"  损失值:     {loss.item():.4f}")
    
    # 测试生成
    print("\n--- 生成测试 ---")
    context = torch.zeros((1, 1), dtype=torch.long)  # 从0开始生成
    generated = model.generate(context, max_new_tokens=20)
    print(f"  生成的 token 序列: {generated[0].tolist()}")
    
    # 打印模型架构
    print("\n--- 模型架构 ---")
    print(model)
    
    print("\n✅ 模型创建和测试成功！")
    print("\n架构要点:")
    print("  1. Token嵌入 + 位置嵌入 → 捕获语义和位置信息")
    print("  2. N个Transformer块 → 逐层提取更高层特征")
    print("  3. 每个块: 注意力(全局信息收集) + 前馈(局部信息处理)")
    print("  4. 残差连接 → 梯度直通，训练深层网络")
    print("  5. 层归一化 → 稳定训练过程")


def explain_attention():
    """详解注意力机制的数学原理"""
    print("\n" + "=" * 60)
    print("注意力机制数学原理")
    print("=" * 60)
    
    # 简单示例
    print("\n假设输入序列: ['我', '爱', '编程']")
    
    # 模拟 Q, K, V
    torch.manual_seed(42)
    seq_len = 3
    d_k = 4  # key/query 维度
    d_v = 4  # value 维度
    
    Q = torch.randn(seq_len, d_k)  # 每个位置的 Query
    K = torch.randn(seq_len, d_k)  # 每个位置的 Key
    V = torch.randn(seq_len, d_v)  # 每个位置的 Value
    
    print(f"\nQ (查询) 形状: {Q.shape}")
    print(f"K (键)   形状: {K.shape}")
    print(f"V (值)   形状: {V.shape}")
    
    # Step 1: 计算注意力分数
    scores = Q @ K.T / (d_k ** 0.5)
    print(f"\nStep 1 - 注意力分数 Q @ K.T / sqrt(d_k):")
    print(f"  分数矩阵形状: {scores.shape}")
    print(f"  '我' 对 ['我','爱','编程'] 的注意力分数: {scores[0].tolist()}")
    
    # Step 2: Softmax 归一化
    weights = F.softmax(scores, dim=-1)
    print(f"\nStep 2 - Softmax 归一化 (注意力权重):")
    print(f"  '我' 的注意力分布: {weights[0].tolist()}")
    print(f"  注意: 所有权重之和 = {weights[0].sum().item():.4f}")
    
    # Step 3: 加权求和
    output = weights @ V
    print(f"\nStep 3 - 加权求和 weights @ V:")
    print(f"  输出形状: {output.shape}")
    print(f"  '我' 的输出 = {weights[0][0]:.3f}×V_我 + {weights[0][1]:.3f}×V_爱 + {weights[0][2]:.3f}×V_编")
    
    print("\n核心思想:")
    print("  每个位置通过 Query 询问'我需要什么信息'")
    print("  其他位置通过 Key 回答'我包含什么信息'")
    print("  相似度高的位置获得更大权重")
    print("  最终输出是 Value 的加权组合")


if __name__ == '__main__':
    demo()
    explain_attention()
