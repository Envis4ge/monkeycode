#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库AI查询助手
带缓存的知识库查询系统
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any


class KBAIAssistant:
    """知识库AI查询助手"""
    
    def __init__(self, device: str = "ZXA10_OLT", kb_root: str = "knowledge_base"):
        self.device = device
        self.kb_root = Path(kb_root)
        self.kb_path = self.kb_root / "devices" / device
        
        self._scenario_cache = {}
        self._keyword_cache = {}
        self._command_cache = {}
        
        try:
            from tools.cache_manager import KnowledgeBaseCache
            self.cache = KnowledgeBaseCache()
        except ImportError:
            self.cache = None
    
    def query(self, question: str, user_id: str = "default") -> Dict[str, Any]:
        """查询知识库"""
        keywords = self._extract_keywords(question)
        query_key = "_".join(keywords) if keywords else question[:20]
        
        if self.cache:
            cached = self.cache.get_cached_query(query_key)
            if cached:
                self.cache.record_user_query(user_id, query_key, len(cached['results']))
                return {
                    "source": "cache",
                    "results": cached['results'],
                    "keywords": keywords,
                    "question": question
                }
        
        results = self._search_in_kb(keywords, question)
        
        if self.cache and results:
            self.cache.cache_query_result(query_key, results)
            self.cache.record_user_query(user_id, query_key, len(results))
        
        return {
            "source": "file",
            "results": results,
            "keywords": keywords,
            "question": question
        }
    
    def query_by_scenario(self, scenario: str) -> List[Dict]:
        """按场景查询"""
        if scenario in self._scenario_cache:
            return self._scenario_cache[scenario]
        
        scenario_file = self.kb_path / "docs" / "SCENARIO_COMMANDS.md"
        if not scenario_file.exists():
            return []
        
        results = self._parse_scenario_file(scenario_file, scenario)
        self._scenario_cache[scenario] = results
        return results
    
    def query_by_keyword(self, keyword: str) -> List[Dict]:
        """按关键字查询"""
        keyword = keyword.lower()
        if keyword in self._keyword_cache:
            return self._keyword_cache[keyword]
        
        index_file = self.kb_path / "indexes" / "INDEX_BY_KEYWORD.md"
        if not index_file.exists():
            return []
        
        results = self._search_in_index(index_file, keyword)
        self._keyword_cache[keyword] = results
        return results
    
    def query_command(self, command_name: str) -> Optional[Dict]:
        """查询命令详情"""
        cmd_key = command_name.lower()
        if cmd_key in self._command_cache:
            return self._command_cache[cmd_key]
        
        index_file = self.kb_path / "commands" / "INDEX.json"
        if not index_file.exists():
            return None
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            for cmd in index_data.get('commands', []):
                if cmd.get('name', '').lower() == cmd_key:
                    self._command_cache[cmd_key] = cmd
                    return cmd
        except:
            pass
        
        return None
    
    def get_stats(self) -> Dict:
        """获取统计"""
        if self.cache:
            return self.cache.get_stats()
        return {"message": "缓存系统未初始化"}
    
    def get_hot_commands(self, limit: int = 10) -> List:
        """获取热点命令"""
        if self.cache:
            return self.cache.get_hot_commands(limit)
        return []
    
    def _extract_keywords(self, question: str) -> List[str]:
        """提取关键字"""
        words = re.findall(r'[a-zA-Z]+', question.lower())
        stop_words = {'the', 'a', 'an', 'is', 'are', 'how', 'to', 'what', 'do', 'can', 'i', 'you', 'we', 'me', 'my'}
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return keywords[:3]
    
    def _search_in_kb(self, keywords: List[str], question: str) -> List[Dict]:
        """在知识库中搜索"""
        results = []
        
        scenario_map = {
            "bgp": "BGP配置", "ospf": "OSPF配置", "vlan": "VLAN配置",
            "qos": "QoS配置", "dhcp": "DHCP配置", "acl": "ACL配置",
            "mpls": "MPLS配置", "interface": "接口配置",
        }
        
        for kw in keywords:
            if kw in scenario_map:
                results.extend(self.query_by_scenario(scenario_map[kw]))
        
        for kw in keywords:
            results.extend(self.query_by_keyword(kw))
        
        seen = set()
        unique = []
        for r in results:
            name = r.get('name', '')
            if name and name not in seen:
                seen.add(name)
                unique.append(r)
        
        return unique[:20]
    
    def _parse_scenario_file(self, file_path: Path, scenario: str) -> List[Dict]:
        """解析场景文件"""
        results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            in_scenario = False
            
            for line in lines:
                if scenario in line and ('##' in line):
                    in_scenario = True
                    continue
                
                if in_scenario and line.startswith('##'):
                    break
                
                if in_scenario and '|' in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3 and parts[2]:
                        results.append({
                            "name": parts[2],
                            "description": parts[3] if len(parts) > 3 else ""
                        })
        except:
            pass
        
        return results
    
    def _search_in_index(self, index_file: Path, keyword: str) -> List[Dict]:
        """在索引文件中搜索"""
        results = []
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            for line in lines:
                if keyword.lower() in line.lower() and '**' in line:
                    matches = re.findall(r'\*\*([^*]+)\*\*', line)
                    for cmd in matches:
                        results.append({
                            "name": cmd.strip(),
                            "keyword": keyword
                        })
        except:
            pass
        
        return results


def query(question: str, device: str = "ZXA10_OLT") -> Dict:
    """快速查询接口"""
    ai = KBAIAssistant(device)
    return ai.query(question)


def get_hot(limit: int = 10, device: str = "ZXA10_OLT") -> List:
    """获取热点命令"""
    ai = KBAIAssistant(device)
    return ai.get_hot_commands(limit)


def get_stats(device: str = "ZXA10_OLT") -> Dict:
    """获取统计"""
    ai = KBAIAssistant(device)
    return ai.get_stats()


if __name__ == "__main__":
    print("知识库AI查询助手初始化")
    ai = KBAIAssistant()
    print(f"统计: {ai.get_stats()}")
