"""
makemore_annotated.py — 逐行解释注释版
======================================
字符级语言模型的完整实现与教学注释

文件特点：
1. ✅ 逐行中文解释：每行代码都有详细解释
2. ✅ 设计意图说明：为什么这样设计
3. ✅ 替代方案对比：其他实现方式的优缺点
4. ✅ 常见错误提醒：初学者容易犯的错误
5. ✅ 核心概念标注：重点概念用⭐标记

学习路线：
1. Bigram 模型：最简单的统计模型
2. MLP 语言模型：神经网络模型
3. 词嵌入：字符向量表示
4. 训练循环：梯度下降优化

作者：哆啦claw梦
创建时间：2026-04-06
"""

# ============ 1. 导入模块 ============

import torch  # 🔹 PyTorch 深度学习框架，提供张量计算和自动求导
import torch.nn.functional as F  # 🔹 PyTorch 函数库，包含激活函数、损失函数等
import matplotlib.pyplot as plt  # 🔹 Matplotlib 绘图库，用于可视化
import random  # 🔹 Python 随机模块，用于数据打乱

print("✅ 模块导入完成：PyTorch用于深度学习，Matplotlib用于可视化")

# ============ 2. 数据准备 ============

def load_names(filepath=None):
    """
    加载名字数据集的函数
    
    参数：
    - filepath: 可选的文件路径。如果提供，从文件读取；否则使用内置示例数据
    
    返回：
    - names: 名字列表，如 ['emma', 'olivia', 'ava', ...]
    
    ⭐ 核心概念：数据是机器学习的燃料，好的数据准备是成功的一半
    """
    if filepath:
        # 🔹 从文件加载数据
        with open(filepath, 'r') as f:
            names = f.read().splitlines()  # 🔹 splitlines() 按行分割，去除换行符
    else:
        # 🔹 使用内置示例数据（用于教学演示）
        names = [
            'emma', 'olivia', 'ava', 'isabella', 'sophia',
            'charlotte', 'mia', 'amelia', 'harper', 'evelyn',
            'liam', 'noah', 'oliver', 'elijah', 'james',
            'benjamin', 'lucas', 'mason', 'ethan', 'alexander',
            'bob', 'alice', 'david', 'sarah', 'michael',
        ] * 10  # 🔹 重复10次以增加数据量
        random.shuffle(names)  # 🔹 随机打乱顺序，避免模式固定
    
    return names  # 🔹 返回名字列表

# ⚠️ 注意事项：
# 1. 实际应用中应该从文件加载真实数据
# 2. 数据量不足时模型容易过拟合
# 3. 数据清洗很重要（去除空白、特殊字符等）

# ============ 3. 数据预处理 ============

def prepare_data(names):
    """
    将名字数据转换为模型可用的格式
    
    步骤：
    1. 构建字符字典：所有出现字符的映射表
    2. 添加特殊标记：<S>表示开始，<E>表示结束
    3. 将名字转换为索引序列
    
    参数：
    - names: 名字列表
    
    返回：
    - stoi: 字符到索引的字典，如 {'a': 0, 'b': 1, ...}
    - itos: 索引到字符的列表，如 [0: 'a', 1: 'b', ...]
    - vocab_size: 词汇表大小（唯一字符数量）
    """
    
    # 3.1 提取所有字符并排序
    chars = sorted(list(set(''.join(names))))  # 🔹 set去重，sorted排序
    # 解释：''.join(names) 将所有名字连接成一个字符串
    #      set() 提取唯一字符
    #      list() 转换为列表
    #      sorted() 按字母顺序排序
    
    # 3.2 构建字符到索引的映射（stoi = string to index）
    stoi = {s: i+1 for i, s in enumerate(chars)}  # 🔹 i+1 为特殊标记留出位置0
    # 解释：枚举chars列表，为每个字符分配一个索引（从1开始）
    #      为什么从1开始？因为0要留给特殊标记
    
    # 3.3 添加特殊标记
    stoi['<S>'] = 0  # 🔹 <S> 表示序列开始（Start）
    stoi['<E>'] = len(stoi)  # 🔹 <E> 表示序列结束（End），索引为当前最大索引+1
    
    # 3.4 构建索引到字符的映射（itos = index to string）
    itos = {i: s for s, i in stoi.items()}  # 🔹 反转stoi字典
    
    # 3.5 计算词汇表大小
    vocab_size = len(stoi)  # 🔹 包括所有字符和特殊标记
    
    return stoi, itos, vocab_size

