"""
nanoGPT 错误处理增强版 - 测试脚本
====================================
测试目标：
1. 验证错误处理功能正常工作
2. 确保向后兼容性
3. 测试数值稳定性
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import torch
import torch.nn as nn
import warnings
from nanogpt_enhanced import *


def test_config_validation():
    """测试配置验证"""
    print("=" * 60)
    print("测试配置验证")
    print("=" * 60)
    
    tests = []
    
    # 测试1: 正常配置
    try:
        config = GPTConfig(vocab_size=65, block_size=128, n_embd=384, n_head=6, n_layer=6, dropout=0.2)
        print("✅ 测试1: 正常配置 - 通过")
        tests.append(True)
    except Exception as e:
        print(f"❌ 测试1: 正常配置 - 失败: {e}")
        tests.append(False)
    
    # 测试2: 词汇表大小过小
    try:
        config = GPTConfig(vocab_size=0)
        print("❌ 测试2: 词汇表大小过小 - 应该失败但通过了")
        tests.append(False)
    except ConfigValidationError as e:
        print("✅ 测试2: 词汇表大小过小 - 正确捕获错误")
        tests.append(True)
    
    # 测试3: 上下文长度过大
    try:
        config = GPTConfig(block_size=5000)
        print("❌ 测试3: 上下文长度过大 - 应该失败但通过了")
        tests.append(False)
    except ConfigValidationError as e:
        print("✅ 测试3: 上下文长度过大 - 正确捕获错误")
        tests.append(True)
    
    # 测试4: Dropout 范围错误
    try:
        config = GPTConfig(dropout=1.5)
        print("❌ 测试4: Dropout 范围错误 - 应该失败但通过了")
        tests.append(False)
    except ConfigValidationError as e:
        print("✅ 测试4: Dropout 范围错误 - 正确捕获错误")
        tests.append(True)
    
    # 测试5: 参数类型错误
    try:
        config = GPTConfig(vocab_size="65")
        print("❌ 测试5: 参数类型错误 - 应该失败但通过了")
        tests.append(False)
    except ConfigValidationError as e:
        print("✅ 测试5: 参数类型错误 - 正确捕获错误")
        tests.append(True)
    
    passed = sum(tests)
    total = len(tests)
    print(f"\n📊 配置验证测试: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    return passed == total


def test_attention_head():
    """测试注意力头"""
    print("\n" + "=" * 60)
    print("测试注意力头")
    print("=" * 60)
    
    tests = []
    
    # 测试1: 正常前向传播
    try:
        head = Head(head_size=64, n_embd=384, block_size=128, dropout=0.1)
        test_input = torch.randn(2, 10, 384)
        output = head(test_input)
        
        if output.shape == (2, 10, 64):
            print("✅ 测试1: 正常前向传播 - 通过")
            tests.append(True)
        else:
            print(f"❌ 测试1: 输出形状错误: {output.shape} != (2, 10, 64)")
            tests.append(False)
    except Exception as e:
        print(f"❌ 测试1: 正常前向传播 - 失败: {e}")
        tests.append(False)
    
    # 测试2: 序列长度超过限制
    try:
        head = Head(head_size=64, n_embd=384, block_size=10, dropout=0.1)
        test_input = torch.randn(2, 20, 384)  # T=20 > block_size=10
        output = head(test_input)
        print("❌ 测试2: 序列长度超过限制 - 应该失败但通过了")
        tests.append(False)
    except InputValidationError as e:
        print("✅ 测试2: 序列长度超过限制 - 正确捕获错误")
        tests.append(True)
    except Exception as e:
        print(f"❌ 测试2: 序列长度超过限制 - 错误类型不匹配: {type(e).__name__}")
        tests.append(False)
    
    # 测试3: 输入形状错误
    try:
        head = Head(head_size=64, n_embd=384, block_size=128, dropout=0.1)
        test_input = torch.randn(2, 10)  # 缺少一个维度
        output = head(test_input)
        print("❌ 测试3: 输入形状错误 - 应该失败但通过了")
        tests.append(False)
    except InputValidationError as e:
        print("✅ 测试3: 输入形状错误 - 正确捕获错误")
        tests.append(True)
    except Exception as e:
        print(f"❌ 测试3: 输入形状错误 - 错误类型不匹配: {type(e).__name__}")
        tests.append(False)
    
    passed = sum(tests)
    total = len(tests)
    print(f"\n📊 注意力头测试: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    return passed == total


def test_multihead_attention():
    """测试多头注意力"""
    print("\n" + "=" * 60)
    print("测试多头注意力")
    print("=" * 60)
    
    tests = []
    
    # 测试1: 正常前向传播
    try:
        mha = MultiHeadAttention(num_heads=6, head_size=64, n_embd=384, dropout=0.1)
        test_input = torch.randn(2, 10, 384)
        output = mha(test_input)
        
        if output.shape == (2, 10, 384):
            print("✅ 测试1: 正常前向传播 - 通过")
            tests.append(True)
        else:
            print(f"❌ 测试1: 输出形状错误: {output.shape} != (2, 10, 384)")
            tests.append(False)
    except Exception as e:
        print(f"❌ 测试1: 正常前向传播 - 失败: {e}")
        tests.append(False)
    
    # 测试2: 头数配置错误
    try:
        mha = MultiHeadAttention(num_heads=0, head_size=64, n_embd=384, dropout=0.1)
        print("❌ 测试2: 头数配置错误 - 应该失败但通过了")
        tests.append(False)
    except ConfigValidationError as e:
        print("✅ 测试2: 头数配置错误 - 正确捕获错误")
        tests.append(True)
    except Exception as e:
        print(f"❌ 测试2: 头数配置错误 - 错误类型不匹配: {type(e).__name__}")
        tests.append(False)
    
    # 测试3: 嵌入维度为0
    try:
        mha = MultiHeadAttention(num_heads=6, head_size=64, n_embd=0, dropout=0.1)
        print("❌ 测试3: 嵌入维度为0 - 应该失败但通过了")
        tests.append(False)
    except ConfigValidationError as e:
        print("✅ 测试3: 嵌入维度为0 - 正确捕获错误")
        tests.append(True)
    except Exception as e:
        print(f"❌ 测试3: 嵌入维度为0 - 错误类型不匹配: {type(e).__name__}")
        tests.append(False)
    
    passed = sum(tests)
    total = len(tests)
    print(f"\n📊 多头注意力测试: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    return passed == total


def test_numerical_stability():
    """测试数值稳定性"""
    print("\n" + "=" * 60)
    print("测试数值稳定性")
    print("=" * 60)
    
    tests = []
    
    # 测试1: 极端缩放因子
    try:
        head = Head(head_size=64, n_embd=0, block_size=128, dropout=0.1)
        print("❌ 测试1: 极端缩放因子 - 应该失败但通过了")
        tests.append(False)
    except ConfigValidationError as e:
        print("✅ 测试1: 极端缩放因子 - 在初始化时被捕获")
        tests.append(True)
    except Exception as e:
        print(f"❌ 测试1: 极端缩放因子 - 错误类型不匹配: {type(e).__name__}")
        tests.append(False)
    
    # 测试2: 大数值输入
    try:
        head = Head(head_size=64, n_embd=384, block_size=128, dropout=0.1)
        # 创建包含极大值的输入
        test_input = torch.randn(2, 10, 384) * 1e10
        output = head(test_input)
        
        # 检查输出是否包含 NaN 或 Inf
        if torch.isnan(output).any() or torch.isinf(output).any():
            print("❌ 测试2: 大数值输入 - 输出包含 NaN/Inf")
            tests.append(False)
        else:
            print("✅ 测试2: 大数值输入 - 处理正常")
            tests.append(True)
    except Exception as e:
        print(f"❌ 测试2: 大数值输入 - 失败: {e}")
        tests.append(False)
    
    # 测试3: 非常小的输入
    try:
        head = Head(head_size=64, n_embd=384, block_size=128, dropout=0.1)
        test_input = torch.randn(2, 10, 384) * 1e-10
        output = head(test_input)
        
        if torch.isnan(output).any() or torch.isinf(output).any():
            print("❌ 测试3: 非常小的输入 - 输出包含 NaN/Inf")
            tests.append(False)
        else:
            print("✅ 测试3: 非常小的输入 - 处理正常")
            tests.append(True)
    except Exception as e:
        print(f"❌ 测试3: 非常小的输入 - 失败: {e}")
        tests.append(False)
    
    passed = sum(tests)
    total = len(tests)
    print(f"\n📊 数值稳定性测试: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    return passed == total


def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n" + "=" * 60)
    print("测试向后兼容性")
    print("=" * 60)
    
    tests = []
    
    # 测试1: 接口一致性
    try:
        # 测试所有类是否都能正常实例化
        config = GPTConfig()
        head = Head(64, 384, 128, 0.1)
        mha = MultiHeadAttention(6, 64, 384, 0.1)
        
        print("✅ 测试1: 接口一致性 - 通过")
        tests.append(True)
    except Exception as e:
        print(f"❌ 测试1: 接口一致性 - 失败: {e}")
        tests.append(False)
    
    # 测试2: 功能一致性
    try:
        head = Head(64, 384, 128, 0.1)
        test_input = torch.randn(2, 10, 384)
        output = head(test_input)
        
        # 检查输出是否符合预期
        if output.shape == (2, 10, 64):
            print("✅ 测试2: 功能一致性 - 通过")
            tests.append(True)
        else:
            print(f"❌ 测试2: 功能一致性 - 输出形状错误: {output.shape}")
            tests.append(False)
    except Exception as e:
        print(f"❌ 测试2: 功能一致性 - 失败: {e}")
        tests.append(False)
    
    passed = sum(tests)
    total = len(tests)
    print(f"\n📊 向后兼容性测试: {passed}/{total} 通过 ({passed/total*100:.1f}%)")
    
    return passed == total


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始运行所有测试")
    print("=" * 60)
    
    all_tests = [
        ("配置验证", test_config_validation),
        ("注意力头", test_attention_head),
        ("多头注意力", test_multihead_attention),
        ("数值稳定性", test_numerical_stability),
        ("向后兼容性", test_backward_compatibility),
    ]
    
    results = []
    for name, test_func in all_tests:
        try:
            passed = test_func()
            results.append((name, passed, "✅ 通过" if passed else "❌ 失败"))
        except Exception as e:
            results.append((name, False, f"❌ 异常: {e}"))
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed_count = 0
    for name, passed, status in results:
        print(f"{name:15} | {status}")
        if passed:
            passed_count += 1
    
    total_tests = len(results)
    success_rate = passed_count / total_tests * 100
    
    print(f"\n📊 总体结果: {passed_count}/{total_tests} 通过 ({success_rate:.1f}%)")
    
    if passed_count == total_tests:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  {total_tests - passed_count} 项测试失败")
    
    return passed_count == total_tests


if __name__ == "__main__":
    try:
        # 过滤警告
        warnings.filterwarnings('ignore', category=RuntimeWarning)
        warnings.filterwarnings('ignore', category=ResourceWarning)
        warnings.filterwarnings('ignore', category=UserWarning)
        
        success = run_all_tests()
        
        if success:
            print("\n" + "=" * 60)
            print("✅ nanoGPT 错误处理增强测试完成")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("❌ nanoGPT 错误处理增强测试失败")
            print("=" * 60)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试执行异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)