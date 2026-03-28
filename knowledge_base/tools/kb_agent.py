#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库Agent集成示例
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from kb_ai_assistant import KBAIAssistant


class KnowledgeBaseAgent:
    """知识库Agent"""
    
    def __init__(self, device: str = "ZXA10_OLT"):
        self.ai = KBAIAssistant(device)
        self.device = device
    
    def ask(self, question: str, user_id: str = "default") -> dict:
        """向知识库提问"""
        result = self.ai.query(question, user_id)
        return self._build_response(result)
    
    def _build_response(self, result: dict) -> dict:
        """构建回答"""
        results = result.get("results", [])
        
        if not results:
            return {
                "answer": "抱歉，未找到相关信息",
                "commands": [],
                "source": result.get("source", "unknown")
            }
        
        commands = [r.get("name", "") for r in results if r.get("name")]
        
        answer = f"找到 {len(commands)} 个相关命令：\n\n"
        for i, cmd in enumerate(commands[:10], 1):
            answer += f"{i}. `{cmd}`\n"
        
        if len(commands) > 10:
            answer += f"\n...还有 {len(commands) - 10} 个命令"
        
        return {
            "answer": answer,
            "commands": commands,
            "source": result.get("source", "unknown"),
            "keywords": result.get("keywords", [])
        }
    
    def get_hot(self, limit: int = 10) -> list:
        """获取热点命令"""
        return self.ai.get_hot_commands(limit)
    
    def get_stats(self) -> dict:
        """获取统计"""
        return self.ai.get_stats()


def query(question: str, device: str = "ZXA10_OLT") -> dict:
    """快速查询接口"""
    agent = KnowledgeBaseAgent(device)
    return agent.ask(question)


if __name__ == "__main__":
    agent = KnowledgeBaseAgent()
    print("知识库Agent测试")
    result = agent.ask("如何配置BGP？")
    print(result["answer"])
