#!/usr/bin/env python3
"""阶段6: 高级特性 (Ch6-7)"""

# 6.1 切片
list1 = [0, 1, 2, 3, 4, 5]
print(f"切片: {list1[1:3]}")       # [1, 2]
print(f"步长: {list1[::2]}")       # [0, 2, 4]
print(f"反转: {list1[::-1]}")      # [5, 4, 3, 2, 1, 0]

# 6.2 迭代
d = {'a': 1, 'b': 2}
for k, v in d.items():
    print(f"dict: {k}={v}")

# 6.3 列表生成式
squares = [x**2 for x in range(10)]
print(f"squares: {squares}")

# 6.4 生成器
def fib():
    a, b = 0, 1
    while True:
        yield b
        a, b = b, a + b

f = fib()
print(f"生成器: {[next(f) for _ in range(6)]}")

# 7.1-7.3 高阶函数
print(f"map: {list(map(str, [1, 2, 3]))}")
from functools import reduce
print(f"reduce: {reduce(lambda x, y: x + y, [1, 2, 3, 4])}")
print(f"filter: {list(filter(lambda x: x % 2 == 0, range(10)))}")
print(f"sorted: {sorted([3, 1, 2], key=lambda x: -x)}")

# 7.4-7.7 闭包/装饰器
def logger(func):
    def wrapper(*args, **kwargs):
        print(f"调用: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@logger
def hello():
    print("Hello!")

hello()

# 偏函数
import functools
int2 = functools.partial(int, base=2)
print(f"偏函数: int2('1010') = {int2('1010')}")
