#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库缓存管理系统
用于提高查询效率和学习用户习惯
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any


class KnowledgeBaseCache:
    """知识库缓存管理系统"""
    
    def __init__(self, cache_dir: str = "knowledge_base/cache"):
        """初始化缓存系统"""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.query_cache_file = self.cache_dir / "query_cache.json"
        self.hot_commands_file = self.cache_dir / "hot_commands.json"
        self.user_history_file = self.cache_dir / "user_history.json"
        self.stats_file = self.cache_dir / "stats.json"
        
        self.query_cache = {}
        self.hot_commands = {}
        self.user_history = {}
        self.stats = {
            "total_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "created_at": datetime.now().isoformat()
        }
        
        self.load_cache()
    
    def load_cache(self):
        """加载所有缓存文件"""
        if self.query_cache_file.exists():
            with open(self.query_cache_file, 'r', encoding='utf-8') as f:
                self.query_cache = json.load(f)
        
        if self.hot_commands_file.exists():
            with open(self.hot_commands_file, 'r', encoding='utf-8') as f:
                self.hot_commands = json.load(f)
        
        if self.user_history_file.exists():
            with open(self.user_history_file, 'r', encoding='utf-8') as f:
                self.user_history = json.load(f)
        
        if self.stats_file.exists():
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                self.stats = json.load(f)
    
    def save_cache(self):
        """保存所有缓存文件"""
        with open(self.query_cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.query_cache, f, ensure_ascii=False, indent=2)
        
        with open(self.hot_commands_file, 'w', encoding='utf-8') as f:
            json.dump(self.hot_commands, f, ensure_ascii=False, indent=2)
        
        with open(self.user_history_file, 'w', encoding='utf-8') as f:
            json.dump(self.user_history, f, ensure_ascii=False, indent=2)
        
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
    
    def get_cached_query(self, query_key: str, cache_ttl: int = 86400) -> Optional[Dict]:
        """获取缓存的查询结果"""
        if query_key not in self.query_cache:
            self.stats["cache_misses"] += 1
            return None
        
        cache_entry = self.query_cache[query_key]
        cache_age = time.time() - cache_entry['timestamp']
        
        if cache_age > cache_ttl:
            del self.query_cache[query_key]
            self.stats["cache_misses"] += 1
            return None
        
        cache_entry['hit_count'] = cache_entry.get('hit_count', 0) + 1
        self.stats["cache_hits"] += 1
        self.save_cache()
        
        return cache_entry
    
    def cache_query_result(self, query_key: str, results: List[Dict], 
                          device: str = "ZXA10_OLT"):
        """缓存查询结果"""
        self.query_cache[query_key] = {
            'timestamp': time.time(),
            'device': device,
            'results': results,
            'hit_count': 0,
            'result_count': len(results)
        }
        
        for result in results:
            cmd_name = result.get('name', '')
            if cmd_name:
                self.hot_commands[cmd_name] = self.hot_commands.get(cmd_name, 0) + 1
        
        self.stats["total_queries"] += 1
        self.stats["last_query"] = datetime.now().isoformat()
        
        self.save_cache()
    
    def record_user_query(self, user_id: str, query_key: str, 
                         results_count: int, device: str = "ZXA10_OLT"):
        """记录用户查询历史"""
        if user_id not in self.user_history:
            self.user_history[user_id] = {
                'total_queries': 0,
                'favorite_commands': [],
                'favorite_scenarios': [],
                'query_log': []
            }
        
        user_profile = self.user_history[user_id]
        user_profile['total_queries'] += 1
        user_profile['query_log'].append({
            'timestamp': datetime.now().isoformat(),
            'query': query_key,
            'device': device,
            'results_count': results_count
        })
        
        if len(user_profile['query_log']) > 100:
            user_profile['query_log'] = user_profile['query_log'][-100:]
        
        self.save_cache()
    
    def get_hot_commands(self, limit: int = 10) -> List[tuple]:
        """获取热点命令"""
        sorted_commands = sorted(
            self.hot_commands.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_commands[:limit]
    
    def get_user_favorites(self, user_id: str) -> Dict[str, Any]:
        """获取用户偏好"""
        if user_id not in self.user_history:
            return {}
        
        user_profile = self.user_history[user_id]
        
        query_counts = {}
        for log in user_profile['query_log']:
            query = log['query']
            query_counts[query] = query_counts.get(query, 0) + 1
        
        favorite_queries = sorted(
            query_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'user_id': user_id,
            'total_queries': user_profile['total_queries'],
            'favorite_queries': [q[0] for q in favorite_queries],
            'recent_queries': [log['query'] for log in user_profile['query_log'][-10:]]
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        hit_rate = 0
        if self.stats["total_queries"] > 0:
            hit_rate = (self.stats["cache_hits"] / self.stats["total_queries"]) * 100
        
        return {
            **self.stats,
            'cache_hit_rate': f"{hit_rate:.1f}%",
            'cached_queries': len(self.query_cache),
            'hot_commands_count': len(self.hot_commands),
            'users_tracked': len(self.user_history)
        }
    
    def clear_old_cache(self, days: int = 7):
        """清理旧缓存"""
        cutoff_time = time.time() - (days * 86400)
        
        keys_to_delete = []
        for key, entry in self.query_cache.items():
            if entry['timestamp'] < cutoff_time:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self.query_cache[key]
        
        self.save_cache()
        return len(keys_to_delete)


if __name__ == "__main__":
    cache = KnowledgeBaseCache()
    print("知识库缓存系统初始化完成")
    print(f"统计: {cache.get_stats()}")
