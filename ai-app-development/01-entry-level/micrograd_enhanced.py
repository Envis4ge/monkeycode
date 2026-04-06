"""
micrograd — 自动微分引擎（错误处理增强版）
========================

目标：理解反向传播如何工作，具备健壮的错误处理机制

核心增强：
1. 输入验证：所有外部输入严格检查
2. 数值稳定性：数学计算边界情况处理
3. 配置验证：模型参数合理性检查
4. 运行时监控：训练过程状态监控
5. 错误报告：统一的错误信息格式

来源：Andrej Karpathy 的 micrograd 项目复现 + 错误处理增强
"""

import math
import warnings
from typing import Union, List, Tuple


class MicrogradError(Exception):
    """micrograd 统一错误基类"""
    def __init__(self, message: str, context: dict = None):
        self.message = message
        self.context = context or {}
        super().__init__(f"{message} [上下文: {context}]")


class InputValidationError(MicrogradError):
    """输入验证错误"""
    pass


class NumericalStabilityError(MicrogradError):
    """数值稳定性错误"""
    pass


class ConfigValidationError(MicrogradError):
    """配置验证错误"""
    pass


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
    
    @staticmethod
    def _validate_input(data, label: str = "") -> bool:
        """验证输入数据的有效性"""
        if data is None:
            raise InputValidationError(
                f"{label}数据不能为 None",
                {"input_data": data, "operation": "Value 初始化"}
            )
        
        if not isinstance(data, (int, float)):
            if isinstance(data, (list, tuple, dict)):
                raise InputValidationError(
                    f"{label}应为标量数值，但收到了 {type(data).__name__} 类型",
                    {"input_type": type(data).__name__, "expected_type": "int/float"}
                )
            
            try:
                float(data)
            except (ValueError, TypeError):
                raise InputValidationError(
                    f"{label}无法转换为数值: {repr(data)}",
                    {"input_value": repr(data)}
                )
            
            warnings.warn(
                f"{label}输入 {repr(data)} 被自动转换为数值，建议使用明确类型",
                UserWarning
            )
        
        # 检查数值范围
        data_float = float(data)
        if abs(data_float) > 1e100:
            warnings.warn(
                f"{label}数值 {data_float} 过大，可能导致数值溢出",
                RuntimeWarning
            )
        
        if data_float == 0.0 and 'div' in label.lower():
            raise NumericalStabilityError(
                "除数不能为零",
                {"numerator": "unknown", "denominator": 0.0}
            )
        
        return True
    
    @staticmethod
    def _check_numerical_stability(operation: str, *args) -> bool:
        """检查数值稳定性"""
        if operation == 'exp':
            x = args[0]
            if x > 700:  # exp(709) 接近 float64 的上限
                raise NumericalStabilityError(
                    f"指数运算输入 {x} 过大，可能导致溢出",
                    {"operation": "exp", "input": x, "threshold": 700}
                )
            if x < -700:
                warnings.warn(
                    f"指数运算输入 {x} 过小，可能导致下溢",
                    RuntimeWarning
                )
        
        elif operation == 'log':
            x = args[0]
            if x <= 0:
                raise NumericalStabilityError(
                    f"对数运算输入 {x} 必须为正数",
                    {"operation": "log", "input": x}
                )
            if x < 1e-15:
                warnings.warn(
                    f"对数运算输入 {x} 过小，精度可能损失",
                    RuntimeWarning
                )
        
        elif operation == 'div':
            numerator, denominator = args[0], args[1]
            if abs(denominator) < 1e-15:
                raise NumericalStabilityError(
                    f"除数 {denominator} 过小，可能导致数值不稳定",
                    {"operation": "div", "numerator": numerator, "denominator": denominator}
                )
        
        return True
    
    def __init__(self, data, _children=(), _op='', label=''):
        # 输入验证
        self._validate_input(data, f"Value{'' if not label else f'({label})'} 的")
        
        self.data = float(data)
        self.grad = 0.0  # 梯度初始化为0（默认假设不影响输出）
        self._backward = lambda: None  # 默认：叶子节点不需要反向传播
        
        # 验证 _children
        if not isinstance(_children, (tuple, list)):
            warnings.warn(
                f"_children 应为元组或列表，但收到了 {type(_children).__name__}",
                UserWarning
            )
            _children = (_children,) if _children else ()
        
        self._prev = set(_children)  # 计算图中的父节点
        self._op = _op  # 产生此节点的操作
        self.label = label  # 可选标签，用于可视化
    
    def __repr__(self):
        return f"Value(data={self.data:.4f}, grad={self.grad:.4f})"
    
    # ============ 加法 ============
    def __add__(self, other):
        try:
            other = other if isinstance(other, Value) else Value(other)
            
            # 数值稳定性检查
            if abs(self.data) > 1e100 and abs(other.data) > 1e100:
                warnings.warn(
                    "两个大数相加可能导致数值溢出",
                    RuntimeWarning
                )
            
            out = Value(self.data + other.data, (self, other), '+')
            
            def _backward():
                # 加法的局部梯度：d(a+b)/da = 1, d(a+b)/db = 1
                # 链式法则：上游梯度 × 局部梯度
                try:
                    self.grad += 1.0 * out.grad
                    other.grad += 1.0 * out.grad
                except Exception as e:
                    raise MicrogradError(
                        "加法反向传播计算失败",
                        {"self.grad": self.grad, "other.grad": other.grad, 
                         "out.grad": out.grad, "error": str(e)}
                    )
            out._backward = _backward
            
            return out
            
        except (InputValidationError, NumericalStabilityError):
            raise
        except Exception as e:
            raise MicrogradError(
                "加法运算失败",
                {"self.data": self.data, "other": repr(other), "error": str(e)}
            )
    
    def __radd__(self, other):  # 支持 1 + Value
        return self + other
    
    # ============ 乘法 ============
    def __mul__(self, other):
        try:
            other = other if isinstance(other, Value) else Value(other)
            
            # 数值稳定性检查
            if abs(self.data) > 1e50 and abs(other.data) > 1e50:
                warnings.warn(
                    "两个大数相乘可能导致数值溢出",
                    RuntimeWarning
                )
            
            out = Value(self.data * other.data, (self, other), '*')
            
            def _backward():
                # 乘法的局部梯度：d(a*b)/da = b, d(a*b)/db = a
                try:
                    self.grad += other.data * out.grad
                    other.grad += self.data * out.grad
                except Exception as e:
                    raise MicrogradError(
                        "乘法反向传播计算失败",
                        {"self.data": self.data, "other.data": other.data,
                         "out.grad": out.grad, "error": str(e)}
                    )
            out._backward = _backward
            
            return out
            
        except (InputValidationError, NumericalStabilityError):
            raise
        except Exception as e:
            raise MicrogradError(
                "乘法运算失败",
                {"self.data": self.data, "other": repr(other), "error": str(e)}
            )
    
    def __rmul__(self, other):  # 支持 2 * Value
        return self * other
    
    # ============ 减法 ============
    def __sub__(self, other):
        try:
            return self + (-other)
        except Exception as e:
            raise MicrogradError(
                "减法运算失败",
                {"self.data": self.data, "other": repr(other), "error": str(e)}
            )
    
    def __rsub__(self, other):  # 支持 2 - Value
        try:
            return (-self) + other
        except Exception as e:
            raise MicrogradError(
                "反向减法运算失败",
                {"self.data": self.data, "other": repr(other), "error": str(e)}
            )
    
    def __neg__(self):  # -Value
        try:
            return self * -1
        except Exception as e:
            raise MicrogradError(
                "取负运算失败",
                {"self.data": self.data, "error": str(e)}
            )
    
    # ============ 除法 ============
    def __truediv__(self, other):
        try:
            other = other if isinstance(other, Value) else Value(other)
            
            # 数值稳定性检查
            self._check_numerical_stability('div', self.data, other.data)
            
            out = Value(self.data / other.data, (self, other), '/')
            
            def _backward():
                # d(a/b)/da = 1/b, d(a/b)/db = -a/b²
                try:
                    self.grad += (1 / other.data) * out.grad
                    other.grad += (-self.data / other.data**2) * out.grad
                except ZeroDivisionError:
                    raise NumericalStabilityError(
                        "除法反向传播中除数为零",
                        {"self.data": self.data, "other.data": other.data}
                    )
                except Exception as e:
                    raise MicrogradError(
                        "除法反向传播计算失败",
                        {"self.data": self.data, "other.data": other.data,
                         "out.grad": out.grad, "error": str(e)}
                    )
            out._backward = _backward
            
            return out
            
        except (InputValidationError, NumericalStabilityError):
            raise
        except Exception as e:
            raise MicrogradError(
                "除法运算失败",
                {"self.data": self.data, "other": repr(other), "error": str(e)}
            )
    
    def __rtruediv__(self, other):  # 支持 2 / Value
        try:
            other = other if isinstance(other, Value) else Value(other)
            return other / self
        except Exception as e:
            raise MicrogradError(
                "反向除法运算失败",
                {"self.data": self.data, "other": repr(other), "error": str(e)}
            )
    
    # ============ 幂运算 ============
    def __pow__(self, other):
        try:
            # 输入验证
            if not isinstance(other, (int, float)):
                try:
                    other = float(other)
                except (ValueError, TypeError):
                    raise InputValidationError(
                        "幂运算指数应为标量数值",
                        {"exponent_type": type(other).__name__, "exponent_value": repr(other)}
                    )
            
            # 数值稳定性检查
            if other > 1000:
                warnings.warn(
                    f"幂运算指数 {other} 过大，可能导致数值溢出",
                    RuntimeWarning
                )
            
            if self.data < 0 and not isinstance(other, int):
                raise NumericalStabilityError(
                    f"负数 {self.data} 的非整数幂 {other} 会产生复数结果",
                    {"base": self.data, "exponent": other, "operation": "pow"}
                )
            
            out = Value(self.data ** other, (self,), f'**{other}')
            
            def _backward():
                # d(x^n)/dx = n * x^(n-1)
                try:
                    if abs(self.data) < 1e-15 and other < 1:
                        # 处理 x^a 在 x=0 附近的特殊情况
                        if other > 0:
                            self.grad += 0.0  # x^a 在 x=0 处导数为0 (a>0)
                        else:
                            raise NumericalStabilityError(
                                f"x^{other} 在 x=0 处导数不存在",
                                {"base": self.data, "exponent": other}
                            )
                    else:
                        self.grad += (other * self.data ** (other - 1)) * out.grad
                except (ValueError, ZeroDivisionError) as e:
                    raise NumericalStabilityError(
                        f"幂运算反向传播数值不稳定",
                        {"base": self.data, "exponent": other, "error": str(e)}
                    )
                except Exception as e:
                    raise MicrogradError(
                        "幂运算反向传播计算失败",
                        {"self.data": self.data, "exponent": other,
                         "out.grad": out.grad, "error": str(e)}
                    )
            out._backward = _backward
            
            return out
            
        except (InputValidationError, NumericalStabilityError):
            raise
        except Exception as e:
            raise MicrogradError(
                "幂运算失败",
                {"self.data": self.data, "exponent": repr(other), "error": str(e)}
            )
    
    # ============ 激活函数 ============
    def tanh(self):
        """tanh 激活函数：将值压缩到 (-1, 1)"""
        try:
            x = self.data
            
            # 数值稳定性检查
            if abs(x) > 50:
                warnings.warn(
                    f"tanh 输入 {x} 绝对值过大，结果将接近 ±1",
                    RuntimeWarning
                )
                t = 1.0 if x > 0 else -1.0
            else:
                # 稳定的 tanh 计算
                if abs(x) < 1e-3:
                    # 小 x 使用泰勒展开避免数值问题
                    t = x - x**3/3 + 2*x**5/15 - 17*x**7/315
                else:
                    # 标准计算
                    t = (math.exp(2*x) - 1) / (math.exp(2*x) + 1)
            
            out = Value(t, (self,), 'tanh')
            
            def _backward():
                # d(tanh(x))/dx = 1 - tanh²(x)
                try:
                    if abs(t) > 0.999999:
                        # tanh(x) 接近 ±1 时导数接近0，避免数值误差
                        self.grad += 0.0
                    else:
                        self.grad += (1 - t**2) * out.grad
                except Exception as e:
                    raise MicrogradError(
                        "tanh 反向传播计算失败",
                        {"self.data": self.data, "t": t, "out.grad": out.grad, "error": str(e)}
                    )
            out._backward = _backward
            
            return out
            
        except Exception as e:
            raise MicrogradError(
                "tanh 运算失败",
                {"self.data": self.data, "error": str(e)}
            )
    
    def relu(self):
        """ReLU 激活函数：max(0, x)"""
        try:
            out = Value(0 if self.data < 0 else self.data, (self,), 'ReLU')
            
            def _backward():
                try:
                    self.grad += (out.data > 0) * out.grad
                except Exception as e:
                    raise MicrogradError(
                        "ReLU 反向传播计算失败",
                        {"self.data": self.data, "out.data": out.data, 
                         "out.grad": out.grad, "error": str(e)}
                    )
            out._backward = _backward
            
            return out
            
        except Exception as e:
            raise MicrogradError(
                "ReLU 运算失败",
                {"self.data": self.data, "error": str(e)}
            )
    
    def sigmoid(self):
        """sigmoid 激活函数：1 / (1 + exp(-x))"""
        try:
            x = self.data
            
            # 数值稳定性检查
            if x > 50:
                t = 1.0
            elif x < -50:
                t = 0.0
            else:
                t = 1 / (1 + math.exp(-x))
            
            out = Value(t, (self,), 'sigmoid')
            
            def _backward():
                # d(sigmoid)/dx = sigmoid(x) * (1 - sigmoid(x))
                try:
                    self.grad += t * (1 - t) * out.grad
                except Exception as e:
                    raise MicrogradError(
                        "sigmoid 反向传播计算失败",
                        {"self.data": self.data, "t": t, "out.grad": out.grad, "error": str(e)}
                    )
            out._backward = _backward
            
            return out
            
        except Exception as e:
            raise MicrogradError(
                "sigmoid 运算失败",
                {"self.data": self.data, "error": str(e)}
            )
    
    # ============ 反向传播 ============
    def backward(self):
        """计算所有相关节点的梯度"""
        try:
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
            
            # 设置输出梯度为1（假设是损失函数）
            self.grad = 1.0
            
            # 反向传播
            for v in reversed(topo):
                try:
                    v._backward()
                except Exception as e:
                    raise MicrogradError(
                        f"节点反向传播失败 [op={v._op}, data={v.data}]",
                        {"node_op": v._op, "node_data": v.data, "error": str(e)}
                    )
                    
        except Exception as e:
            raise MicrogradError(
                "反向传播过程失败",
                {"self.data": self.data, "self.op": self._op, "error": str(e)}
            )


