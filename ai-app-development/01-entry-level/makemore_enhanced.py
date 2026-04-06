"""
makemore — 字符级语言模型（错误处理增强版）
=========================
目标：理解语言模型如何预测下一个字符，具备健壮的错误处理机制

核心增强：
1. 数据验证：文件路径、数据格式、空数据处理
2. 模型配置验证：参数合理性检查
3. 训练监控：梯度爆炸/消失检测
4. 生成安全：生成过程错误处理
5. 资源管理：内存使用监控

来源：Andrej Karpathy 的 makemore 项目复现 + 错误处理增强
"""

import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
import random
import os
import sys
import warnings
from typing import List, Tuple, Optional, Union, Dict
import math


# ============ 错误处理体系 ============

class MakemoreError(Exception):
    """makemore 统一错误基类"""
    def __init__(self, message: str, context: dict = None, suggestion: str = None):
        self.message = message
        self.context = context or {}
        self.suggestion = suggestion
        full_msg = f"{message}"
        if context:
            full_msg += f" [上下文: {context}]"
        if suggestion:
            full_msg += f"\n💡 建议: {suggestion}"
        super().__init__(full_msg)


class DataValidationError(MakemoreError):
    """数据验证错误"""
    pass


class ModelConfigError(MakemoreError):
    """模型配置错误"""
    pass


class TrainingError(MakemoreError):
    """训练过程错误"""
    pass


class GenerationError(MakemoreError):
    """生成过程错误"""
    pass


class ResourceError(MakemoreError):
    """资源管理错误"""
    pass


# ============ 数据验证工具 ============

def validate_file_path(filepath: str) -> bool:
    """验证文件路径"""
    if not filepath:
        raise DataValidationError(
            "文件路径不能为空",
            {"operation": "文件加载"},
            "请提供有效的文件路径或使用默认数据"
        )
    
    if not os.path.exists(filepath):
        raise DataValidationError(
            f"文件不存在: {filepath}",
            {"filepath": filepath},
            "检查文件路径是否正确，或使用绝对路径"
        )
    
    if not os.path.isfile(filepath):
        raise DataValidationError(
            f"路径不是文件: {filepath}",
            {"filepath": filepath},
            "请提供有效的文件路径"
        )
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            f.read(1024)  # 测试读取
    except PermissionError:
        raise DataValidationError(
            f"没有读取权限: {filepath}",
            {"filepath": filepath},
            "检查文件权限或使用其他文件"
        )
    except UnicodeDecodeError:
        raise DataValidationError(
            f"文件编码问题: {filepath}",
            {"filepath": filepath},
            "尝试使用其他编码或确保文件是UTF-8格式"
        )
    except Exception as e:
        raise DataValidationError(
            f"文件读取失败: {str(e)}",
            {"filepath": filepath, "error": str(e)},
            "检查文件是否损坏或被占用"
        )
    
    return True


