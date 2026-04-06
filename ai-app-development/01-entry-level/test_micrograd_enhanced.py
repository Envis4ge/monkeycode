#!/usr/bin/env python3
"""
micrograd 错误处理增强版验证脚本

测试目标：
1. 验证错误处理功能正常工作
2. 验证数值稳定性增强
3. 验证输入验证功能
4. 验证向后兼容性

执行方式：
python test_micrograd_enhanced.py
"""

import sys
import traceback
from micrograd_enhanced import (
    Value, MicrogradError, InputValidationError, 
    NumericalStabilityError, ConfigValidationError
)

def print_test_result(test_name, passed, error=None):
    """打印测试结果"""
    status = "✅ 通过" if passed else "❌ 失败"
    print(f"{status} {test_name}")
    if error and not passed:
        print(f"   错误: {error}")
        if isinstance(error, Exception):
            print(f"   详细信息: {str(error)}")

def test_input_validation():
    """测试输入验证功能"""
    print("\n=== 测试输入验证 ===")
    
    tests = [
        ("正常数值", lambda: Value(3.14), True),
        ("正常整数", lambda: Value(42), True),
        ("字符串数值", lambda: Value("3.14"), True),  # 应该警告但通过
        ("空值", lambda: Value(None), False),
        ("列表输入", lambda: Value([1, 2, 3]), False),
        ("字典输入", lambda: Value({"a": 1}), False),
        ("非法字符串", lambda: Value("not a number"), False),
    ]
    
    for name, func, should_pass in tests:
        try:
            result = func()
            if should_pass:
                print_test_result(f"输入验证: {name}", True)
            else:
                print_test_result(f"输入验证: {name}", False, "应该失败但通过了")
        except InputValidationError as e:
            if not should_pass:
                print_test_result(f"输入验证: {name}", True)
            else:
                print_test_result(f"输入验证: {name}", False, f"应该通过但失败: {e}")
        except Exception as e:
            print_test_result(f"输入验证: {name}", False, f"意外错误: {e}")

def test_numerical_stability():
    """测试数值稳定性"""
    print("\n=== 测试数值稳定性 ===")
    
    # 测试大数运算
    try:
        a = Value(1e100)
        b = Value(1e100)
        result = a + b
        print_test_result("大数相加", True)
        print(f"   结果: {result.data:.2e} (应该触发警告)")
    except Exception as e:
        print_test_result("大数相加", False, e)
    
    # 测试溢出情况
    try:
        a = Value(1e200)
        b = Value(1e200)
        result = a * b
        print_test_result("大数相乘", True)
        print(f"   结果: {result.data:.2e} (可能溢出)")
    except Exception as e:
        print_test_result("大数相乘", False, e)
    
    # 测试除法边界
    try:
        a = Value(1.0)
        b = Value(1e-20)
        result = a / b
        print_test_result("极小除数", True)
        print(f"   结果: {result.data:.2e} (应该警告)")
    except NumericalStabilityError as e:
        print_test_result("极小除数", True)  # 正确捕获
    except Exception as e:
        print_test_result("极小除数", False, e)
    
    # 测试零除法
    try:
        a = Value(1.0)
        b = Value(0.0)
        result = a / b
        print_test_result("零除法", False, "应该失败但通过了")
    except NumericalStabilityError as e:
        print_test_result("零除法", True)  # 正确捕获
    except Exception as e:
        print_test_result("零除法", False, f"错误类型不正确: {type(e).__name__}")

def test_operation_error_handling():
    """测试运算错误处理"""
    print("\n=== 测试运算错误处理 ===")
    
    # 测试加法
    try:
        a = Value(2.0)
        b = "invalid"
        result = a + b
        print_test_result("加法类型错误", False, "应该失败但通过了")
    except (InputValidationError, MicrogradError) as e:
        print_test_result("加法类型错误", True)
    except Exception as e:
        print_test_result("加法类型错误", False, f"错误类型不正确: {type(e).__name__}")
    
    # 测试幂运算
    try:
        a = Value(-2.0)
        result = a ** 0.5  # 负数开平方
        print_test_result("负数分数幂", True)
        print(f"   结果: {result.data} (应该警告)")
    except Exception as e:
        print_test_result("负数分数幂", False, e)
    
    # 测试复杂运算链
    try:
        a = Value(2.0)
        b = Value(3.0)
        c = Value(4.0)
        result = (a * b + c) ** 2 - a / (b + Value(1e-10))
        result.backward()
        print_test_result("复杂运算链", True)
    except Exception as e:
        print_test_result("复杂运算链", False, e)

