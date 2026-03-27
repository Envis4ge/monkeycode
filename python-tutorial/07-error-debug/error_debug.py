#!/usr/bin/env python3
"""阶段7: 错误调试与测试 (Ch11)"""

import logging
import unittest

# 11.1 错误处理
def divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        print("除数不能为0")
        return None
    except TypeError:
        print("参数类型错误")
        return None
    finally:
        print("finally 总会执行")

print(f"divide(10, 3) = {divide(10, 3)}")
print(f"divide(10, 0) = {divide(10, 0)}")

# 11.2 调试
logging.basicConfig(level=logging.DEBUG)
logging.debug('调试信息')
logging.info('普通信息')
logging.warning('警告信息')

# 11.3 单元测试
class TestDivide(unittest.TestCase):
    def test_normal(self):
        self.assertAlmostEqual(divide(10, 3), 3.333, places=3)

    def test_zero(self):
        self.assertIsNone(divide(10, 0))

# 11.4 doctest
def factorial(n):
    """
    计算阶乘
    >>> factorial(5)
    120
    >>> factorial(1)
    1
    """
    if n <= 1:
        return 1
    return n * factorial(n - 1)

if __name__ == '__main__':
    unittest.main(argv=[''], exit=False, verbosity=2)
