"""
makemore — 字符级语言模型
=========================
目标：理解语言模型如何预测下一个字符

核心概念：
- Bigram 模型：只看前一个字符预测下一个
- MLP 语言模型：用神经网络学习字符模式
- 词嵌入(Embedding)：将离散字符映射为连续向量
- Softmax：将原始分数转为概率分布

来源：Andrej Karpathy 的 makemore 项目复现
"""

import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
import random

# ============ 数据准备 ============

def load_names(filepath=None):
    """
    加载名字数据集。如果没有文件，使用内置示例。
    """
    if filepath:
        with open(filepath, 'r') as f:
            names = f.read().splitlines()
    else:
        # 内置示例数据
        names = [
            'emma', 'olivia', 'ava', 'isabella', 'sophia',
            'charlotte', 'mia', 'amelia', 'harper', 'evelyn',
            'liam', 'noah', 'oliver', 'elijah', 'james',
            'benjamin', 'lucas', 'mason', 'ethan', 'alexander',
            'bob', 'alice', 'david', 'sarah', 'michael',
        ] * 10  # 重复增加数据量
        random.shuffle(names)
    
    return names


# ============ 方案1：Bigram 模型 ============

class BigramModel:
    """
    Bigram 模型：统计相邻字符的共现频率
    
    思路：
    - 统计 "a后面跟b" 的次数
    - 用频率估计概率
    - 按概率采样生成新名字
    """
    
    def __init__(self):
        self.chars = []
        self.stoi = {}  # string to index
        self.itos = {}  # index to string
        self.N = None   # 计数矩阵
    
    def fit(self, names):
        """训练：统计字符对的出现次数"""
        # 构建字符表
        all_chars = set()
        for name in names:
            all_chars.update(name)
        all_chars.add('.')  # 特殊标记：开始/结束
        
        self.chars = sorted(all_chars)
        self.stoi = {ch: i for i, ch in enumerate(self.chars)}
        self.itos = {i: ch for ch, i in self.stoi.items()}
        
        # 统计 bigram 频率
        self.N = torch.zeros(len(self.chars), len(self.chars), dtype=torch.int32)
        
        for name in names:
            chs = ['.'] + list(name) + ['.']
            for ch1, ch2 in zip(chs, chs[1:]):
                self.N[self.stoi[ch1], self.stoi[ch2]] += 1
        
        return self
    
    def probability(self):
        """将计数矩阵转为概率矩阵"""
        P = self.N.float()
        P = P / P.sum(dim=1, keepdim=True)  # 每行归一化
        return P
    
    def generate(self, num=10):
        """生成新名字"""
        P = self.probability()
        names = []
        
        for _ in range(num):
            out = []
            ix = self.stoi['.']  # 从开始标记出发
            
            while True:
                # 根据概率分布采样下一个字符
                p = P[ix]
                ix = torch.multinomial(p, num_samples=1).item()
                if ix == self.stoi['.']:
                    break
                out.append(self.itos[ix])
            
            names.append(''.join(out))
        
        return names
    
    def evaluate(self, names):
        """计算负对数似然损失（越低越好）"""
        P = self.probability()
        log_likelihood = 0.0
        n = 0
        
        for name in names:
            chs = ['.'] + list(name) + ['.']
            for ch1, ch2 in zip(chs, chs[1:]):
                prob = P[self.stoi[ch1], self.stoi[ch2]]
                log_likelihood += torch.log(prob)
                n += 1
        
        return -log_likelihood / n  # 负平均对数似然


# ============ 方案2：神经网络 Bigram ============

class NeuralBigram:
    """
    用神经网络（单层）实现 bigram 模型
    
    核心思想：
    - 输入：当前字符的 one-hot 编码
    - 输出：下一个字符的概率分布
    - 训练：梯度下降最小化交叉熵损失
    """
    
    def __init__(self, num_chars):
        self.num_chars = num_chars
        # 随机初始化权重矩阵
        # W[i][j] 表示字符i后面出现字符j的"分数"
        self.W = torch.randn(num_chars, num_chars, requires_grad=True)
    
    def fit(self, stoi, itos, names, epochs=500, lr=50):
        """训练模型"""
        losses = []
        
        for epoch in range(epochs):
            # 构建训练数据
            xs, ys = [], []
            for name in names:
                chs = ['.'] + list(name) + ['.']
                for ch1, ch2 in zip(chs, chs[1:]):
                    xs.append(stoi[ch1])
                    ys.append(stoi[ch2])
            
            xs = torch.tensor(xs)
            ys = torch.tensor(ys)
            num = xs.nelement()
            
            # 前向传播
            xenc = F.one_hot(xs, num_classes=self.num_chars).float()
            logits = xenc @ self.W  # 预测的 log-counts
            counts = logits.exp()   # 等价于 N 矩阵
            probs = counts / counts.sum(dim=1, keepdim=True)  # softmax
            
            # 损失：负对数似然
            loss = -probs[torch.arange(num), ys].log().mean()
            
            # 反向传播
            self.W.grad = None
            loss.backward()
            
            # 更新参数
            self.W.data -= lr * self.W.grad
            
            if epoch % 100 == 0:
                losses.append(loss.item())
                print(f"  Epoch {epoch:4d} | Loss: {loss.item():.4f}")
        
        return losses
    
    def generate(self, stoi, itos, num=10):
        """生成新名字"""
        names = []
        
        for _ in range(num):
            out = []
            ix = stoi['.']
            
            while True:
                xenc = F.one_hot(torch.tensor([ix]), num_classes=self.num_chars).float()
                logits = xenc @ self.W
                counts = logits.exp()
                probs = counts / counts.sum(dim=1, keepdim=True)
                
                ix = torch.multinomial(probs, num_samples=1).item()
                if ix == stoi['.']:
                    break
                out.append(itos[ix])
            
            names.append(''.join(out))
        
        return names


