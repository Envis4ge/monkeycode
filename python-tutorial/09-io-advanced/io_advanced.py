#!/usr/bin/env python3
"""阶段9: IO高级 (Ch12.4-12.5)"""
import json
import pickle
import os
import shutil

# 12.4 序列化 - JSON
data = {'name': 'Alice', 'age': 25, 'scores': [90, 85, 92]}
json_str = json.dumps(data, ensure_ascii=False, indent=2)
print(f"JSON 序列化:\n{json_str}")

restored = json.loads(json_str)
print(f"JSON 反序列化: {restored['name']}")

# 自定义 JSON 序列化
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __json__(self):
        return {'name': self.name, 'age': self.age}

s = Student('Bob', 20)
print(f"自定义序列化: {json.dumps(s.__json__())}")

# 12.4 序列化 - Pickle
pickled = pickle.dumps(data)
restored = pickle.loads(pickled)
print(f"Pickle: {restored['name']}")

# 12.3 文件和目录操作
os.makedirs('/tmp/test_dir/sub', exist_ok=True)
with open('/tmp/test_dir/test.txt', 'w') as f:
    f.write('test')
print(f"目录: {os.listdir('/tmp/test_dir')}")
print(f"文件存在: {os.path.exists('/tmp/test_dir/test.txt')}")
print(f"文件大小: {os.path.getsize('/tmp/test_dir/test.txt')}")
shutil.rmtree('/tmp/test_dir')
