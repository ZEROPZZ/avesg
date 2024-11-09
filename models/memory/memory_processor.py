from typing import Dict, List, Any, Optional
from .memory_core import MemoryCore, MemoryType, MemoryItem
import numpy as np # type: ignore
from datetime import datetime, timedelta

class MemoryProcessor:
    def __init__(self):
        self.memory_core = MemoryCore()
        self.processing_queue = []
        
    def process_new_information(self, information: Dict):
        """处理新信息"""
        # 分析信息重要性
        importance = self._analyze_importance(information)
        
        # 生成标签
        tags = self._generate_tags(information)
        
        # 确定记忆类型
        memory_type = self._determine_memory_type(importance)
        
        # 存储记忆
        self.memory_core.store_memory(
            content=information,
            memory_type=memory_type,
            importance=importance,
            tags=tags
        )
        
    def _analyze_importance(self, information: Dict) -> float:
        """分析信息重要性"""
        importance_factors = {
            'frequency': 0.3,
            'emotional_value': 0.3,
            'relevance': 0.4
        }
        
        # 计算重要性分数
        importance = sum(
            importance_factors[factor] * self._calculate_factor_score(information, factor)
            for factor in importance_factors
        )
        
        return min(max(importance, 0), 1)  # 确保在0-1范围内
        
    def _calculate_factor_score(self, information: Dict, factor: str) -> float:
        """计算特定因素的分数"""
        # 实现具体的因素分数计算逻辑
        return 0.5
        
    def _generate_tags(self, information: Dict) -> List[str]:
        """生成记忆标签"""
        tags = []
        
        # 基于内容生成标签
        if 'category' in information:
            tags.append(information['category'])
        if 'context' in information:
            tags.extend(information['context'].split())
            
        return list(set(tags))  # 去重
        
    def _determine_memory_type(self, importance: float) -> MemoryType:
        """确定记忆类型"""
        if importance >= 0.8:
            return MemoryType.LONG_TERM
        elif importance >= 0.4:
            return MemoryType.SHORT_TERM
        else:
            return MemoryType.WORKING
            
    def search_memories(self, query: Dict) -> List[MemoryItem]:
        """搜索记忆"""
        return self.memory_core.retrieve_memory(query)
        
    def maintain_memories(self):
        """维护记忆系统"""
        # 执行记忆巩固
        self.memory_core.consolidate_memories()
        
        # 执行记忆遗忘
        self.memory_core.forget_memories()
        
    def get_related_memories(self, memory_id: str) -> List[MemoryItem]:
        """获取相关记忆"""
        memory = self.memory_core.long_term_memory.get(memory_id)
        if memory and memory.associations:
            related_memories = []
            for associated_id in memory.associations:
                if associated_memory := self.memory_core.long_term_memory.get(associated_id):
                    related_memories.append(associated_memory)
            return related_memories
        return [] 