# ============ 方案3：MLP 语言模型 ============

class MLPLanguageModel:
    """
    MLP 语言模型：用前馈神经网络学习字符模式
    
    思路（来自 Bengio et al. 2003）：
    - 用前 N 个字符的嵌入向量拼接作为输入
    - 通过隐藏层非线性变换
    - 输出下一个字符的概率分布
    """
    
    def __init__(self, vocab_size, embed_dim=10, context_len=3, hidden_size=200):
        self.context_len = context_len
        
        # 字符嵌入表：将每个字符映射为一个向量
        self.C = torch.randn(vocab_size, embed_dim)
        
        # 隐藏层
        fan_in = embed_dim * context_len
        self.W1 = torch.randn(fan_in, hidden_size) * 0.01
        self.b1 = torch.randn(hidden_size) * 0.01
        
        # 输出层
        self.W2 = torch.randn(hidden_size, vocab_size) * 0.01
        self.b2 = torch.randn(vocab_size) * 0.01
        
        # 收集所有参数
        self.params = [self.C, self.W1, self.b1, self.W2, self.b2]
        for p in self.params:
            p.requires_grad = True
    
    def fit(self, stoi, itos, names, epochs=50000, lr=0.1, batch_size=32):
        """训练模型（mini-batch 梯度下降）"""
        # 构建数据集
        X, Y = [], []
        for name in names:
            context = [stoi['.']] * self.context_len
            for ch in name + '.':
                ix = stoi[ch]
                X.append(context)
                Y.append(ix)
                context = context[1:] + [ix]
        
        X = torch.tensor(X)
        Y = torch.tensor(Y)
        
        for epoch in range(epochs):
            # Mini-batch
            ix = torch.randint(0, len(X), (batch_size,))
            xb, yb = X[ix], Y[ix]
            
            # 前向传播
            # 1. 嵌入查找
            emb = self.C[xb]  # (batch, context_len, embed_dim)
            emb_cat = emb.view(emb.shape[0], -1)  # 拼接
            
            # 2. 隐藏层
            h = torch.tanh(emb_cat @ self.W1 + self.b1)
            
            # 3. 输出层
            logits = h @ self.W2 + self.b2
            loss = F.cross_entropy(logits, yb)
            
            # 反向传播
            for p in self.params:
                p.grad = None
            loss.backward()
            
            # 更新
            for p in self.params:
                p.data -= lr * p.grad
            
            if epoch % 50000 == 0:
                print(f"  Epoch {epoch:7d} | Loss: {loss.item():.4f}")
        
        # 最终在全部数据上的损失
        with torch.no_grad():
            emb = self.C[X]
            emb_cat = emb.view(emb.shape[0], -1)
            h = torch.tanh(emb_cat @ self.W1 + self.b1)
            logits = h @ self.W2 + self.b2
            final_loss = F.cross_entropy(logits, Y)
            print(f"  Final Loss: {final_loss.item():.4f}")
        
        return final_loss.item()
    
    def generate(self, stoi, itos, num=10):
        """生成新名字"""
        names = []
        
        for _ in range(num):
            out = []
            context = [stoi['.']] * self.context_len
            
            while True:
                # 嵌入
                emb = self.C[torch.tensor([context])]
                emb_cat = emb.view(1, -1)
                
                # 隐藏层
                h = torch.tanh(emb_cat @ self.W1 + self.b1)
                
                # 输出层
                logits = h @ self.W2 + self.b2
                probs = F.softmax(logits, dim=1)
                
                # 采样
                ix = torch.multinomial(probs, num_samples=1).item()
                if ix == stoi['.']:
                    break
                out.append(itos[ix])
                context = context[1:] + [ix]
            
            names.append(''.join(out))
        
        return names


# ============ 演示 ============

def demo():
    print("=" * 60)
    print("makemore 演示：字符级语言模型")
    print("=" * 60)
    
    # 加载数据
    names = load_names()
    print(f"\n数据集: {len(names)} 个名字")
    print(f"示例: {names[:5]}")
    
    # 构建字符表
    all_chars = set()
    for name in names:
        all_chars.update(name)
    all_chars.add('.')
    chars = sorted(all_chars)
    stoi = {ch: i for i, ch in enumerate(chars)}
    itos = {i: ch for ch, i in stoi.items()}
    vocab_size = len(chars)
    print(f"字符表大小: {vocab_size}")
    
    # ---- 方案1: Bigram 统计模型 ----
    print("\n--- 方案1: Bigram 统计模型 ---")
    bigram = BigramModel()
    bigram.fit(names)
    loss1 = bigram.evaluate(names)
    print(f"  训练损失: {loss1:.4f}")
    generated = bigram.generate(5)
    print(f"  生成: {generated}")
    
    # ---- 方案2: 神经网络 Bigram ----
    print("\n--- 方案2: 神经网络 Bigram ---")
    nbigram = NeuralBigram(vocab_size)
    nbigram.fit(stoi, itos, names, epochs=500, lr=50)
    generated = nbigram.generate(stoi, itos, 5)
    print(f"  生成: {generated}")
    
    # ---- 方案3: MLP 语言模型 ----
    print("\n--- 方案3: MLP 语言模型 (上下文长度=3) ---")
    mlp = MLPLanguageModel(vocab_size, embed_dim=10, context_len=3, hidden_size=200)
    mlp.fit(stoi, itos, names, epochs=30000, lr=0.1)
    generated = mlp.generate(stoi, itos, 10)
    print(f"  生成: {generated}")
    
    print("\n✅ 所有模型训练完成！")
    print("注意：MLP 模型生成的名字质量明显优于简单 Bigram")


if __name__ == '__main__':
    demo()
