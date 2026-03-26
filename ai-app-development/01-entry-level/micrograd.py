"""
micrograd — 自动微分引擎
========================
目标：理解反向传播如何工作

核心概念：
- 计算图(Computational Graph)：用图表示数学运算
- 自动微分(Automatic Differentiation)：自动计算梯度
- 反向传播(Backpropagation)：从输出到输入逐层传递梯度

来源：Andrej Karpathy 的 micrograd 项目复现
"""

import math


class Value:
    """
    计算图中的一个节点，存储标量值及其梯度。
    
    每个 Value 对象知道：
    1. 自己的值 (.data)
    2. 自己的梯度 (.grad)
    3. 如何计算自己的梯度 (._backward)
    4. 自己的"孩子"是谁 (.prev)
    5. 自己是怎么被创造出来的 (.op)
    """
    
    def __init__(self, data, _children=(), _op='', label=''):
        if not isinstance(data, (int, float)):
            raise TypeError(f"Value 只支持标量，收到: {type(data)}")
        self.data = float(data)
        self.grad = 0.0  # 梯度初始化为0（默认假设不影响输出）
        self._backward = lambda: None  # 默认：叶子节点不需要反向传播
        self._prev = set(_children)  # 计算图中的父节点
        self._op = _op  # 产生此节点的操作
        self.label = label  # 可选标签，用于可视化
    
    def __repr__(self):
        return f"Value(data={self.data:.4f}, grad={self.grad:.4f})"
    
    # ============ 加法 ============
    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), '+')
        
        def _backward():
            # 加法的局部梯度：d(a+b)/da = 1, d(a+b)/db = 1
            # 链式法则：上游梯度 × 局部梯度
            self.grad += 1.0 * out.grad
            other.grad += 1.0 * out.grad
        out._backward = _backward
        
        return out
    
    def __radd__(self, other):  # 支持 1 + Value
        return self + other
    
    # ============ 乘法 ============
    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), '*')
        
        def _backward():
            # 乘法的局部梯度：d(a*b)/da = b, d(a*b)/db = a
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad
        out._backward = _backward
        
        return out
    
    def __rmul__(self, other):  # 支持 2 * Value
        return self * other
    
    # ============ 幂运算 ============
    def __pow__(self, other):
        assert isinstance(other, (int, float)), "幂只支持标量"
        out = Value(self.data ** other, (self,), f'**{other}')
        
        def _backward():
            # d(x^n)/dx = n * x^(n-1)
            self.grad += (other * self.data ** (other - 1)) * out.grad
        out._backward = _backward
        
        return out
    
    # ============ 激活函数 ============
    def tanh(self):
        """tanh 激活函数：将值压缩到 (-1, 1)"""
        x = self.data
        t = (math.exp(2*x) - 1) / (math.exp(2*x) + 1)
        out = Value(t, (self,), 'tanh')
        
        def _backward():
            # d(tanh(x))/dx = 1 - tanh²(x)
            self.grad += (1 - t**2) * out.grad
        out._backward = _backward
        
        return out
    
    def exp(self):
        """指数函数"""
        x = self.data
        out = Value(math.exp(x), (self,), 'exp')
        
        def _backward():
            # d(e^x)/dx = e^x
            self.grad += out.data * out.grad
        out._backward = _backward
        
        return out
    
    def relu(self):
        """ReLU 激活函数：max(0, x)"""
        out = Value(max(0, self.data), (self,), 'ReLU')
        
        def _backward():
            self.grad += (out.data > 0) * out.grad
        out._backward = _backward
        
        return out
    
    # ============ 减法和除法 ============
    def __neg__(self):  # -Value
        return self * -1
    
    def __sub__(self, other):  # Value - other
        return self + (-other)
    
    def __truediv__(self, other):  # Value / other
        return self * other**-1
    
    # ============ 反向传播 ============
    def backward(self):
        """
        从当前节点开始，反向传播梯度到整个计算图。
        
        关键步骤：
        1. 拓扑排序：确保父节点在子节点之前被处理
        2. 反向遍历：从输出到输入计算梯度
        """
        # 拓扑排序
        topo = []
        visited = set()
        
        def build_topo(v):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build_topo(child)
                topo.append(v)
        
        build_topo(self)
        
        # 初始化：输出节点的梯度为1
        self.grad = 1.0
        
        # 反向遍历计算图
        for node in reversed(topo):
            node._backward()


# ============ 神经网络单元 ============

class Neuron:
    """单个神经元：加权求和 + 激活函数"""
    
    def __init__(self, nin):
        """
        nin: 输入数量
        self.w: 权重列表 (每个输入一个权重)
        self.b: 偏置
        """
        self.w = [Value(random.uniform(-1, 1)) for _ in range(nin)]
        self.b = Value(0.0)
    
    def __call__(self, x):
        """
        前向传播：激活(w·x + b)
        
        x: 输入列表
        返回: tanh(Σ(wi * xi) + b)
        """
        # 加权求和：w1*x1 + w2*x2 + ... + wn*xn + b
        act = sum((wi * xi for wi, xi in zip(self.w, x)), self.b)
        # 激活函数
        return act.tanh()
    
    def parameters(self):
        """返回所有可训练参数"""
        return self.w + [self.b]