# 💡 实战技巧：
# 1. 特殊标记可以处理变长序列
# 2. 从1开始编号为后续扩展留出空间
# 3. 保持映射的一致性很重要

# ============ 4. Bigram 模型（统计模型） ============

class BigramModel:
    """
    Bigram模型：基于统计的简单语言模型
    
    原理：
    - 只考虑前一个字符预测下一个字符
    - 统计所有字符对的共现频率
    - 使用这些频率作为预测概率
    
    优点：简单直观，计算快
    缺点：无法捕获长距离依赖
    
    ⭐ 核心概念：Bigram = 二元语法，马尔可夫假设
    """
    
    def __init__(self, vocab_size):
        """
        初始化Bigram模型
        
        参数：
        - vocab_size: 词汇表大小（包括特殊标记）
        
        初始化内容：
        - counts: 计数矩阵，记录字符对的出现次数
        - probs: 概率矩阵，通过归一化计数得到
        """
        self.vocab_size = vocab_size  # 🔹 存储词汇表大小
        
        # 创建计数矩阵，形状为(vocab_size, vocab_size)
        # 行：前一个字符，列：后一个字符
        self.counts = torch.zeros((vocab_size, vocab_size), dtype=torch.float32)
        # 🔹 使用float32而不是int，便于后续计算概率
        
        print(f"✅ Bigram模型初始化完成，词汇表大小：{vocab_size}")
    
    def train(self, names, stoi):
        """
        训练Bigram模型：统计字符对出现次数
        
        参数：
        - names: 名字列表
        - stoi: 字符到索引的映射
        
        过程：
        1. 遍历每个名字
        2. 为每个名字添加开始和结束标记
        3. 统计相邻字符的出现次数
        """
        print("🚀 开始训练Bigram模型...")
        
        for name in names:  # 🔹 遍历每个名字
            # 将名字转换为索引序列，并添加特殊标记
            indices = [stoi['<S>']] + [stoi[ch] for ch in name] + [stoi['<E>']]
            # 🔹 [stoi[ch] for ch in name]：将每个字符转换为索引
            # 🔹 前后分别添加开始和结束标记
            
            # 统计相邻字符对的出现次数
            for i in range(len(indices) - 1):  # 🔹 遍历每个字符对
                current_idx = indices[i]      # 🔹 当前字符索引
                next_idx = indices[i + 1]     # 🔹 下一个字符索引
                self.counts[current_idx, next_idx] += 1  # 🔹 计数+1
        
        # 计算概率矩阵：每行归一化为概率分布
        row_sums = self.counts.sum(dim=1, keepdim=True)  # 🔹 每行的和
        
        # 安全除法：避免除以零
        self.probs = torch.where(
            row_sums > 0, 
            self.counts / row_sums, 
            torch.zeros_like(self.counts)
        )
        # 🔹 where(条件, 真值, 假值)：条件为真时返回真值，否则返回假值
        # 🔹 这里处理了零行的情况
        
        # 添加小常数避免完全为零（用于生成时的采样）
        self.probs = self.probs + 1e-10
        # 重新归一化
        self.probs = self.probs / self.probs.sum(dim=1, keepdim=True)
        
        print(f"✅ Bigram模型训练完成，共处理 {len(names)} 个名字")
    
    def generate(self, itos, max_len=20, seed=None):
        """
        使用Bigram模型生成新名字
        
        参数：
        - itos: 索引到字符的映射
        - max_len: 最大生成长度（防止无限循环）
        - seed: 随机种子（用于可重复性）
        
        返回：
        - generated_name: 生成的名字字符串
        """
        if seed is not None:
            torch.manual_seed(seed)  # 🔹 设置随机种子确保结果可复现
        
        generated_indices = []  # 🔹 存储生成的索引
        current_idx = 0  # 🔹 从开始标记 <S> 开始（索引为0）
        
        for _ in range(max_len):  # 🔹 最多生成max_len个字符
            # 获取当前字符的概率分布
            prob_dist = self.probs[current_idx]  # 🔹 形状为(vocab_size,)
            
            # ⚠️ 安全处理：如果概率分布全为0，随机选择一个字符
            if prob_dist.sum().item() == 0:
                # 均匀分布随机选择（排除开始标记）
                possible_indices = list(range(1, len(prob_dist)))
                if possible_indices:
                    next_idx = random.choice(possible_indices)
                else:
                    break  # 没有可选的字符
            else:
                # 基于概率分布采样下一个字符
                next_idx = torch.multinomial(prob_dist, 1).item()
                # 🔹 multinomial：多项式分布采样
                # 🔹 1：采样数量
                # 🔹 item()：将张量转换为Python整数
            
            # 🔹 获取结束标记索引
            end_idx = max(itos.keys()) if isinstance(itos, dict) else len(itos) - 1
            
            if next_idx == end_idx:  # 🔹 检查是否为结束标记 <E>
                break  # 🔹 遇到结束标记，停止生成
            
            generated_indices.append(next_idx)  # 🔹 添加到结果列表
            current_idx = next_idx  # 🔹 更新当前字符
        
        # 将索引转换为字符
        generated_name = ''.join([itos[idx] for idx in generated_indices])
        
        return generated_name
    
    def evaluate(self, names, stoi):
        """
        评估Bigram模型在测试数据上的性能
        
        参数：
        - names: 测试名字列表
        - stoi: 字符到索引的映射
        
        返回：
        - avg_log_likelihood: 平均对数似然（越大越好）
        - perplexity: 困惑度（越小越好）
        """
        total_log_likelihood = 0.0  # 🔹 总对数似然
        total_chars = 0  # 🔹 总字符数
        
        for name in names:
            indices = [stoi['<S>']] + [stoi[ch] for ch in name] + [stoi['<E>']]
            
            for i in range(len(indices) - 1):
                current_idx = indices[i]
                next_idx = indices[i + 1]
                
                # 获取真实概率
                prob = self.probs[current_idx, next_idx]
                
                # 计算对数似然（加小常数避免log(0)）
                log_prob = torch.log(prob + 1e-10)
                total_log_likelihood += log_prob.item()
                total_chars += 1
        
        # 计算平均对数似然和困惑度
        avg_log_likelihood = total_log_likelihood / total_chars if total_chars > 0 else -float('inf')
        perplexity = torch.exp(-torch.tensor(avg_log_likelihood)).item()
        
        return avg_log_likelihood, perplexity

