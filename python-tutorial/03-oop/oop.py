#!/usr/bin/env python3
"""阶段3: OOP (Ch9-10)"""

class Student:
    """9.1-9.3: 类、实例、继承"""
    def __init__(self, name, score):
        self.name = name
        self.__score = score  # 私有属性

    @property
    def score(self):
        return self.__score

    @score.setter
    def score(self, value):
        if 0 <= value <= 100:
            self.__score = value
        else:
            raise ValueError('score must be 0-100')

    def __str__(self):
        return f'Student({self.name}, {self.score})'

s = Student('Alice', 90)
print(s)  # Student(Alice, 90)
s.score = 95
print(f"score: {s.score}")

# 9.3 继承
class GraduateStudent(Student):
    def __init__(self, name, score, thesis):
        super().__init__(name, score)
        self.thesis = thesis

g = GraduateStudent('Bob', 85, 'AI Research')
print(f"{g.name}, thesis: {g.thesis}")

# 9.4 获取对象信息
print(f"type: {type(s)}")
print(f"isinstance: {isinstance(s, Student)}")
print(f"dir: {[x for x in dir(s) if not x.startswith('_')][:5]}")

# 10.1 __slots__
class Point:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
print(f"Point: ({p.x}, {p.y})")

# 10.4 定制类
class Fib:
    def __init__(self):
        self.a, self.b = 0, 1

    def __iter__(self):
        return self

    def __next__(self):
        self.a, self.b = self.b, self.a + self.b
        if self.a > 100:
            raise StopIteration
        return self.a

    def __getitem__(self, n):
        a, b = 1, 1
        for _ in range(n):
            a, b = b, a + b
        return a

f = Fib()
print(f"Fib: {[x for x in f]}")
print(f"Fib[5]: {f[5]}")

# 10.5 枚举
from enum import Enum, unique

@unique
class Weekday(Enum):
    Mon = 1
    Tue = 2
    Wed = 3

print(f"Enum: {Weekday.Mon}, value: {Weekday.Mon.value}")
