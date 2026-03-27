#!/usr/bin/env python3
"""阶段13: Web开发 (Ch20-22)"""
import sqlite3
import asyncio
import json

# 20.1 SQLite
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()
cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)')
cursor.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')")
cursor.execute("INSERT INTO users VALUES (2, 'Bob', 'bob@example.com')")
conn.commit()

cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
print(f"SQLite 查询: {len(rows)} 行")
conn.close()

# 21.3 WSGI 接口
def app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b'<h1>Hello WSGI!</h1>']

# 22.1-22.3 异步IO
async def fetch(url, delay):
    await asyncio.sleep(delay)
    return f'{url} done'

async def main():
    results = await asyncio.gather(
        fetch('url1', 0.01),
        fetch('url2', 0.02),
        fetch('url3', 0.01),
    )
    return results

results = asyncio.run(main())
print(f"asyncio.gather: {results}")

# Task
async def task_demo():
    task = asyncio.create_task(fetch('task', 0.01))
    result = await task
    return result

result = asyncio.run(task_demo())
print(f"asyncio.create_task: {result}")

# 超时控制
async def timeout_demo():
    try:
        await asyncio.wait_for(asyncio.sleep(10), timeout=0.01)
    except asyncio.TimeoutError:
        return 'timeout'

result = asyncio.run(timeout_demo())
print(f"asyncio.wait_for: {result}")