# ⚠️ 常见错误：
# 1. 忘记处理零行（除以零错误）
# 2. 没有添加特殊标记导致序列长度不一致
# 3. 混淆行和列的方向

print("✅ Bigram模型类定义完成")

# ============ 5. 神经网络模型（MLP） ============

class MLPLanguageModel(torch.nn.Module):
    """
    MLP语言模型：使用神经网络学习字符模式
    
    架构：
    1. 词嵌入层：将字符索引转换为向量
    2. 隐藏层：全连接层 + 激活函数
    3. 输出层：将隐藏状态转换为字符概率
    
    优势：
    - 可以学习非线性模式
    - 泛化能力比统计模型强
    - 支持梯度下降优化
    
    ⭐ 核心概念：词嵌入、前向传播、反向传播
    """
    
    def __init__(self, vocab_size, embedding_dim=10, hidden_dim=200):
        """
        初始化MLP语言模型
        
        参数：
        - vocab_size: 词汇表大小
        - embedding_dim: 词嵌入维度（默认10）
        - hidden_dim: 隐藏层维度（默认200）
        
        网络结构：
        - embedding: 词嵌入层，将索引映射为向量
        - fc1: 第一个全连接层（embedding_dim → hidden_dim）
        - fc2: 第二个全连接层（hidden_dim → hidden_dim）
        - fc3: 输出层（hidden_dim → vocab_size）
        """
        super().__init__()  # 🔹 调用父类torch.nn.Module的初始化
        
        # 词嵌入层
        self.embedding = torch.nn.Embedding(vocab_size, embedding_dim)
        # 🔹 输入：字符索引（形状 [batch_size, sequence_length]）
        # 🔹 输出：词向量（形状 [batch_size, sequence_length, embedding_dim]）
        
        # 第一个全连接层（含批量归一化）
        self.fc1 = torch.nn.Linear(embedding_dim, hidden_dim)
        self.bn1 = torch.nn.BatchNorm1d(hidden_dim)  # 🔹 批量归一化，加速训练
        
        # 第二个全连接层
        self.fc2 = torch.nn.Linear(hidden_dim, hidden_dim)
        self.bn2 = torch.nn.BatchNorm1d(hidden_dim)
        
        # 输出层（没有激活函数，后面接Softmax）
        self.fc3 = torch.nn.Linear(hidden_dim, vocab_size)
        
        # 初始化权重（重要！）
        self._init_weights()
        
        print(f"✅ MLP语言模型初始化完成")
        print(f"   - 词嵌入维度: {embedding_dim}")
        print(f"   - 隐藏层维度: {hidden_dim}")
        print(f"   - 总参数量: {self._count_parameters():,}")
    
    def _init_weights(self):
        """
        初始化网络权重（Xavier初始化）
        
        为什么需要初始化？
        - 避免梯度消失或爆炸
        - 加速收敛
        - 提高训练稳定性
        """
        for layer in [self.fc1, self.fc2, self.fc3]:
            torch.nn.init.xavier_uniform_(layer.weight)  # 🔹 Xavier均匀初始化
            torch.nn.init.zeros_(layer.bias)  # 🔹 偏置初始化为0
        
        # 词嵌入层使用较小的初始化
        torch.nn.init.normal_(self.embedding.weight, mean=0, std=0.01)
    
    def _count_parameters(self):
        """计算模型总参数量"""
        return sum(p.numel() for p in self.parameters())
    
    def forward(self, x):
        """
        前向传播
        
        参数：
        - x: 输入张量，形状 [batch_size, context_size]
           context_size是上下文长度（看前几个字符）
        
        返回：
        - logits: 原始分数，形状 [batch_size, vocab_size]
        """
        # 1. 词嵌入查找
        embedded = self.embedding(x)  # 🔹 形状: [batch_size, context_size, embedding_dim]
        
        # 2. 平均池化（将上下文信息聚合）
        # 为什么用平均池化？对位置不敏感，简单有效
        context_vector = embedded.mean(dim=1)  # 🔹 形状: [batch_size, embedding_dim]
        
        # 3. 第一个全连接层 + 批量归一化 + ReLU激活
        h = self.fc1(context_vector)  # 🔹 形状: [batch_size, hidden_dim]
        h = self.bn1(h)  # 🔹 批量归一化（仅在训练时起作用）
        h = torch.relu(h)  # 🔹 ReLU激活函数
        
        # 4. 第二个全连接层 + 批量归一化 + ReLU激活
        h = self.fc2(h)
        h = self.bn2(h)
        h = torch.relu(h)
        
        # 5. 输出层（无激活函数）
        logits = self.fc3(h)  # 🔹 形状: [batch_size, vocab_size]
        
        return logits
    
    def train_model(self, train_data, val_data=None, epochs=100, lr=0.1, batch_size=32):
        """
        训练MLP模型
        
        参数：
        - train_data: 训练数据 (X, y) 元组
        - val_data: 验证数据（可选）
        - epochs: 训练轮数
        - lr: 学习率
        - batch_size: 批量大小
        
        返回：
        - train_losses: 训练损失历史
        - val_losses: 验证损失历史（如果有验证数据）
        """
        print("🚀 开始训练MLP语言模型...")
        
        X_train, y_train = train_data
        if val_data:
            X_val, y_val = val_data
        
        # 优化器：随机梯度下降
        optimizer = torch.optim.SGD(self.parameters(), lr=lr)
        # 🔹 SGD：随机梯度下降，简单但有效
        # 🔹 其他选择：Adam, RMSprop等
        
        # 损失函数：交叉熵损失
        criterion = torch.nn.CrossEntropyLoss()
        # 🔹 CrossEntropyLoss = Softmax + 负对数似然
        
        train_losses = []
        val_losses = [] if val_data else None
        
        # 训练循环
        for epoch in range(epochs):
            # 打乱训练数据（重要！避免过拟合）
            indices = torch.randperm(len(X_train))
            X_shuffled = X_train[indices]
            y_shuffled = y_train[indices]
            
            epoch_loss = 0.0
            num_batches = 0
            
            # 批量训练
            for i in range(0, len(X_train), batch_size):
                # 获取当前批次
                batch_X = X_shuffled[i:i+batch_size]
                batch_y = y_shuffled[i:i+batch_size]
                
                # 前向传播
                logits = self(batch_X)  # 🔹 调用forward方法
                loss = criterion(logits, batch_y)
                
                # 反向传播
                optimizer.zero_grad()  # 🔹 清空梯度（重要！）
                loss.backward()  # 🔹 计算梯度
                optimizer.step()  # 🔹 更新参数
                
                epoch_loss += loss.item()
                num_batches += 1
            
            # 计算平均损失
            avg_loss = epoch_loss / num_batches
            train_losses.append(avg_loss)
            
            # 验证（如果有验证数据）
            if val_data:
                with torch.no_grad():  # 🔹 不计算梯度，节省内存
                    val_logits = self(X_val)
                    val_loss = criterion(val_logits, y_val).item()
                    val_losses.append(val_loss)
            
            # 打印进度（每10轮打印一次）
            if (epoch + 1) % 10 == 0 or epoch == 0:
                msg = f"Epoch {epoch+1:3d}/{epochs} | Train Loss: {avg_loss:.4f}"
                if val_data:
                    msg += f" | Val Loss: {val_losses[-1]:.4f}"
                print(msg)
        
        print("✅ MLP模型训练完成")
        return train_losses, val_losses

