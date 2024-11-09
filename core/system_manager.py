from typing import Dict, List, Optional
from models.memory.memory_core import MemoryCore
from models.nlu.language_manager import LanguageManager
from models.autonomous_learning.learning_core import AutonomousLearner
import logging

class SystemManager:
    def __init__(self):
        self.memory_core = MemoryCore()
        self.language_manager = LanguageManager()
        self.learning_core = AutonomousLearner()
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('system_manager')
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('logs/system.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
        
    def process_text(self, text: str, context: Optional[Dict] = None) -> Dict:
        """处理文本输入"""
        try:
            # 语言理解
            language_result = self.language_manager.process_input(text, context)
            
            # 记忆处理
            memory_result = self.memory_core.process_text(text)
            
            # 学习处理
            learning_result = self.learning_core.learn_from_interaction({
                'text': text,
                'language_result': language_result,
                'memory_result': memory_result
            })
            
            return {
                'language': language_result,
                'memory': memory_result,
                'learning': learning_result
            }
            
        except Exception as e:
            self.logger.error(f"Text processing failed: {str(e)}")
            raise
            
    def process_voice(self, audio_data: bytes, format: str, 
                     sample_rate: int) -> Dict:
        """处理语音输入"""
        try:
            # 实现语音处理逻辑
            pass
        except Exception as e:
            self.logger.error(f"Voice processing failed: {str(e)}")
            raise
            
    def query_memory(self, query: Dict) -> List[Dict]:
        """查询记忆"""
        try:
            return self.memory_core.retrieve_memory(query)
        except Exception as e:
            self.logger.error(f"Memory query failed: {str(e)}")
            raise
            
    def get_learning_status(self) -> Dict:
        """获取学习状态"""
        try:
            return self.learning_core.get_learning_status()
        except Exception as e:
            self.logger.error(f"Failed to get learning status: {str(e)}")
            raise 