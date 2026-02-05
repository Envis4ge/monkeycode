from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import asyncio
import json
import logging

from src.remote.connection_manager import ConnectionManager
from src.remote.session_manager import SessionManager
from src.remote.category_manager import CategoryManager
from src.remote.command_history import CommandHistory
from src.ai.command_converter import convert_natural_language_to_command
from src.models.remote import (
    RemoteConnectionConfig,
    DeviceProductCategory,
    AuthType,
    ConnectionProtocol
)

app = FastAPI(title="SmartTerm Web API", version="1.0.0")

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应限制为具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局实例
connection_manager = ConnectionManager()
session_manager = SessionManager()
category_manager = CategoryManager()

@app.on_event("startup")
async def startup_event():
    # 初始化默认设备产品类别
    await category_manager.initialize_default_categories()
    print("SmartTerm Web API started successfully!")

@app.get("/")
async def root():
    return {"message": "SmartTerm Web API", "version": "1.0.0"}

@app.get("/api/configs")
async def list_configs():
    """获取所有连接配置"""
    configs = await connection_manager.list_saved_configs()
    return {"configs": [config.__dict__ for config in configs]}

@app.post("/api/configs")
async def add_config(config_data: dict):
    """添加连接配置"""
    config = RemoteConnectionConfig(
        id=0,  # 数据库会自动分配ID
        name=config_data["name"],
        host=config_data["host"],
        port=config_data.get("port", 22),
        auth_type=AuthType(config_data.get("auth_type", "password")),
        username=config_data["username"],
        password=config_data.get("password"),
        key_path=config_data.get("key_path"),
        protocol=ConnectionProtocol(config_data.get("protocol", "ssh"))
    )

    await connection_manager.save_config(config)
    return {"message": f"Configuration '{config.name}' saved successfully"}

@app.get("/api/configs/{config_id}")
async def get_config(config_id: int):
    """根据ID获取连接配置"""
    config = await connection_manager.get_config_by_id(config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config

@app.delete("/api/configs/{config_id}")
async def delete_config(config_id: int):
    """删除连接配置"""
    try:
        await connection_manager.delete_config(config_id)
        return {"message": "Configuration deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/connect")
async def connect_to_host(connection_data: dict):
    """连接到远程主机"""
    config = RemoteConnectionConfig(
        id=connection_data.get("id", 0),
        name=connection_data.get("name", f"temp_{connection_data['host']}_{connection_data['port']}"),
        host=connection_data["host"],
        port=connection_data.get("port", 22),
        auth_type=AuthType(connection_data.get("auth_type", "password")),
        username=connection_data["username"],
        password=connection_data.get("password"),
        key_path=connection_data.get("key_path"),
        protocol=ConnectionProtocol(connection_data.get("protocol", "ssh"))
    )

    try:
        session = await connection_manager.connect(config)
        return {
            "session_id": session.id,
            "status": session.status.value,
            "host": session.host,
            "port": session.port,
            "username": session.username
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/disconnect")
async def disconnect():
    """断开当前连接"""
    try:
        await connection_manager.disconnect()
        return {"message": "Disconnected successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/session")
async def get_active_session():
    """获取当前活动会话"""
    session = connection_manager.get_active_session()
    if session:
        return {
            "session_id": session.id,
            "status": session.status.value,
            "host": session.host,
            "port": session.port,
            "username": session.username,
            "protocol": session.protocol.value,
            "is_active": session.is_active
        }
    return {"message": "No active session"}

@app.post("/api/command")
async def execute_command(command_data: dict):
    """执行命令"""
    command = command_data.get("command", "")
    mode = command_data.get("mode", "interactive")  # "interactive" or "ai"

    try:
        if mode == "ai":
            # 使用AI转换自然语言为命令
            category_id = 0  # 获取当前会话的设备类别
            session = connection_manager.get_active_session()
            if session:
                category = await category_manager.get_category_by_id(session.config_id % 10)  # 简单映射
            else:
                category = None

            parsed_cmd = await convert_natural_language_to_command(command, category)

            if parsed_cmd:
                result = await connection_manager.execute_command(parsed_cmd.command)
                return {
                    "original_request": command,
                    "converted_command": parsed_cmd.command,
                    "explanation": parsed_cmd.explanation,
                    "confidence": parsed_cmd.confidence,
                    "exit_code": result[0],
                    "output": result[1]
                }
            else:
                raise HTTPException(status_code=400, detail="Could not understand the command")
        else:
            # 直接执行命令
            result = await connection_manager.execute_command(command)
            return {
                "command": command,
                "exit_code": result[0],
                "output": result[1]
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.websocket("/ws/terminal")
async def websocket_terminal(websocket: WebSocket):
    """WebSocket终端连接"""
    await websocket.accept()

    try:
        while True:
            # 接收来自前端的命令
            data = await websocket.receive_text()
            command_data = json.loads(data)

            command = command_data.get("command", "")
            mode = command_data.get("mode", "interactive")

            if command == "exit" or command == "quit":
                await websocket.send_text(json.dumps({"type": "output", "data": "disconnecting...\n"}))
                await connection_manager.disconnect()
                break

            try:
                if mode == "ai":
                    # 使用AI转换
                    session = connection_manager.get_active_session()
                    if session:
                        category = await category_manager.get_category_by_id(session.config_id % 10)
                    else:
                        category = None

                    parsed_cmd = await convert_natural_language_to_command(command, category)

                    if parsed_cmd:
                        result = await connection_manager.execute_command(parsed_cmd.command)

                        response = {
                            "type": "ai_result",
                            "original_request": command,
                            "converted_command": parsed_cmd.command,
                            "explanation": parsed_cmd.explanation,
                            "confidence": parsed_cmd.confidence,
                            "exit_code": result[0],
                            "output": result[1]
                        }
                    else:
                        response = {
                            "type": "error",
                            "message": f"Could not understand the request: {command}"
                        }
                else:
                    # 直接执行命令
                    result = await connection_manager.execute_command(command)
                    response = {
                        "type": "output",
                        "command": command,
                        "exit_code": result[0],
                        "output": result[1]
                    }

                await websocket.send_text(json.dumps(response))

            except Exception as e:
                error_response = {
                    "type": "error",
                    "message": str(e)
                }
                await websocket.send_text(json.dumps(error_response))

    except WebSocketDisconnect:
        print("WebSocket disconnected")
        try:
            await connection_manager.disconnect()
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)