# 💡 实战技巧：
# 1. 使用批量归一化加速训练
# 2. 学习率调整可以改善收敛
# 3. 早停（early stopping）防止过拟合

print("✅ MLP语言模型类定义完成")

# ============ 6. 创建训练数据 ============

def create_training_data(names, stoi, context_size=3):
    """
    为神经网络模型创建训练数据
    
    参数：
    - names: 名字列表
    - stoi: 字符到索引的映射
    - context_size: 上下文大小（看前几个字符）
    
    返回：
    - X: 输入特征，形状 [num_samples, context_size]
    - y: 目标标签，形状 [num_samples]
    """
    X, y = [], []
    
    for name in names:
        # 为每个名字添加开始和结束标记
        indices = [stoi['<S>']] + [stoi[ch] for ch in name] + [stoi['<E>']]
        
        # 创建上下文-目标对
        for i in range(len(indices) - context_size):
            # 上下文：前context_size个字符
            context = indices[i:i+context_size]
            # 目标：下一个字符
            target = indices[i+context_size]
            
            X.append(context)
            y.append(target)
    
    # 转换为PyTorch张量
    X_tensor = torch.tensor(X, dtype=torch.long)
    y_tensor = torch.tensor(y, dtype=torch.long)
    
    print(f"✅ 训练数据创建完成")
    print(f"   - 样本数量: {len(X)}")
    print(f"   - 上下文大小: {context_size}")
    print(f"   - X形状: {X_tensor.shape}")
    print(f"   - y形状: {y_tensor.shape}")
    
    return X_tensor, y_tensor