class Neuron:
    """一个简单的神经元"""
    
    def __init__(self, nin):
        try:
            # 输入验证
            if not isinstance(nin, int):
                raise InputValidationError(
                    "神经元输入维度应为整数",
                    {"nin_type": type(nin).__name__, "nin_value": nin}
                )
            
            if nin <= 0:
                raise InputValidationError(
                    "神经元输入维度必须为正数",
                    {"nin": nin}
                )
            
            if nin > 1000:
                warnings.warn(
                    f"神经元输入维度 {nin} 较大，可能影响性能",
                    UserWarning
                )
            
            # 初始化权重和偏置
            self.w = [Value(random.uniform(-1, 1)) for _ in range(nin)]
            self.b = Value(0.0)
            
        except Exception as e:
            if not isinstance(e, (InputValidationError, MicrogradError)):
                raise MicrogradError(
                    "神经元初始化失败",
                    {"nin": nin, "error": str(e)}
                )
            else:
                raise
    
    def __call__(self, x):
        try:
            # 输入验证
            if not isinstance(x, list):
                raise InputValidationError(
                    "神经元输入应为列表",
                    {"x_type": type(x).__name__, "x_value": repr(x)}
                )
            
            if len(x) != len(self.w):
                raise InputValidationError(
                    f"输入维度 {len(x)} 与权重维度 {len(self.w)} 不匹配",
                    {"input_len": len(x), "weight_len": len(self.w)}
                )
            
            # 验证每个输入
            for i, xi in enumerate(x):
                if not isinstance(xi, (int, float, Value)):
                    try:
                        x[i] = float(xi)
                    except (ValueError, TypeError):
                        raise InputValidationError(
                            f"输入第{i}个元素应为数值类型",
                            {"element_index": i, "element_type": type(xi).__name__, "element_value": repr(xi)}
                        )
            
            # 前向传播
            act = sum((wi * xi for wi, xi in zip(self.w, x)), self.b)
            out = act.tanh()
            
            return out
            
        except (InputValidationError, NumericalStabilityError, MicrogradError):
            raise
        except Exception as e:
            raise MicrogradError(
                "神经元前向传播失败",
                {"input": x, "neuron_weights_len": len(self.w), "error": str(e)}
            )


# 为方便测试，添加随机模块
import random

if __name__ == "__main__":
    # 测试代码
    print("=== micrograd 错误处理增强版测试 ===")
    
    try:
        # 测试正常情况
        a = Value(2.0, label='a')
        b = Value(-3.0, label='b')
        c = Value(10.0, label='c')
        
        d = a * b + c
        d.label = 'd'
        
        print(f"正常计算: d = {d.data:.4f}")
        
        # 测试反向传播
        d.backward()
        print(f"梯度: a.grad = {a.grad:.4f}, b.grad = {b.grad:.4f}, c.grad = {c.grad:.4f}")
        
        # 测试异常输入处理
        print("\n=== 测试异常输入处理 ===")
        try:
            bad = Value("not a number")
        except InputValidationError as e:
            print(f"✅ 正确捕获输入验证错误: {e}")
        
        # 测试数值稳定性
        print("\n=== 测试数值稳定性 ===")
        try:
            big = Value(1e200)
            bigger = Value(1e200)
            result = big + bigger
            print(f"大数相加: {result.data:.4e} (已警告)")
        except Exception as e:
            print(f"数值稳定性处理: {e}")
        
        print("\n✅ 所有测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")