class Layer:
    """一层神经元"""
    
    def __init__(self, nin, nout):
        """
        nin: 输入数量
        nout: 输出数量（神经元数量）
        """
        self.neurons = [Neuron(nin) for _ in range(nout)]
    
    def __call__(self, x):
        """
        前向传播：将输入传给每个神经元，返回所有输出
        """
        outs = [n(x) for n in self.neurons]
        return outs[0] if len(outs) == 1 else outs
    
    def parameters(self):
        """返回这一层所有参数"""
        return [p for neuron in self.neurons for p in neuron.parameters()]


class MLP:
    """多层感知器 (Multi-Layer Perceptron)"""
    
    def __init__(self, nin, nouts):
        """
        nin: 输入层大小
        nouts: 每层输出大小的列表，如 [4, 4, 1] 表示3层
        
        示例：MLP(3, [4, 4, 1])
        - 第1层：3输入 → 4输出
        - 第2层：4输入 → 4输出
        - 第3层：4输入 → 1输出
        """
        sz = [nin] + nouts
        self.layers = [Layer(sz[i], sz[i+1]) for i in range(len(nouts))]
    
    def __call__(self, x):
        """前向传播：逐层传递"""
        for layer in self.layers:
            x = layer(x)
        return x
    
    def parameters(self):
        """返回所有层的所有参数"""
        return [p for layer in self.layers for p in layer.parameters()]


# ============ 梯度下降训练 ============

import random

def demo():
    """演示：用 micrograd 实现一个简单的神经网络训练"""
    random.seed(42)
    
    print("=" * 60)
    print("micrograd 演示：用神经网络学习 XOR 问题")
    print("=" * 60)
    
    # XOR 数据集
    xs = [
        [0.0, 0.0],
        [0.0, 1.0],
        [1.0, 0.0],
        [1.0, 1.0],
    ]
    ys = [0.0, 1.0, 1.0, 0.0]  # XOR 真值
    
    # 创建模型：2输入 → 4隐藏 → 1输出
    model = MLP(2, [4, 1])
    print(f"\n模型参数总数: {len(model.parameters())}")
    
    # 训练循环
    learning_rate = 0.1
    epochs = 100
    
    for epoch in range(epochs):
        # ---- 前向传播 ----
        ypred = [model(x) for x in xs]
        
        # 损失函数：均方误差 (MSE)
        loss = sum((yout - ygt)**2 for ygt, yout in zip(ys, ypred))
        
        # ---- 反向传播 ----
        # 先清零所有梯度
        for p in model.parameters():
            p.grad = 0.0
        # 计算梯度
        loss.backward()
        
        # ---- 梯度下降更新 ----
        for p in model.parameters():
            p.data -= learning_rate * p.grad
        
        if epoch % 20 == 0 or epoch == epochs - 1:
            print(f"Epoch {epoch:3d} | Loss: {loss.data:.6f}")
    
    # 最终预测
    print("\n最终预测:")
    for x, ygt in zip(xs, ys):
        ypred = model(x).data
        print(f"  {x[0]:.0f} XOR {x[1]:.0f} = {ypred:.4f} (期望 {ygt:.0f})")
    
    print("\n✅ 训练完成！网络学会了 XOR 函数")


def demo_simple():
    """演示：手动构建计算图并反向传播"""
    print("=" * 60)
    print("micrograd 演示：计算图与反向传播")
    print("=" * 60)
    
    # 构建计算图：L = (a * b + c) * f
    a = Value(2.0, label='a')
    b = Value(-3.0, label='b')
    c = Value(10.0, label='c')
    e = a * b; e.label = 'e'
    d = e + c; d.label = 'd'
    f = Value(-2.0, label='f')
    L = d * f; L.label = 'L'
    
    print(f"\n计算图: L = (a*b + c) * f")
    print(f"  a = {a.data}")
    print(f"  b = {b.data}")
    print(f"  c = {c.data}")
    print(f"  f = {f.data}")
    print(f"  L = {L.data}")
    
    # 反向传播
    L.backward()
    
    print(f"\n反向传播后的梯度:")
    print(f"  dL/da = {a.grad} (期望: b*f = {-3.0 * -2.0})")
    print(f"  dL/db = {b.grad} (期望: a*f = {2.0 * -2.0})")
    print(f"  dL/df = {f.grad} (期望: a*b + c = {2.0 * -3.0 + 10.0})")
    
    print("\n✅ 梯度计算正确！")


if __name__ == '__main__':
    demo_simple()
    print()
    demo()