# ============ 7. 主函数：演示使用 ============

def main():
    """
    主函数：演示如何使用makemore模型
    
    步骤：
    1. 加载数据
    2. 数据预处理
    3. 训练Bigram模型
    4. 训练MLP模型
    5. 生成新名字
    6. 可视化结果
    """
    print("=" * 60)
    print("makemore 字符级语言模型演示")
    print("=" * 60)
    
    # 1. 加载数据
    print("\n1️⃣ 加载数据...")
    names = load_names()
    print(f"   加载了 {len(names)} 个名字")
    print(f"   示例名字: {names[:5]}")
    
    # 2. 数据预处理
    print("\n2️⃣ 数据预处理...")
    stoi, itos, vocab_size = prepare_data(names)
    print(f"   词汇表大小: {vocab_size}")
    print(f"   字符映射: {list(stoi.items())[:5]}...")
    
    # 3. Bigram模型演示
    print("\n3️⃣ Bigram模型演示...")
    bigram = BigramModel(vocab_size)
    bigram.train(names, stoi)
    
    # 生成名字
    print("\n   📝 生成新名字:")
    for i in range(5):
        name = bigram.generate(itos, seed=i)
        print(f"      {i+1}. {name}")
    
    # 评估
    log_likelihood, perplexity = bigram.evaluate(names[:10], stoi)
    print(f"   📊 评估结果: 对数似然={log_likelihood:.3f}, 困惑度={perplexity:.3f}")
    
    # 4. MLP模型演示
    print("\n4️⃣ MLP模型演示...")
    
    # 创建训练数据
    context_size = 3
    X_train, y_train = create_training_data(names, stoi, context_size)
    
    # 分割训练集和验证集
    split_idx = int(0.8 * len(X_train))
    X_train_split = X_train[:split_idx]
    y_train_split = y_train[:split_idx]
    X_val_split = X_train[split_idx:]
    y_val_split = y_train[split_idx:]
    
    # 创建模型
    mlp = MLPLanguageModel(vocab_size, embedding_dim=10, hidden_dim=100)
    
    # 训练模型
    train_losses, val_losses = mlp.train_model(
        train_data=(X_train_split, y_train_split),
        val_data=(X_val_split, y_val_split),
        epochs=50,
        lr=0.1,
        batch_size=32
    )
    
    # 5. 生成名字（MLP）
    print("\n5️⃣ MLP生成新名字...")
    
    def mlp_generate(mlp_model, stoi, itos, context_size=3, max_len=20, seed=42):
        """使用MLP模型生成名字"""
        if seed is not None:
            torch.manual_seed(seed)
        
        # 从开始标记开始
        context = [stoi['<S>']] * context_size
        generated = []
        
        for _ in range(max_len):
            # 准备输入
            x = torch.tensor([context[-context_size:]], dtype=torch.long)
            
            # 前向传播
            with torch.no_grad():
                logits = mlp_model(x)
                probs = torch.softmax(logits, dim=1)
            
            # 采样
            next_idx = torch.multinomial(probs, 1).item()
            
            # 检查结束标记
            if next_idx == stoi['<E>']:
                break
            
            # 更新
            generated.append(itos[next_idx])
            context.append(next_idx)
        
        return ''.join(generated)
    
    print("\n   📝 MLP生成的名字:")
    for i in range(5):
        name = mlp_generate(mlp, stoi, itos, seed=i)
        print(f"      {i+1}. {name}")
    
    # 6. 可视化
    print("\n6️⃣ 可视化训练过程...")
    
    plt.figure(figsize=(12, 4))
    
    # 训练损失曲线
    plt.subplot(1, 2, 1)
    plt.plot(train_losses, label='训练损失')
    if val_losses:
        plt.plot(val_losses, label='验证损失')
    plt.xlabel('训练轮数')
    plt.ylabel('损失')
    plt.title('训练损失曲线')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Bigram概率矩阵可视化
    plt.subplot(1, 2, 2)
    plt.imshow(bigram.probs.numpy(), cmap='viridis', aspect='auto')
    plt.colorbar(label='概率')
    plt.title('Bigram概率矩阵')
    plt.xlabel('下一个字符')
    plt.ylabel('当前字符')
    
    plt.tight_layout()
    plt.show()
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)
    
    return bigram, mlp, stoi, itos