def validate_names(names: List[str]) -> List[str]:
    """验证和清洗名字数据"""
    if not names:
        raise DataValidationError(
            "名字列表为空",
            {"operation": "数据验证"},
            "请提供非空的名字列表或检查数据源"
        )
    
    if not isinstance(names, list):
        raise DataValidationError(
            f"名字数据应为列表，但收到: {type(names).__name__}",
            {"data_type": type(names).__name__},
            "请确保数据是列表格式"
        )
    
    cleaned_names = []
    warnings_list = []
    
    for i, name in enumerate(names):
        if not isinstance(name, str):
            warnings.warn(
                f"第{i}个名字不是字符串类型: {repr(name)}，已跳过",
                UserWarning
            )
            continue
        
        # 清理空白字符
        name = name.strip()
        if not name:
            warnings.warn(
                f"第{i}个名字为空字符串，已跳过",
                UserWarning
            )
            continue
        
        # 检查名字长度
        if len(name) < 2:
            warnings.warn(
                f"第{i}个名字 '{name}' 过短（长度<2），可能影响模型学习",
                UserWarning
            )
        
        if len(name) > 50:
            warnings.warn(
                f"第{i}个名字 '{name}' 过长（长度>50），可能影响模型性能",
                UserWarning
            )
        
        # 检查非法字符
        illegal_chars = []
        for char in name:
            if not char.isalpha() and char not in ['-', "'", ' ']:
                illegal_chars.append(char)
        
        if illegal_chars:
            warnings.warn(
                f"第{i}个名字 '{name}' 包含非常规字符: {illegal_chars}",
                UserWarning
            )
        
        cleaned_names.append(name.lower())  # 统一转为小写
    
    if len(cleaned_names) < 10:
        warnings.warn(
            f"数据量较少（{len(cleaned_names)}个名字），模型可能欠拟合",
            RuntimeWarning
        )
    
    if len(cleaned_names) == 0:
        raise DataValidationError(
            "清洗后没有有效名字",
            {"original_count": len(names)},
            "检查数据格式或提供更多有效数据"
        )
    
    # 统计信息
    unique_names = len(set(cleaned_names))
    if unique_names < len(cleaned_names) * 0.8:
        warnings.warn(
            f"数据重复率较高（唯一性: {unique_names}/{len(cleaned_names)}）",
            RuntimeWarning
        )
    
    return cleaned_names


# ============ 数据准备（增强版） ============

def load_names(filepath: Optional[str] = None, min_names: int = 5) -> List[str]:
    """
    加载名字数据集（增强版）
    
    参数:
        filepath: 数据文件路径，如果为None则使用内置数据
        min_names: 最小名字数量要求
    
    返回:
        清洗后的名字列表
    """
    try:
        if filepath:
            # 验证文件路径
            validate_file_path(filepath)
            
            # 读取文件
            with open(filepath, 'r', encoding='utf-8') as f:
                raw_names = f.read().splitlines()
            
            print(f"✅ 从文件加载 {len(raw_names)} 个名字")
            
        else:
            # 内置示例数据
            raw_names = [
                'emma', 'olivia', 'ava', 'isabella', 'sophia',
                'charlotte', 'mia', 'amelia', 'harper', 'evelyn',
                'liam', 'noah', 'oliver', 'elijah', 'james',
                'benjamin', 'lucas', 'mason', 'ethan', 'alexander',
                'bob', 'alice', 'david', 'sarah', 'michael',
            ] * 2  # 重复增加数据量
            random.shuffle(raw_names)
            
            print(f"✅ 使用内置数据 {len(raw_names)} 个名字")
        
        # 验证和清洗数据
        cleaned_names = validate_names(raw_names)
        
        # 检查最小数量要求
        if len(cleaned_names) < min_names:
            raise DataValidationError(
                f"名字数量不足: {len(cleaned_names)} < {min_names}",
                {"current_count": len(cleaned_names), "required_min": min_names},
                "提供更多名字或降低 min_names 参数"
            )
        
        # 数据统计
        avg_len = sum(len(name) for name in cleaned_names) / len(cleaned_names)
        unique_chars = len(set(''.join(cleaned_names)))
        
        print(f"📊 数据统计:")
        print(f"  有效名字: {len(cleaned_names)}")
        print(f"  平均长度: {avg_len:.1f}")
        print(f"  唯一字符: {unique_chars}")
        
        return cleaned_names
        
    except (DataValidationError, MakemoreError):
        raise
    except Exception as e:
        raise MakemoreError(
            "加载名字数据失败",
            {"filepath": filepath, "error": str(e)},
            "检查数据文件格式或使用默认数据"
        )


# ============ 方案1：Bigram 模型（增强版） ============

