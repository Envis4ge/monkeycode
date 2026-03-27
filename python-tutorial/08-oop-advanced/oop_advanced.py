#!/usr/bin/env python3
"""阶段8: OOP高级 (Ch10)"""
from enum import Enum, unique

# 10.1 __slots__
class Student:
    __slots__ = ('name', 'age')
    def __init__(self, name, age):
        self.name = name
        self.age = age

s = Student('Alice', 20)
print(f"Student: {s.name}, {s.age}")

# 10.2 @property
class Screen:
    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if value > 0:
            self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if value > 0:
            self._height = value

    @property
    def resolution(self):
        return self._width * self._height

scr = Screen()
scr.width = 1920
scr.height = 1080
print(f"Resolution: {scr.resolution}")

# 10.3 多重继承
class Animal:
    pass

class Runnable:
    def run(self):
        print("Running!")

class Dog(Animal, Runnable):
    pass

dog = Dog()
dog.run()

# 10.4 定制类
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return f'Vector({self.x}, {self.y})'

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __abs__(self):
        return (self.x**2 + self.y**2)**0.5

v1 = Vector(3, 4)
v2 = Vector(1, 2)
print(f"v1: {v1}, |v1|: {abs(v1)}, v1+v2: {v1+v2}")

# 10.5 枚举
@unique
class Status(Enum):
    PENDING = 1
    RUNNING = 2
    DONE = 3

print(f"Status: {Status.RUNNING}, value: {Status.RUNNING.value}")

# 10.6 元类
def hello(self):
    return f"Hello, {self.name}"

# 动态创建类
Hello = type('Hello', (object,), {'name': 'Dynamic', 'hello': hello})
h = Hello()
print(f"Metaclass: {h.hello()}")
