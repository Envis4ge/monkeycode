#!/usr/bin/env python3
"""阶段12: 图形界面与网络编程 (Ch17-19)"""
import socket
import threading
import time
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

# 17.1-17.2 Tkinter/turtle 概念（服务器环境无GUI）
print("Tkinter: Label/Button/Entry + pack/grid/place 布局")
print("turtle: forward/right/circle 画图")

# 18.2 TCP 编程
def tcp_demo():
    # 服务器
    def server():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', 9999))
        s.listen(1)
        conn, addr = s.accept()
        data = conn.recv(1024).decode()
        conn.send(f'Hello, {data}!'.encode())
        conn.close()
        s.close()

    # 启动服务器
    t = threading.Thread(target=server)
    t.daemon = True
    t.start()
    time.sleep(0.1)

    # 客户端
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 9999))
    s.send(b'Python')
    resp = s.recv(1024).decode()
    s.close()
    t.join(timeout=2)
    print(f"TCP: 客户端发送 'Python', 收到 '{resp}'")

tcp_demo()

# 18.3 UDP 编程
def udp_demo():
    def server():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('127.0.0.1', 9998))
        data, addr = s.recvfrom(1024)
        s.sendto(f'UDP Echo: {data.decode()}'.encode(), addr)
        s.close()

    t = threading.Thread(target=server)
    t.daemon = True
    t.start()
    time.sleep(0.1)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(b'Hello UDP', ('127.0.0.1', 9998))
    data, addr = s.recvfrom(1024)
    s.close()
    print(f"UDP: {data.decode()}")

udp_demo()

# 19.1-19.2 电子邮件
msg = MIMEText('测试邮件正文', 'plain', 'utf-8')
msg['From'] = formataddr(('发件人', 'sender@example.com'))
msg['Subject'] = Header('测试邮件', 'utf-8').encode()
print(f"邮件: From={msg['From']}, Subject={msg['Subject']}")