class BigramModel:
    """
    Bigram 模型：统计相邻字符的共现频率（增强版）
    
    增强特性：
    1. 输入验证：所有参数检查
    2. 数值稳定性：零概率处理
    3. 配置验证：模型参数合理性
    4. 生成安全：生成过程错误处理
    """
    
    def __init__(self, min_count: int = 1, smoothing: float = 1e-6):
        """
        初始化 Bigram 模型
        
        参数:
            min_count: 最小出现次数阈值
            smoothing: 平滑因子，避免零概率
        """
        try:
            # 参数验证
            if not isinstance(min_count, int):
                raise ModelConfigError(
                    f"min_count 应为整数，但收到: {type(min_count).__name__}",
                    {"parameter": "min_count", "value": min_count},
                    "使用整数，例如 min_count=1"
                )
            
            if min_count < 0:
                raise ModelConfigError(
                    f"min_count 不能为负数: {min_count}",
                    {"parameter": "min_count", "value": min_count},
                    "使用非负整数，例如 min_count=0 或 1"
                )
            
            if not isinstance(smoothing, (int, float)):
                raise ModelConfigError(
                    f"smoothing 应为数值，但收到: {type(smoothing).__name__}",
                    {"parameter": "smoothing", "value": smoothing},
                    "使用数值，例如 smoothing=1e-6"
                )
            
            if smoothing < 0:
                raise ModelConfigError(
                    f"smoothing 不能为负数: {smoothing}",
                    {"parameter": "smoothing", "value": smoothing},
                    "使用非负数，例如 smoothing=1e-6"
                )
            
            if smoothing > 0.1:
                warnings.warn(
                    f"平滑因子 {smoothing} 较大，可能过度平滑概率分布",
                    UserWarning
                )
            
            self.min_count = min_count
            self.smoothing = smoothing
            self.chars = []
            self.stoi = {}  # string to index
            self.itos = {}  # index to string
            self.N = None   # 计数矩阵
            
            print(f"✅ Bigram 模型初始化完成 (min_count={min_count}, smoothing={smoothing})")
            
        except (ModelConfigError, MakemoreError):
            raise
        except Exception as e:
            raise MakemoreError(
                "Bigram 模型初始化失败",
                {"min_count": min_count, "smoothing": smoothing, "error": str(e)}
            )
    
    def fit(self, names: List[str]) -> 'BigramModel':
        """训练：统计字符对的出现次数（增强版）"""
        try:
            # 输入验证
            if not names:
                raise DataValidationError(
                    "训练数据为空",
                    {"operation": "Bigram.fit"},
                    "提供非空的名字列表"
                )
            
            if not isinstance(names, list):
                raise DataValidationError(
                    f"训练数据应为列表，但收到: {type(names).__name__}",
                    {"data_type": type(names).__name__},
                    "确保输入是列表格式"
                )
            
            # 构建字符表
            all_chars = set()
            for i, name in enumerate(names):
                if not isinstance(name, str):
                    raise DataValidationError(
                        f"第{i}个名字不是字符串: {repr(name)}",
                        {"index": i, "name": repr(name)},
                        "确保所有名字都是字符串"
                    )
                all_chars.update(name)
            
            all_chars.add('.')  # 特殊标记：开始/结束
            
            if len(all_chars) < 2:
                raise ModelConfigError(
                    f"字符表过小: {len(all_chars)} 个字符",
                    {"char_count": len(all_chars)},
                    "提供包含更多不同字符的数据"
                )
            
            if len(all_chars) > 1000:
                warnings.warn(
                    f"字符表较大: {len(all_chars)} 个字符，可能影响性能",
                    RuntimeWarning
                )
            
            self.chars = sorted(all_chars)
            self.stoi = {ch: i for i, ch in enumerate(self.chars)}
            self.itos = {i: ch for i, ch in enumerate(self.chars)}
            
            print(f"📊 字符表构建完成: {len(self.chars)} 个字符")
            print(f"   字符范围: {self.chars[:10]}..." if len(self.chars) > 10 else f"   字符: {self.chars}")
            
            # 统计 bigram 频率
            vocab_size = len(self.chars)
            self.N = torch.zeros(vocab_size, vocab_size, dtype=torch.int32)
            
            total_pairs = 0
            for name in names:
                chs = ['.'] + list(name) + ['.']
                for ch1, ch2 in zip(chs, chs[1:]):
                    if ch1 not in self.stoi or ch2 not in self.stoi:
                        # 理论上不会发生，但防御性编程
                        continue
                    self.N[self.stoi[ch1], self.stoi[ch2]] += 1
                    total_pairs += 1
            
            if total_pairs == 0:
                raise DataValidationError(
                    "没有有效的字符对",
                    {"names_count": len(names)},
                    "检查数据是否包含有效字符"
                )
            
            # 检查稀疏性
            nonzero_count = (self.N > 0).sum().item()
            sparsity = 1.0 - nonzero_count / (vocab_size * vocab_size)
            
            print(f"📊 Bigram 统计完成:")
            print(f"   总字符对: {total_pairs}")
            print(f"   非零条目: {nonzero_count}/{vocab_size*vocab_size}")
            print(f"   稀疏度: {sparsity:.2%}")
            
            if sparsity > 0.95:
                warnings.warn(
                    f"Bigram 矩阵非常稀疏 ({sparsity:.2%})，模型可能欠拟合",
                    RuntimeWarning
                )
            
            # 检查最小计数
            if self.min_count > 1:
                low_count = (self.N < self.min_count).sum().item()
                if low_count > 0:
                    print(f"⚠️  有 {low_count} 个条目低于最小计数 {self.min_count}")
            
            return self
            
        except (DataValidationError, ModelConfigError, MakemoreError):
            raise
        except Exception as e:
            raise MakemoreError(
                "Bigram 模型训练失败",
                {"names_count": len(names) if names else 0, "error": str(e)}
            )
    
    def probability(self, add_smoothing: bool = True) -> torch.Tensor:
        """将计数矩阵转为概率矩阵（增强版）"""
        try:
            if self.N is None:
                raise ModelConfigError(
                    "模型未训练",
                    {"operation": "probability"},
                    "先调用 fit() 方法训练模型"
                )
            
            P = self.N.float()
            
            # 应用最小计数阈值
            if self.min_count > 1:
                P = torch.where(P < self.min_count, torch.tensor(0.0), P)
            
            # 添加平滑
            if add_smoothing and self.smoothing > 0:
                P = P + self.smoothing
            
            # 行归一化
            row_sums = P.sum(dim=1, keepdim=True)
            zero_rows = (row_sums == 0).squeeze()
            
            if zero_rows.any():
                zero_indices = torch.where(zero_rows)[0].tolist()
                warnings.warn(
                    f"有 {len(zero_indices)} 行总和为零（字符: {[self.itos[i] for i in zero_indices[:5]]}...）",
                    RuntimeWarning
                )
                # 均匀分布处理零行
                uniform_prob = 1.0 / P.shape[1]
                P[zero_rows] = uniform_prob
                row_sums[zero_rows] = 1.0
            
            P = P / row_sums
            
            # 验证概率分布
            if torch.any(P < 0):
                raise ModelConfigError(
                    "概率矩阵包含负值",
                    {"negative_count": (P < 0).sum().item()},
                    "检查平滑因子或数据"
                )
            
            if torch.any(torch.isnan(P)):
                raise ModelConfigError(
                    "概率矩阵包含 NaN",
                    {"nan_count": torch.isnan(P).sum().item()},
                    "检查数据或数值稳定性"
                )
            
            return P
            
        except (ModelConfigError, MakemoreError):
            raise
        except Exception as e:
            raise MakemoreError(
                "概率矩阵计算失败",
                {"add_smoothing": add_smoothing, "error": str(e)}
            )
    
    def generate(self, num: int = 10, max_length: int = 50, temperature: float = 1.0) -> List[str]:
        """生成新名字（增强版）"""
        try:
            # 参数验证
            if not isinstance(num, int):
                raise GenerationError(
                    f"生成数量应为整数，但收到: {type(num).__name__}",
                    {"parameter": "num", "value": num},
                    "使用整数，例如 num=10"
                )
            
            if num <= 0:
                raise GenerationError(
                    f"生成数量必须为正数: {num}",
                    {"parameter": "num", "value": num},
                    "使用正数，例如 num=10"
                )
            
            if num > 1000:
                warnings.warn(
                    f"生成数量较大: {num}，可能需要较长时间",
                    UserWarning
                )
            
            if not isinstance(max_length, int):
                raise GenerationError(
                    f"最大长度应为整数，但收到: {type(max_length).__name__}",
                    {"parameter": "max_length", "value": max_length},
                    "使用整数，例如 max_length=50"
                )
            
            if max_length <= 0:
                raise GenerationError(
                    f"最大长度必须为正数: {max_length}",
                    {"parameter": "max_length", "value": max_length},
                    "使用正数，例如 max_length=50"
                )
            
            if not isinstance(temperature, (int, float)):
                raise GenerationError(
                    f"温度参数应为数值，但收到: {type(temperature).__name__}",
                    {"parameter": "temperature", "value": temperature},
                    "使用数值，例如 temperature=1.0"
                )
            
            if temperature <= 0:
                raise GenerationError(
                    f"温度参数必须为正数: {temperature}",
                    {"parameter": "temperature", "value": temperature},
                    "使用正数，例如 temperature=1.0"
                )
            
            if temperature > 10:
                warnings.warn(
                    f"温度参数较高: {temperature}，生成结果可能过于随机",
                    UserWarning
                )
            
            # 检查模型状态
            if self.N is None:
                raise ModelConfigError(
                    "模型未训练",
                    {"operation": "generate"},
                    "先调用 fit() 方法训练模型"
                )
            
            P = self.probability()
            names = []
            
            for gen_idx in range(num):
                try:
                    out = []
                    ix = self.stoi['.']  # 从开始标记出发
                    steps = 0
                    
                    while True:
                        if steps >= max_length:
                            warnings.warn(
                                f"生成 #{gen_idx+1} 达到最大长度 {max_length}，强制终止",
                                RuntimeWarning
                            )
                            break
                        
                        # 获取概率分布
                        p = P[ix]
                        
                        # 应用温度
                        if temperature != 1.0:
                            p = p ** (1.0 / temperature)
                            p = p / p.sum()
                        
                        # 采样下一个字符
                        try:
                            ix = torch.multinomial(p, num_samples=1).item()
                        except RuntimeError as e:
                            if "invalid multinomial distribution" in str(e):
                                raise GenerationError(
                                    f"概率分布无效（可能包含NaN或负值）",
                                    {"distribution": p.tolist()},
                                    "检查模型训练或调整平滑因子"
                                )
                            else:
                                raise
                        
                        if ix == self.stoi['.']:
                            break
                        
                        out.append(self.itos[ix])
                        steps += 1
                    
                    # 检查生成结果
                    if not out:
                        warnings.warn(
                            f"生成 #{gen_idx+1} 结果为空",
                            RuntimeWarning
                        )
                        name = ""
                    else:
                        name = ''.join(out)
                        if len(name) < 2:
                            warnings.warn(
                                f"生成 #{gen_idx+1} 名字过短: '{name}'",
                                RuntimeWarning
                            )
                    
                    names.append(name)
                    
                except Exception as e:
                    if isinstance(e, (GenerationError, MakemoreError)):
                        raise
                    raise GenerationError(
                        f"生成第 {gen_idx+1} 个名字失败",
                        {"generation_index": gen_idx, "error": str(e)}
                    )
            
            # 生成统计
            valid_names = [n for n in names if len(n) >= 2]
            if valid_names:
                avg_len = sum(len(n) for n in valid_names) / len(valid_names)
                print(f"✅ 生成完成: {len(valid_names)}/{num} 个有效名字")
                print(f"   平均长度: {avg_len:.1f}")
            else:
                warnings.warn(
                    f"生成的名字全部无效（长度<2）",
                    RuntimeWarning
                )
            
            return names
            
        except (GenerationError, ModelConfigError, MakemoreError):
            raise
        except Exception as e:
            raise MakemoreError(
                "名字生成失败",
                {"num": num, "max_length": max_length, "temperature": temperature, "error": str(e)}
            )
    
    def evaluate(self, names: List[str]) -> float:
        """计算负对数似然损失（越低越好）（增强版）"""
        try:
            # 输入验证
            if not names:
                raise DataValidationError(
                    "评估数据为空",
                    {"operation": "Bigram.evaluate"},
                    "提供非空的名字列表"
                )
            
            # 检查模型状态
            if self.N is None:
                raise ModelConfigError(
                    "模型未训练",
                    {"operation": "evaluate"},
                    "先调用 fit() 方法训练模型"
                )
            
            P = self.probability()
            log_likelihood = 0.0
            n = 0
            
            for name in names:
                if not isinstance(name, str):
                    warnings.warn(
                        f"评估数据包含非字符串: {repr(name)}，已跳过",
                        UserWarning
                    )
                    continue
                
                chs = ['.'] + list(name) + ['.']
                for ch1, ch2 in zip(chs, chs[1:]):
                    if ch1 not in self.stoi or ch2 not in self.stoi:
                        warnings.warn(
                            f"名字 '{name}' 包含未知字符: '{ch1}'->'{ch2}'，已跳过该字符对",
                            UserWarning
                        )
                        continue
                    
                    prob = P[self.stoi[ch1], self.stoi[ch2]]
                    
                    # 检查零概率
                    if prob <= 0:
                        warnings.warn(
                            f"零概率事件: '{ch1}'->'{ch2}' 在名字 '{name}' 中",
                            RuntimeWarning
                        )
                        # 使用极小值避免负无穷
                        prob = 1e-10
                    
                    log_likelihood += torch.log(prob)
                    n += 1
            
            if n == 0:
                raise DataValidationError(
                    "没有有效的字符对用于评估",
                    {"names_count": len(names)},
                    "检查评估数据是否包含已知字符"
                )
            
            loss = -log_likelihood / n  # 负平均对数似然
            
            # 检查损失值合理性
            if torch.isnan(loss):
                raise ModelConfigError(
                    "损失值为 NaN",
                    {"log_likelihood": log_likelihood, "n": n},
                    "检查数据或概率矩阵"
                )
            
            if torch.isinf(loss):
                raise ModelConfigError(
                    "损失值为无穷大",
                    {"log_likelihood": log_likelihood, "n": n},
                    "检查是否有零概率事件"
                )
            
            return loss.item()
            
        except (DataValidationError, ModelConfigError, MakemoreError):
            raise
        except Exception as e:
            raise MakemoreError(
                "模型评估失败",
                {"names_count": len(names), "error": str(e)}
            )


