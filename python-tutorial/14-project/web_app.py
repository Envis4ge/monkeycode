#!/usr/bin/env python3
"""阶段14: 实战项目 - Web App 骨架"""
import sqlite3
import asyncio
import json
from datetime import datetime
import logging

# ========== Day 2: 日志系统 ==========
logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logger.addHandler(handler)

# ========== Day 3: ORM (元类) ==========
class Field:
    def __init__(self, name, column_type):
        self.name = name
        self.column_type = column_type

class StringField(Field):
    def __init__(self, name):
        super().__init__(name, 'VARCHAR(100)')

class IntegerField(Field):
    def __init__(self, name):
        super().__init__(name, 'INTEGER')

class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        mappings = {}
        for k, v in attrs.items():
            if isinstance(v, Field):
                mappings[k] = v
        for k in mappings:
            attrs.pop(k)
        attrs['__mappings__'] = mappings
        attrs['__table__'] = name.lower() + 's'
        return type.__new__(cls, name, bases, attrs)

class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kw):
        super().__init__(**kw)

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def save(self):
        fields = [v.name for v in self.__mappings__.values()]
        params = [self.get(k) for k in self.__mappings__]
        sql = f"INSERT INTO {self.__table__} ({','.join(fields)}) VALUES ({','.join(['?']*len(params))})"
        return sql, params

# ========== Day 4: Model 层 ==========
class User(Model):
    id = IntegerField('id')
    name = StringField('name')
    email = StringField('email')

# ========== Day 5: Web 框架 ==========
class Request:
    def __init__(self, method='GET', path='/', body=None):
        self.method = method
        self.path = path
        self.body = body

class Response:
    def __init__(self, body='', status=200, content_type='text/html'):
        self.body = body
        self.status = status
        self.content_type = content_type

class SimpleFramework:
    def __init__(self):
        self.routes = {}

    def route(self, path, methods=['GET']):
        def decorator(f):
            for m in methods:
                self.routes[(m, path)] = f
            return f
        return decorator

    def handle(self, request):
        handler = self.routes.get((request.method, request.path))
        if handler:
            return handler(request)
        return Response('404 Not Found', 404)

# ========== Day 6: 配置 ==========
class Config:
    DEBUG = True
    DATABASE = ':memory:'
    SECRET_KEY = 'dev-secret-key'

# ========== Day 7: MVC ==========
class TaskController:
    def __init__(self, db):
        self.db = db

    def list(self):
        rows = self.db.fetchall('SELECT * FROM tasks')
        return {'tasks': [dict(r) for r in rows]}

    def create(self, title):
        self.db.execute('INSERT INTO tasks (title, done) VALUES (?, ?)', (title, False))
        return {'status': 'created', 'title': title}

class Database:
    def __init__(self, db=':memory:'):
        self.conn = sqlite3.connect(db)
        self.conn.row_factory = sqlite3.Row

    def execute(self, sql, params=()):
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        self.conn.commit()
        return cursor

    def fetchall(self, sql, params=()):
        return self.execute(sql, params).fetchall()

# ========== 运行 ==========
if __name__ == '__main__':
    # 初始化
    db = Database()
    db.execute('CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT, done BOOLEAN)')
    db.execute('INSERT INTO tasks VALUES (1, "学习Python", 1)')
    db.execute('INSERT INTO tasks VALUES (2, "学习Flask", 0)')

    # ORM
    user = User(id=1, name='Alice', email='alice@example.com')
    sql, params = user.save()
    logger.info(f"ORM save: {sql}")

    # Web 框架
    fw = SimpleFramework()

    @fw.route('/')
    def index(req):
        return Response('<h1>Home</h1>')

    @fw.route('/api/tasks')
    def get_tasks(req):
        controller = TaskController(db)
        return Response(json.dumps(controller.list()), 200, 'application/json')

    # 测试
    resp = fw.handle(Request('GET', '/'))
    logger.info(f"GET / => {resp.status}")

    resp = fw.handle(Request('GET', '/api/tasks'))
    logger.info(f"GET /api/tasks => {resp.status}")

    print("\n✅ 实战项目 Web App 运行成功!")