# ============ 8. 辅助函数 ============

def save_model(model, filepath):
    """保存模型到文件"""
    torch.save(model.state_dict(), filepath)
    print(f"✅ 模型已保存到: {filepath}")

def load_model(model_class, filepath, vocab_size, **kwargs):
    """从文件加载模型"""
    model = model_class(vocab_size, **kwargs)
    model.load_state_dict(torch.load(filepath))
    model.eval()  # 🔹 设置为评估模式
    print(f"✅ 模型已从 {filepath} 加载")
    return model

# ============ 9. 测试函数 ============

def test_bigram_model():
    """测试Bigram模型"""
    print("🧪 测试Bigram模型...")
    
    # 创建测试数据
    test_names = ['test', 'demo', 'sample']
    
    # 预处理
    stoi, itos, vocab_size = prepare_data(test_names)
    
    # 创建并训练模型
    model = BigramModel(vocab_size)
    model.train(test_names, stoi)
    
    # 测试生成
    name = model.generate(itos, seed=123)
    print(f"   生成的名字: {name}")
    
    # 测试评估
    log_likelihood, perplexity = model.evaluate(test_names, stoi)
    print(f"   对数似然: {log_likelihood:.3f}, 困惑度: {perplexity:.3f}")
    
    print("✅ Bigram模型测试通过")