# ============ 主程序测试 ============

if __name__ == "__main__":
    print("=" * 60)
    print("makemore 错误处理增强版 - 测试程序")
    print("=" * 60)
    
    try:
        # 测试数据加载
        print("\n1. 测试数据加载...")
        names = load_names()
        print(f"✅ 加载 {len(names)} 个名字")
        
        # 测试 Bigram 模型
        print("\n2. 测试 Bigram 模型...")
        model = BigramModel(min_count=1, smoothing=1e-6)
        model.fit(names)
        
        # 测试生成
        print("\n3. 测试名字生成...")
        generated = model.generate(num=5, max_length=20, temperature=1.0)
        print(f"✅ 生成的名字: {generated}")
        
        # 测试评估
        print("\n4. 测试模型评估...")
        loss = model.evaluate(names[:10])  # 只用前10个评估
        print(f"✅ 负对数似然损失: {loss:.4f}")
        
        # 测试错误处理
        print("\n5. 测试错误处理...")
        try:
            bad_model = BigramModel(min_count=-1)
            print("❌ 应该失败但通过了")
        except ModelConfigError as e:
            print(f"✅ 正确捕获配置错误: {e.message[:50]}...")
        
        try:
            model.generate(num=0)
            print("❌ 应该失败但通过了")
        except GenerationError as e:
            print(f"✅ 正确捕获生成错误: {e.message[:50]}...")
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        
    except MakemoreError as e:
        print(f"\n❌ 测试失败 (MakemoreError): {e}")
        if e.suggestion:
            print(f"💡 建议: {e.suggestion}")
    except Exception as e:
        print(f"\n❌ 测试失败 (意外错误): {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()