#!/usr/bin/env python3
"""阶段11: 常用内建模块 (Ch14-16)"""
import datetime
import collections
import base64
import struct
import hashlib
import itertools
import re

# 14.1 datetime
now = datetime.datetime.now()
print(f"datetime: {now}")
print(f"格式化: {now.strftime('%Y-%m-%d %H:%M:%S')}")

# 14.2 collections
Point = collections.namedtuple('Point', ['x', 'y'])
p = Point(1, 2)
print(f"namedtuple: {p.x}, {p.y}")

d = collections.defaultdict(int)
d['a'] += 1
print(f"defaultdict: {d['a']}")

counter = collections.Counter('abracadabra')
print(f"Counter: {counter.most_common(3)}")

# 14.3 base64
encoded = base64.b64encode(b'hello')
decoded = base64.b64decode(encoded)
print(f"base64: {encoded} -> {decoded}")

# 14.4 struct
packed = struct.pack('>i', 12345)
unpacked = struct.unpack('>i', packed)
print(f"struct: {packed} -> {unpacked}")

# 14.5 hashlib
md5 = hashlib.md5(b'hello').hexdigest()
sha1 = hashlib.sha1(b'hello').hexdigest()
print(f"MD5: {md5}")
print(f"SHA1: {sha1}")

# 14.7 itertools
print(f"itertools.chain: {list(itertools.chain([1,2], [3,4]))}")
print(f"itertools.product: {list(itertools.product([1,2], [3,4]))}")

# 16.1 正则表达式
pattern = re.compile(r'\d+')
result = pattern.findall('abc123def456')
print(f"正则: {result}")
