#!/usr/bin/env python3
"""阶段1: Python 基础 (Ch1-4)"""
# 1.1 print 和 input
print("Hello, Python!")

name = input("你的名字: ")
print(f"你好, {name}!")

# 1.2 数据类型
x = 10          # int
y = 3.14        # float
s = "hello"     # str
b = True        # bool
n = None        # NoneType

print(f"int: {x}, float: {y}, str: {s}, bool: {b}, None: {n}")

# 2.2 字符串与编码
s1 = 'hello'
s2 = "world"
s3 = """多行
字符串"""
print(f"s1={s1}, s2={s2}, s3={s3}")

# bytes
b = b'hello'
print(f"bytes: {b}, decode: {b.decode()}")

# 3.1 list 和 tuple
list1 = [1, 2, 3, 4, 5]
tuple1 = (1, 2, 3)
print(f"list: {list1}, 切片[1:3]: {list1[1:3]}")
print(f"tuple: {tuple1}")

# 3.2 dict 和 set
d = {'a': 1, 'b': 2, 'c': 3}
s = {1, 2, 3, 3, 4}
print(f"dict: {d}, set: {s}")

# 4.1 条件判断
score = 85
if score >= 90:
    print('A')
elif score >= 80:
    print('B')
else:
    print('C')

# 4.2 循环
for i in range(5):
    print(f"for循环: {i}", end=" ")
print()

n = 0
while n < 3:
    print(f"while循环: {n}", end=" ")
    n += 1
print()