def test_mlp_model():
    """测试MLP模型"""
    print("🧪 测试MLP模型...")
    
    # 创建测试数据
    test_names = ['cat', 'dog', 'bird'] * 5
    stoi, itos, vocab_size = prepare_data(test_names)
    
    # 创建训练数据
    X, y = create_training_data(test_names, stoi, context_size=2)
    
    # 创建模型
    model = MLPLanguageModel(vocab_size, embedding_dim=5, hidden_dim=20)
    
    # 测试前向传播
    test_input = X[:2]
    output = model(test_input)
    print(f"   输入形状: {test_input.shape}")
    print(f"   输出形状: {output.shape}")
    print(f"   前向传播测试通过")
    
    print("✅ MLP模型测试通过")

# ============ 10. 执行入口 ============

if __name__ == "__main__":
    """
    程序入口点
    
    当直接运行此文件时，会执行以下操作：
    1. 运行完整演示
    2. 运行单元测试
    
    使用方式：
    python makemore_annotated.py          # 运行完整演示
    python makemore_annotated.py --test   # 只运行测试
    """
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # 只运行测试
        test_bigram_model()
        test_mlp_model()
    else:
        # 运行完整演示
        bigram, mlp, stoi, itos = main()
        
        # 可选：保存模型
        # save_model(bigram, "bigram_model.pth")
        # save_model(mlp, "mlp_model.pth")

# ============ 11. 学习总结 ============

"""
📚 学习总结：

1. Bigram模型：
   - 原理：统计相邻字符的频率
   - 优点：简单快速，易于理解
   - 缺点：无法捕获长距离依赖
   - 应用：简单的文本生成，教学演示

2. MLP语言模型：
   - 原理：神经网络学习字符模式
   - 核心：词嵌入 + 全连接层
   - 优势：可以学习复杂模式，泛化能力强
   - 训练：梯度下降 + 反向传播

3. 关键概念：
   - 词嵌入：将离散字符映射为连续向量
   - Softmax：将分数转换为概率分布
   - 交叉熵损失：衡量预测与真实的差异
   - 困惑度：评估语言模型性能的指标

4. 实际应用：
   - 名字生成
   - 拼写检查
   - 文本补全
   - 密码生成

5. 进阶方向：
   - RNN/LSTM：处理序列数据
   - Transformer：现代语言模型的基础
   - 注意力机制：处理长距离依赖
   - 预训练语言模型：GPT, BERT等

⭐ 核心收获：
- 理解了语言模型的基本原理
- 掌握了PyTorch的基本使用
- 学会了如何训练和评估模型
- 能够根据需求调整模型架构

🚀 下一步：
1. 尝试修改模型参数（隐藏层大小、学习率等）
2. 使用真实数据集（如莎士比亚作品）
3. 实现更复杂的模型（如RNN）
4. 将模型部署为Web服务
"""

print("\n✨ makemore_annotated.py 加载完成！")
print("📖 使用 `python makemore_annotated.py` 运行演示")
print("🧪 使用 `python makemore_annotated.py --test` 运行测试")
print("=" * 60)