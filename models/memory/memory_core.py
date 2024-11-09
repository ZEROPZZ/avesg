import numpy as np # type: ignore
from typing import Dict, List, Any, Optional
import datetime
import json
import pickle
import os
from collections import deque
import logging
from dataclasses import dataclass
from enum import Enum

class MemoryType(Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    WORKING = "working"

@dataclass
class MemoryItem:
    content: Any
    timestamp: datetime.datetime
    importance: float
    memory_type: MemoryType
    tags: List[str]
    access_count: int = 0
    last_access: datetime.datetime = None
    associations: List[str] = None

class MemoryCore:
    def __init__(self):
        self.logger = self._setup_logger()
        
        # 初始化不同类型的记忆存储
        self.short_term_memory = deque(maxlen=100)  # 短期记忆，限制大小
        self.long_term_memory = {}  # 长期记忆
        self.working_memory = deque(maxlen=10)  # 工作记忆，限制大小
        
        # 记忆配置
        self.memory_config = {
            'consolidation_threshold': 0.7,  # 记忆巩固阈值
            'forgetting_rate': 0.1,         # 遗忘率
            'importance_threshold': 0.5      # 重要性阈值
        }
        
        # 加载已存在的记忆
        self._load_memories()

    def _setup_logger(self) -> logging.Logger:
        """设置日志系统"""
        logger = logging.getLogger('memory_core')
        logger.setLevel(logging.DEBUG)
        
        handler = logging.FileHandler('logs/memory.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger

    def store_memory(self, content: Any, memory_type: MemoryType, 
                    importance: float = 0.5, tags: List[str] = None) -> bool:
        """存储新的记忆"""
        try:
            memory_item = MemoryItem(
                content=content,
                timestamp=datetime.datetime.now(),
                importance=importance,
                memory_type=memory_type,
                tags=tags or [],
                associations=[],
                last_access=datetime.datetime.now()
            )

            if memory_type == MemoryType.SHORT_TERM:
                self.short_term_memory.append(memory_item)
            elif memory_type == MemoryType.LONG_TERM:
                self.long_term_memory[str(datetime.datetime.now())] = memory_item
            elif memory_type == MemoryType.WORKING:
                self.working_memory.append(memory_item)

            self.logger.info(f"Stored new {memory_type.value} memory")
            self._save_memories()
            return True

        except Exception as e:
            self.logger.error(f"Failed to store memory: {str(e)}")
            return False

    def retrieve_memory(self, query: Dict, memory_type: MemoryType = None) -> List[MemoryItem]:
        """检索记忆"""
        try:
            results = []
            memories_to_search = []

            if memory_type == MemoryType.SHORT_TERM or memory_type is None:
                memories_to_search.extend(self.short_term_memory)
            if memory_type == MemoryType.LONG_TERM or memory_type is None:
                memories_to_search.extend(self.long_term_memory.values())
            if memory_type == MemoryType.WORKING or memory_type is None:
                memories_to_search.extend(self.working_memory)

            for memory in memories_to_search:
                if self._match_query(memory, query):
                    memory.access_count += 1
                    memory.last_access = datetime.datetime.now()
                    results.append(memory)

            self._save_memories()
            return results

        except Exception as e:
            self.logger.error(f"Failed to retrieve memory: {str(e)}")
            return []

    def _match_query(self, memory: MemoryItem, query: Dict) -> bool:
        """匹配查询条件"""
        for key, value in query.items():
            if key == 'tags' and not any(tag in memory.tags for tag in value):
                return False
            elif key == 'importance' and memory.importance < value:
                return False
            elif key == 'time_range':
                if not (value[0] <= memory.timestamp <= value[1]):
                    return False
        return True

    def consolidate_memories(self):
        """记忆巩固过程"""
        try:
            # 处理短期记忆到长期记忆的转换
            for memory in list(self.short_term_memory):
                if (memory.importance >= self.memory_config['consolidation_threshold'] or
                    memory.access_count > 5):
                    # 转移到长期记忆
                    self.long_term_memory[str(datetime.datetime.now())] = memory
                    self.short_term_memory.remove(memory)
                    self.logger.info("Memory consolidated to long-term storage")

            self._save_memories()

        except Exception as e:
            self.logger.error(f"Memory consolidation failed: {str(e)}")

    def forget_memories(self):
        """记忆遗忘过程"""
        try:
            current_time = datetime.datetime.now()
            
            # 处理长期记忆的遗忘
            for key, memory in list(self.long_term_memory.items()):
                time_diff = (current_time - memory.last_access).days
                forget_probability = self.memory_config['forgetting_rate'] * time_diff
                
                if (forget_probability > 0.9 and 
                    memory.importance < self.memory_config['importance_threshold']):
                    del self.long_term_memory[key]
                    self.logger.info(f"Forgot memory: {key}")

            self._save_memories()

        except Exception as e:
            self.logger.error(f"Memory forgetting process failed: {str(e)}")

    def associate_memories(self, memory_id1: str, memory_id2: str):
        """建立记忆之间的关联"""
        try:
            if memory_id1 in self.long_term_memory and memory_id2 in self.long_term_memory:
                memory1 = self.long_term_memory[memory_id1]
                memory2 = self.long_term_memory[memory_id2]
                
                if memory_id2 not in memory1.associations:
                    memory1.associations.append(memory_id2)
                if memory_id1 not in memory2.associations:
                    memory2.associations.append(memory_id1)
                
                self._save_memories()
                self.logger.info(f"Associated memories: {memory_id1} and {memory_id2}")
                return True
                
            return False

        except Exception as e:
            self.logger.error(f"Failed to associate memories: {str(e)}")
            return False

    def get_memory_stats(self) -> Dict:
        """获取记忆统计信息"""
        return {
            'short_term_count': len(self.short_term_memory),
            'long_term_count': len(self.long_term_memory),
            'working_memory_count': len(self.working_memory),
            'total_memories': (len(self.short_term_memory) + 
                             len(self.long_term_memory) + 
                             len(self.working_memory))
        }

    def _save_memories(self):
        """保存记忆到文件"""
        try:
            memory_data = {
                'short_term': list(self.short_term_memory),
                'long_term': self.long_term_memory,
                'working': list(self.working_memory)
            }
            
            with open('data/memories.pkl', 'wb') as f:
                pickle.dump(memory_data, f)
                
            self.logger.info("Memories saved successfully")

        except Exception as e:
            self.logger.error(f"Failed to save memories: {str(e)}")

    def _load_memories(self):
        """从文件加载记忆"""
        try:
            if os.path.exists('data/memories.pkl'):
                with open('data/memories.pkl', 'rb') as f:
                    memory_data = pickle.load(f)
                    
                self.short_term_memory = deque(memory_data['short_term'], maxlen=100)
                self.long_term_memory = memory_data['long_term']
                self.working_memory = deque(memory_data['working'], maxlen=10)
                
                self.logger.info("Memories loaded successfully")

        except Exception as e:
            self.logger.error(f"Failed to load memories: {str(e)}") 