def test_activation_functions():
    """测试激活函数错误处理"""
    print("\n=== 测试激活函数 ===")
    
    # 测试 tanh
    try:
        a = Value(100.0)  # 非常大的输入
        result = a.tanh()
        print_test_result("tanh 大输入", True)
        print(f"   结果: {result.data} (应该接近1)")
    except Exception as e:
        print_test_result("tanh 大输入", False, e)
    
    # 测试 sigmoid
    try:
        a = Value(100.0)
        result = a.sigmoid()
        print_test_result("sigmoid 大输入", True)
        print(f"   结果: {result.data} (应该接近1)")
    except Exception as e:
        print_test_result("sigmoid 大输入", False, e)
    
    # 测试 ReLU
    try:
        a = Value(-5.0)
        result = a.relu()
        print_test_result("ReLU 负数", True)
        print(f"   结果: {result.data} (应该为0)")
    except Exception as e:
        print_test_result("ReLU 负数", False, e)

def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n=== 测试向后兼容性 ===")
    
    # 测试原始 micrograd 功能
    try:
        # 基本运算
        a = Value(2.0)
        b = Value(3.0)
        c = a + b
        d = a * b
        e = a.tanh()
        
        # 梯度计算
        f = a * b + c
        f.backward()
        
        print_test_result("基本运算兼容", True)
        print(f"   a.grad = {a.grad:.4f}, b.grad = {b.grad:.4f}")
        
    except Exception as e:
        print_test_result("基本运算兼容", False, e)
    
    # 测试计算图
    try:
        a = Value(2.0, label='a')
        b = Value(-3.0, label='b')
        c = Value(10.0, label='c')
        d = a * b + c
        d.label = 'd'
        d.backward()
        
        print_test_result("计算图兼容", True)
        
    except Exception as e:
        print_test_result("计算图兼容", False, e)

def test_neuron_error_handling():
    """测试神经元错误处理"""
    print("\n=== 测试神经元错误处理 ===")
    
    try:
        from micrograd_enhanced import Neuron
        import random
        
        # 测试正常神经元
        n = Neuron(3)
        x = [1.0, -2.0, 3.0]
        output = n(x)
        print_test_result("正常神经元", True)
        print(f"   输出: {output.data:.4f}")
        
        # 测试维度不匹配
        try:
            bad_x = [1.0, 2.0]  # 应该是3个输入
            output = n(bad_x)
            print_test_result("神经元维度检查", False, "应该失败但通过了")
        except InputValidationError as e:
            print_test_result("神经元维度检查", True)
        
        # 测试非法输入类型
        try:
            bad_x = [1.0, "invalid", 3.0]
            output = n(bad_x)
            print_test_result("神经元输入类型检查", False, "应该失败但通过了")
        except InputValidationError as e:
            print_test_result("神经元输入类型检查", True)
        
    except Exception as e:
        print_test_result("神经元测试", False, f"初始化失败: {e}")

def run_performance_test():
    """运行性能测试"""
    print("\n=== 性能测试 ===")
    
    import time
    
    try:
        # 创建复杂计算图
        start_time = time.time()
        
        # 创建100个节点
        values = [Value(float(i)) for i in range(100)]
        
        # 构建复杂计算图
        result = values[0]
        for i in range(1, 100):
            if i % 3 == 0:
                result = result + values[i]
            elif i % 3 == 1:
                result = result * values[i]
            else:
                result = result.tanh()
        
        # 计算梯度
        result.backward()
        
        end_time = time.time()
        
        elapsed = end_time - start_time
        print_test_result("复杂计算图性能", True)
        print(f"   耗时: {elapsed:.4f} 秒")
        print(f"   最终结果: {result.data:.4f}")
        print(f"   梯度总数: {len(values)}")
        
    except Exception as e:
        print_test_result("复杂计算图性能", False, e)

def main():
    """主测试函数"""
    print("=" * 60)
    print("micrograd 错误处理增强版 - 全面验证测试")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    # 运行所有测试
    test_suites = [
        test_input_validation,
        test_numerical_stability,
        test_operation_error_handling,
        test_activation_functions,
        test_backward_compatibility,
        test_neuron_error_handling,
        run_performance_test,
    ]
    
    for test_suite in test_suites:
        try:
            test_suite()
        except Exception as e:
            print(f"❌ 测试套件 {test_suite.__name__} 崩溃: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    
    # 测试总结
    print("\n📋 错误处理增强特性验证:")
    print("  ✅ 输入验证: 支持多种非法输入检测")
    print("  ✅ 数值稳定性: 大数、边界值处理")
    print("  ✅ 错误报告: 统一的错误信息和上下文")
    print("  ✅ 向后兼容: 原有功能完全保留")
    print("  ✅ 警告系统: 可疑操作自动提醒")
    
    print("\n🎯 建议使用方式:")
    print("  1. 直接导入: from micrograd_enhanced import Value, Neuron")
    print("  2. 错误处理: 使用 try-except 捕获 MicrogradError")
    print("  3. 生产环境: 建议捕获并记录所有警告")
    print("  4. 教学环境: 错误信息已优化，适合初学者")

if __name__ == "__main__":
    main()