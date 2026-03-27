#!/usr/bin/env python3
"""阶段10: 进程与线程 (Ch13)"""
import threading
import time
import multiprocessing

# 13.1 多进程（概念）
print(f"CPU 核心数: {multiprocessing.cpu_count()}")

# 13.2 多线程
lock = threading.Lock()
counter = 0

def increment():
    global counter
    for _ in range(10000):
        with lock:
            counter += 1

threads = [threading.Thread(target=increment) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"多线程计数器: {counter}")  # 40000

# 13.3 ThreadLocal
local_data = threading.local()

def worker(name):
    local_data.name = name
    time.sleep(0.01)
    print(f"ThreadLocal: {local_data.name}")

threads = [threading.Thread(target=worker, args=(f'Thread-{i}',)) for i in range(3)]
for t in threads:
    t.start()
for t in threads:
    t.join()

# 13.4 进程 vs 线程
print("""
进程 vs 线程:
- 进程: 独立内存空间，开销大，适合CPU密集
- 线程: 共享内存，开销小，适合IO密集
- Python GIL: 全局解释器锁限制多线程并行
""")
