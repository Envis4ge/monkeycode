#!/usr/bin/env python3
"""阶段5: IO编程 (Ch12)"""

import io
import os
import json
import pickle

# 12.1 文件读写
with open('/tmp/test_file.txt', 'w', encoding='utf-8') as f:
    f.write('Hello, 文件读写!')

with open('/tmp/test_file.txt', 'r', encoding='utf-8') as f:
    print(f"读取: {f.read()}")

# 12.2 StringIO/BytesIO
sio = io.StringIO()
sio.write('hello')
sio.seek(0)
print(f"StringIO: {sio.read()}")

bio = io.BytesIO()
bio.write(b'binary data')
bio.seek(0)
print(f"BytesIO: {bio.read()}")

# 12.3 操作文件和目录
print(f"当前目录: {os.getcwd()}")
print(f"文件列表: {os.listdir('.')[:3]}")

# 12.4 序列化
data = {'name': 'Alice', 'age': 25}
json_str = json.dumps(data)
print(f"JSON: {json_str}")
print(f"反序列化: {json.loads(json_str)}")

# pickle
pickled = pickle.dumps(data)
print(f"Pickle: {pickle.loads(pickled)}")
