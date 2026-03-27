#!/usr/bin/env python3
"""阶段2: 函数 (Ch5)"""

# 5.1 调用函数
def add(a, b):
    return a + b

print(f"add(1, 2) = {add(1, 2)}")

# 数据类型转换
print(f"int('123') = {int('123')}")
print(f"float(3) = {float(3)}")
print(f"str(123) = {str(123)}")

# 5.2 函数的参数
def power(x, n=2):
    return x ** n

print(f"power(3) = {power(3)}")        # 默认参数
print(f"power(3, 3) = {power(3, 3)}")  # 指定参数

# 可变参数 *args
def calc(*args):
    return sum(args)

print(f"calc(1, 2, 3) = {calc(1, 2, 3)}")

# 关键字参数 **kwargs
def person(name, **kw):
    print(f"姓名: {name}, 其他: {kw}")

person('Alice', age=25, city='Beijing')

# 5.3 递归函数
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(f"factorial(5) = {factorial(5)}")  # 120

# 尾递归（概念，Python不优化）
def tail_factorial(n, acc=1):
    if n <= 1:
        return acc
    return tail_factorial(n - 1, acc * n)

print(f"tail_factorial(5) = {tail_factorial(5)}")
